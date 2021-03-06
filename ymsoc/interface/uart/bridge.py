from migen import *
from migen.fhdl.verilog import convert

from ymsoc.arbiter import *
from ymsoc.interface.uart.uart import Core # FIXME: Redundant namespace


# Extremely naive Host-to-sound-CPU interface that favors simplicity over
# performance.
# Command: xxxxxaar: X don't care, A: 00- ROM, 01- RAM, 10- Shared Data, 11- Arb Regs, R: 0- Read, 1- Write
# Address: 16-bit address, top two bits chosen by Command
# Data: 32-bit data.
class UARTBridge(Module):
    def __init__(self, clk_freq, baud_rate=115200):
        self.submodules.uart = ClockDomainsRenamer({"sys" : "arb"})(Core(clk_freq, baud_rate))
        self.bus = Record(arb_bus)
        self.submodules.fsm = fsm = ClockDomainsRenamer({"sys" : "arb"})(FSM("WAIT_CMD"))

        self.command = Signal(8)
        self.addr = Signal(16)
        self.data = Signal(32)

        addr_word = Signal(max=2)
        data_word = Signal(max=4)
        read = Signal(1)
        addr_space = Signal(2)

        self.comb += [read.eq(~self.command[0])]
        self.comb += [addr_space.eq(self.command[1:3])]

        fsm.act("WAIT_CMD",
            If(~self.uart.rx_empty,
                NextState("WAIT_ADDR"),
                NextValue(self.command, self.uart.in_data),
                self.uart.rd.eq(1)
            )
        )

        fsm.act("WAIT_ADDR",
            If(~self.uart.rx_empty,
                self.uart.rd.eq(1),
                If(addr_word == 1,
                    NextValue(self.addr[8:], self.uart.in_data),
                    NextValue(addr_word, 0),
                    If(read,
                        # Preemptively start read.
                        self.bus.wr.eq(0),
                        self.bus.adr.eq(Cat(self.addr, addr_space)),
                        NextState("DO_READ")
                    ).
                    Else(NextState("WAIT_DATA"))
                ).
                Else(
                    NextValue(self.addr[0:8], self.uart.in_data),
                    NextValue(addr_word, addr_word + 1)
                )
            )
        )

        fsm.act("WAIT_DATA",
            If(~self.uart.rx_empty,
                self.uart.rd.eq(1),
                If(data_word == 3,
                    NextValue(self.data[24:], self.uart.in_data),
                    NextValue(data_word, 0),
                    NextState("DO_WRITE")
                ).
                Elif(data_word == 2,
                    NextValue(self.data[16:24], self.uart.in_data),
                    NextValue(data_word, data_word + 1)
                ).
                Elif(data_word == 1,
                    NextValue(self.data[8:16], self.uart.in_data),
                    NextValue(data_word, data_word + 1)
                ).
                Else(
                    NextValue(self.data[0:8], self.uart.in_data),
                    NextValue(data_word, data_word + 1)
                )
            )
        )

        fsm.act("DO_WRITE",
            self.bus.wr.eq(1),
            self.bus.adr.eq(Cat(self.addr, addr_space)),
            self.bus.dat_w.eq(self.data),
            NextState("WAIT_CMD")
        )

        fsm.act("DO_READ",
            self.bus.wr.eq(0),
            self.bus.adr.eq(Cat(self.addr, addr_space)),

            If(self.uart.tx_empty,
                self.uart.wr.eq(1),
                If(data_word == 3,
                    self.uart.out_data.eq(self.bus.dat_r[24:]),
                    NextValue(data_word, 0),
                    NextState("WAIT_CMD")
                ).
                Elif(data_word == 2,
                    self.uart.out_data.eq(self.bus.dat_r[16:24]),
                    NextValue(data_word, data_word + 1)
                ).
                Elif(data_word == 1,
                    self.uart.out_data.eq(self.bus.dat_r[8:16]),
                    NextValue(data_word, data_word + 1)
                ).
                Else(
                    self.uart.out_data.eq(self.bus.dat_r[0:8]),
                    NextValue(data_word, data_word + 1)
                )
            )
        )
