from migen import *
from migen.genlib.cdc import *
from misoc.interconnect import wishbone
from misoc.interconnect.csr import AutoCSR, CSRStatus, CSRStorage

jt51_bus = [
    ("cs_n", 1, DIR_M_TO_S),
    ("wr_n", 1, DIR_M_TO_S),
    ("a0", 1, DIR_M_TO_S),
    ("d_in", 8, DIR_M_TO_S),
    ("d_out", 8, DIR_S_TO_M),
    ("irq_n", 1, DIR_S_TO_M),
]

jt51_out = [
    ("ct1", 1, DIR_M_TO_S),
    ("ct2", 1, DIR_M_TO_S),
    ("p1", 1, DIR_M_TO_S),
    ("sample", 1, DIR_M_TO_S),
    ("dacleft", 16, DIR_M_TO_S),
    ("dacright", 16, DIR_M_TO_S),
]


class SampleQueue(Module):
    """L/R 16-bit sample input/output, for data capture purposes.

    This module provides two interrupts for when the input queue is nearly-full,
    and empty.
    """

    def __init__(self):
        raise NotImplementedError


class SysConJT51(Module, AutoCSR):
    """Programmable clock speed Wishbone SYSCON for JT51.

    In many SoC's it doesn't make sense to run the whole design
    at the same frequency as the YM2151/JT51. This module provides
    a clock domain crossing, as well as a clock and reset at the appropriate
    frequency for the JT51.

    This module assumes all responsibilities of Wishbone2JT51, and adds an
    additional I/O address for clock control on the CSR bus. Since clocking is
    platform-specific, these signals should be propogated back to the top-level
    in some manner.
    """

    def __init__(self):
        self.bus_in = wishbone.Interface()
        self.bus_out = wishbone.Interface()

        mcyc_prev = Signal(1)
        mcyc_negedge = Signal(1)
        cyc_qual = Signal(1)
        cyc_wait_count = Signal(4)

        mstb_prev = Signal(1)
        mstb_negedge = Signal(1)
        stb_qual = Signal(1)
        stb_wait_count = Signal(4)

        bus_in_full = Signal(32)
        bus_out_full = Signal(32)

        self.comb += [bus_in_full.eq(Cat(C(0, 2), self.bus_in.adr))]
        # self.comb += [self.bus_out.eq(bus_out_full[2:])]
        self.comb += [self.bus_out.adr.eq(bus_out_full[2:])]

        self.specials.wb_cdc = Instance("wb_async_reg",
            # M
            i_wbm_clk=ClockSignal("sys"), i_wbm_rst=ResetSignal("sys"),
            i_wbm_adr_i=bus_in_full, i_wbm_dat_i=self.bus_in.dat_w,
            o_wbm_dat_o=self.bus_in.dat_r, i_wbm_we_i=self.bus_in.we,
            i_wbm_sel_i=self.bus_in.sel, i_wbm_stb_i=stb_qual,
            o_wbm_ack_o=self.bus_in.ack, o_wbm_err_o=self.bus_in.err,
            i_wbm_cyc_i=cyc_qual,

            # S
            i_wbs_clk=ClockSignal("ym2151"), i_wbs_rst=ResetSignal("ym2151"),
            o_wbs_adr_o=bus_out_full, i_wbs_dat_i=self.bus_out.dat_r,
            o_wbs_dat_o=self.bus_out.dat_w, o_wbs_we_o=self.bus_out.we,
            o_wbs_sel_o=self.bus_out.sel, o_wbs_stb_o=self.bus_out.stb,
            i_wbs_ack_i=self.bus_out.ack, i_wbs_err_i=self.bus_out.err,
            o_wbs_cyc_o=self.bus_out.cyc
        )

        # It's possible for CYC/STB to reassert in one clock cycle in the source
        # domain. Force CYC/STB low to ensure its registered in dest to
        # reset the CDC handshake.
        self.comb += [cyc_qual.eq(self.bus_in.cyc & (cyc_wait_count == 0))]
        self.comb += [stb_qual.eq(self.bus_in.stb & (stb_wait_count == 0))]

        self.comb += [mcyc_negedge.eq(~self.bus_in.cyc & mcyc_prev)]
        self.comb += [mstb_negedge.eq(~self.bus_in.stb & mstb_prev)]
        self.sync += [
            mcyc_prev.eq(self.bus_in.cyc),
            mstb_prev.eq(self.bus_in.stb),

            If(cyc_wait_count != 0,
                cyc_wait_count.eq(cyc_wait_count - 1)),
            If(stb_wait_count != 0,
                stb_wait_count.eq(stb_wait_count - 1)),

            # Not going to happen, but in case we aren't done prev count,
            # restart it.
            If(mcyc_negedge,
                cyc_wait_count.eq(8)),
            If(mstb_negedge,
                stb_wait_count.eq(8)),
        ]


class Wishbone2YM2151(Module):
    def __init__(self):
        self.bus = wishbone.Interface()
        self.submodules.jt51 = JT51()

        ###

        bus_cyc = self.bus.stb & self.bus.cyc

        # IRQ connection goes to CPU.
        self.comb += [
            self.jt51.bus.d_in.eq(self.bus.dat_w[0:8]),
            # self.bus.dat_r.eq(self.jt51.bus.d_out),
            self.bus.dat_r.eq(Replicate(self.jt51.bus.d_out, 4)),
            self.jt51.bus.a0.eq(self.bus.adr[0]),
            self.jt51.bus.cs_n.eq(~bus_cyc),
            self.jt51.bus.wr_n.eq(~self.bus.we)
        ]

        self.sync.ym2151 += [
            self.bus.ack.eq(0),
            If(bus_cyc & ~self.bus.ack,
                self.bus.ack.eq(1)),
        ]


class JT51(Module):
    """Migen wrapper for JT51 Verilog core."""

    def __init__(self):
        self.bus = Record(jt51_bus)
        self.out = Record(jt51_out)

        self.specials.jt51 = Instance("jt51", i_clk=ClockSignal("ym2151"),
            i_rst=ResetSignal("ym2151"), i_cs_n=self.bus.cs_n,
            i_wr_n=self.bus.wr_n, i_a0=self.bus.a0, i_d_in=self.bus.d_in,
            o_d_out=self.bus.d_out, o_ct1=self.out.ct1, o_ct2=self.out.ct2,
            o_irq_n=self.bus.irq_n,
            o_p1=self.out.p1, o_sample=self.out.sample,
            o_dacleft=self.out.dacleft, o_dacright=self.out.dacright)

        # self.specials.dac_clk += Instance
        # self.clock_domains += ClockDomain("ym3012")


# TODO: Choice of sigma-delta DAC or raw.
class JT51PHY(Module):
    def __init__(self, pads):
        self.inp = Record(jt51_out)
        (dacl, dacr) = (DeltaSigma(), DeltaSigma())
        self.submodules += [dacl, dacr]

        ###

        self.comb += [dacl.data.eq(self.inp.dacleft),
            dacr.data.eq(self.inp.dacright),
            pads.a0.eq(dacl.out),
            pads.a1.eq(dacr.out)
        ]


# https://github.com/jordens/redpid/blob/master/gateware/delta_sigma.py#L8
class DeltaSigma(Module):
    def __init__(self, width=16):
        self.data = Signal(width)
        self.out = Signal()

        ###

        delta = Signal(width + 1)
        sigma = Signal(width + 1)
        self.comb += delta.eq(self.out << width)
        self.sync += sigma.eq(self.data - delta + sigma)
        self.comb += self.out.eq(sigma[-1])
