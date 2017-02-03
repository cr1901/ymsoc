from migen import *

from misoc.integration.soc_core import *

from ymsoc.ymctl import CtlUnitYM2151
from ymsoc.arbiter import Arbiter
from ymsoc.ym2151 import *


class YMSoCCore(SoCCore):
    mem_map = {
        "ym2151": 0x30000000,
        "host": 0x50000000,
    }
    mem_map.update(SoCCore.mem_map)

    def __init__(self, platform, clk_freq, **kwargs):
        SoCCore.__init__(self, platform,
            clk_freq=clk_freq,
            # integrated_rom_size=0x8000,
            # integrated_main_ram_size=16*1024,
            with_uart=False,
            with_timer=False,
            **kwargs)

        # Sound chip core
        self.submodules.ym2151 = CtlUnitYM2151()
        self.add_wb_slave(mem_decoder(self.mem_map["ym2151"]), self.ym2151.bus)
        self.add_memory_region("ym2151", self.mem_map["ym2151"] | self.shadow_base, 0x1000)
        self.csr_devices += ["ym2151"] # CSR bus provides IRQ logic.
        self.interrupt_devices.append("ym2151")

        # Arbiter connections-
        # Add a second port separate from the wishbone bus for memories.
        self.submodules.host = Arbiter()
        port = self.rom.mem.get_port(write_capable=True, clock_domain="arb")
        self.comb += [self.host.rom_port.dat_r.eq(port.dat_r),
            port.dat_w.eq(self.host.rom_port.dat_w),
            port.we.eq(self.host.rom_port.wr),
            port.adr.eq(self.host.rom_port.adr)]
        self.specials += port

        # Audio connections
        audio = platform.request("audio")
        self.submodules.jt51_phy = JT51PHY(audio)
        self.comb += [self.ym2151.wb2151.jt51.out.connect(self.jt51_phy.inp)]

        # LED connections
        leds = [platform.request("user_led") for x in range(2)]
        self.comb += [leds[0].eq(self.ym2151.wb2151.jt51.out.ct1)]
        self.comb += [leds[1].eq(self.ym2151.wb2151.jt51.out.ct2)]

        # Hack: Avoid compile error for missing UART interrupt by forcing
        # definition to a bogus value.
        self._constants.append(("UART_INTERRUPT", 33))
