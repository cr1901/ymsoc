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


"""class ArbDecode(Module):
    def __init__(self):
        self.in_addr = Signal(18)
        self.out_addr = Signal(4)

        self.ym_rom = Signal(1)
        self.ym_ram = Signal(1)
        self.host_buffer = Signal(1)
        self.arb_ctl = Signal(1)

        self.comb += [self.ym_rom.eq(in_addr[17:19] == 0x00),
            self.ym_ram.eq(in_addr[17:19] == 0x01),
            self.host_buffer.eq(in_addr[17:19] == 0x10),
            self.arb_ctl.eq(in_addr[17:19] == 0x11),
        ]"""



class ArbReg(Module):
    def __init__(self):
        self.reg_bus = Record(mem_port)
        self.reg_ctl = Signal(32, reset=1) # Reset CPU (bit 0), notify data avail (bit 1).
        self.reg_size = Signal(16) # Payload size from host to sound CPU
        # data area.

        cases = {
            0x00 : [
                self.reg_bus.dat_r.eq(self.reg_ctl)
            ],

            0x01 : [
                self.reg_bus.dat_r.eq(self.reg_size)
            ]
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


"""class ArbSend(Module):
    def __init__(self):
        self.cpu_bus = wishbone.Interface()
        self.addr = Signal(16)
        self.count = Signal(16)
        self.start = Signal(1)
        self.next_req = Signal(1)
        self.
        self.done = Signal(1)

        self.submodules.fsm = fsm = FSM(reset_state="IDLE")

        fsm.act("IDLE",
            If(self.start,
                NextValue(count)
                NextState("SEND")
            )
        )

        fsm.act("SEND",
            self.cpu_bus
            self.cpu_bus.stb.eq(1),
            self.cpu_bus.cyc.eq(1),

            If(self.cpu_bus.ack == 1,
                If(self.count == 0,
                    NextState("IDLE"),
                    NextValue(self.done, 1)
                ).
                Else(
                    NextValue(self.count, self.count - 1),
                    NextState("WAIT")
                )
            )
        )"""


# Arbiter serves two roles:
# 1. Reset and load a program into CPU address space
# 2. Provide data path for host to send/recv data.
class Arbiter(Module, AutoCSR):
    def __init__(self):
        self.host_bus = Record(arb_bus)
        self.rom_port = Record(mem_port)
        # CSR bus will be provided automatically.

        self.submodules.regs = ArbReg()
        self.cpu_reset = Signal()

        cases = {
            0x00: [
                self.host_bus.connect(self.rom_port, leave_out={"ack", "avail"})
            ],

            0x03 : [
                self.host_bus.connect(self.regs.reg_bus, leave_out={"ack", "avail"})
            ],
        }

        self.comb += [Case(self.host_bus.adr[16:], cases)]
        self.comb += [self.cpu_reset.eq(self.regs.reg_ctl[0])]


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
    # ios.extend([io[0] for io in m.rom_port.iter_flat()])
    ios.extend([m.cpu_reset])

    mem = Memory(32, 64)
    port = mem.get_port(write_capable=True, clock_domain="arb")
    m.specials += mem, port

    m.comb += [m.rom_port.dat_r.eq(port.dat_r),
        port.dat_w.eq(m.rom_port.dat_w),
        port.we.eq(m.rom_port.wr),
        port.adr.eq(m.rom_port.adr)]

    # convert(m, ios=set(ios)).write("arbiter.v")
