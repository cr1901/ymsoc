from migen import *
from migen.fhdl.verilog import convert

from misoc.interconnect import wishbone
from misoc.interconnect.csr import *
from misoc.interconnect.csr_eventmanager import *

arb_bus = [
    ("dat_w", 32, DIR_M_TO_S),
    ("dat_r", 32, DIR_S_TO_M),
    ("adr", 18, DIR_M_TO_S),
    ("wr", 1, DIR_M_TO_S),
    ("ack", 1, DIR_S_TO_M), # WB ack analogue
    ("avail", 1, DIR_S_TO_M) # Sound CPU wants to send data.
]

# _MemoryPort isn't exported in Migen.
mem_port = [
    ("adr", 16, DIR_M_TO_S),
    ("wr", 1, DIR_M_TO_S),
    ("dat_w", 32, DIR_M_TO_S),
    ("dat_r", 32, DIR_S_TO_M)
]


class ArbReg(Module):
    def __init__(self):
        self.reg_bus = Record(mem_port)
        self.reg_ctl = Signal(32, reset=1) # Reset CPU (bit 0), notify data avail (bit 1).
        self.reg_size = Signal(16) # Payload size from host to sound CPU
        self.reg_snd_ctl = Signal(8)
        self.reg_snd_size = Signal(16)

        self.host_ack = Signal(1) # Write to this reg to ack data-avail
        # from sound CPU data area. Clears DAT_AVAIL of snd_ctl.
        self.snd_ack = Signal(1) # Signal that tells reg file to clear
        # DAT_AVAIL of host. If there's a tie (i.e. sound CPU and host are
        # both writing at the same time), host wins.

        cases = {
            0x00 : [
                self.reg_bus.dat_r.eq(self.reg_ctl)
            ],

            0x01 : [
                self.reg_bus.dat_r.eq(self.reg_size)
            ],

            0x02 : [
                self.reg_bus.dat_r.eq(self.reg_snd_ctl)
            ],

            0x03 : [
                self.reg_bus.dat_r.eq(self.reg_snd_size)
            ],
        }

        self.comb += [
            Case(self.reg_bus.adr[0:2], cases)
        ]

        self.sync.arb += [
            If(self.reg_bus.wr,
                If(self.reg_bus.adr[0:2] == 0x00,
                    self.reg_ctl.eq(self.reg_bus.dat_w)
                ).
                Elif(self.reg_bus.adr[0:2] == 0x01,
                    self.reg_size.eq(self.reg_bus.dat_w)
                )
            )
        ]


# Arbiter serves two roles:
# 1. Reset and load a program into CPU address space
# 2. Provide data path for host to send/recv data.
class Arbiter(Module, AutoCSR):
    def __init__(self):
        self.host_bus = Record(arb_bus)
        self.rom_port = Record(mem_port)
        self.xfer_port = Record(mem_port)
        # CSR bus will be provided automatically.

        self.submodules.regs = ArbReg()

        self.host_ctl = CSRStatus(32)
        self.host_size = CSRStatus(16)
        # Send data back to host. Perhaps attach directly to avail
        # signal and have arbiter bridges block until toggle?
        self.snd_ctl = CSRStorage(8)
        self.snd_size = CSRStorage(16)
        # self.snd_ack = CSR(1) # Write-through

        self.submodules.ev = EventManager()
        # EventSourcePulse should also probably work?
        self.ev.data_avail = EventSourceProcess()
        self.ev.finalize()

        self.cpu_reset = Signal()

        # Reg file from host perspective
        cases = {
            0x00: [
                self.host_bus.connect(self.rom_port, leave_out={"ack", "avail"})
            ],

            0x02: [
                self.host_bus.connect(self.xfer_port, leave_out={"ack", "avail"})
            ],

            0x03 : [
                self.host_bus.connect(self.regs.reg_bus, leave_out={"ack", "avail"})
            ],
        }

        # Bank buses
        self.comb += [Case(self.host_bus.adr[16:], cases)]

        # Control connections to/from arbiter.
        self.comb += [self.cpu_reset.eq(self.regs.reg_ctl[0]),
            self.ev.data_avail.trigger.eq(~self.regs.reg_ctl[1]),
            self.host_bus.avail.eq(self.snd_ctl.storage[1])]

        # Reg file from sound CPU perspective.
        self.comb += [self.host_ctl.status.eq(self.regs.reg_ctl),
            self.host_size.status.eq(self.regs.reg_size)]

        # Sound CPU reg file from host perspective.
        self.comb += [self.regs.reg_snd_ctl.eq(self.snd_ctl.storage),
            self.regs.reg_snd_size.eq(self.snd_size.storage)]


def write_port(bus, adr, dat):
    yield bus.adr.eq(adr)
    yield bus.dat_w.eq(dat)
    yield bus.wr.eq(1)
    yield
    yield bus.wr.eq(0)

def read_port(bus, adr):
    yield bus.adr.eq(adr)
    yield bus.wr.eq(0)
    yield
    return (yield bus.dat_r)


if __name__ == "__main__":
    m = Arbiter()
    ios = [io[0] for io in m.host_bus.iter_flat()]
    ios.extend([io[0] for io in m.rom_port.iter_flat()])
    ios.extend([m.cpu_reset])
    convert(m, ios=set(ios)).write("arbiter.v")
