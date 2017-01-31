from migen import *
from migen.genlib.cdc import *
from migen.genlib.fifo import SyncFIFO
from migen.fhdl.verilog import convert

from misoc.interconnect import wishbone
from misoc.interconnect.csr import *
from misoc.interconnect.csr_eventmanager import *

from ymsoc.ym2151 import *


"""class WishboneSyncFIFO(Module, AutoCSR):
    def __init__(self, width, depth):
        self.bus = wishbone.bus()
        self.fifo = SyncFIFO(width, depth)"""


class CtlUnitYM2151(Module, AutoCSR):
    """Top-level wishbone bus for YM2151 and associated peripherals.

    This wishbone device concatenates all YM2151-related wishbone devices
    into a single shared bus for convenience.

    This device is exposed to both the wishbone bus and CSR buses. Memory I/O
    buffers for the device and timing sensitive I/O registers (YM2151)
    appear on the wishbone bus.

    TODO: Depending on the setting of "use_ct", the use
    of the CSR bus can be eliminated by using the YM2151's CT outputs
    as 1-bit registers.

    Wishbone Addr Map (Upper Addr Bits are expected to be provided by external
    decoding logic):
    000-007: YM2151 I/O registers (2, 1 registers byte each). Mirrored to 3FF.
    008: Output FIFO (16 bit/word x 512 words)
    00C: Input FIFO (16 bit/word x 512 words)
    Alternate:
    400-7FF: Output buffer (16 bit/word x 512 words)
    800-FFF: Input buffer (16 bit/word x 512 words, to DAC output if enabled)
    """

    def __init__(self):
        self.bus = wishbone.Interface()
        self.submodules.syscon2151 = SysConJT51()
        self.submodules.wb2151 = Wishbone2YM2151()

        # self.submodules.ym_out = wishbone.SRAM(512*2, read_only=True)
        # self.submodules.dac_in = wishbone.SRAM(512*2)

        self.submodules += wishbone.InterconnectPointToPoint(self.bus, self.syscon2151.bus_in)
        self.submodules += wishbone.InterconnectPointToPoint(self.syscon2151.bus_out, self.wb2151.bus)

        self.submodules.ev = EventManager()
        self.ev.time_up = EventSourceLevel()
        self.ev.sample_ready = EventSourcePulse()
        self.ev.finalize()

        irq_n = Signal() # Bring irq_n to sys domain.
        sample = Signal() # Ditto with the sample signal.
        self.specials += MultiReg(self.wb2151.jt51.bus.irq_n, irq_n)
        self.specials += MultiReg(self.wb2151.jt51.out.sample, sample)
        self.comb += [self.ev.time_up.trigger.eq(irq_n == 0)]
        self.comb += [self.ev.sample_ready.trigger.eq(sample)]

        # sel_exprs = [(lambda a : a[10:12] == 0, self.syscon2151.bus_in),
        #              (lambda a : a[10] == 1, self.ym_out.bus),
        #              (lambda a : a[11] == 1, self.dac_in.bus)]
        # self.submodules += wishbone.InterconnectShared([self.bus], sel_exprs)

if __name__ == "__main__":
    m = CtlUnitYM2151()
    ios = [io[0] for io in m.bus.iter_flat()]
    ios.extend([io[0] for io in m.wb2151.jt51.out.iter_flat()])
    ios.extend([m.ev.irq])
    # print(ios)

    convert(m, ios=set(ios)).write("ymctl.v")
