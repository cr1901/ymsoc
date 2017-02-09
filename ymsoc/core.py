from migen import *

from misoc.integration.soc_core import *
from misoc.interconnect.wishbone import SRAM

from ymsoc.ymctl import CtlUnitYM2151
from ymsoc.arbiter import Arbiter
from ymsoc.ym2151 import *


class YMSoCCore(SoCCore):
    mem_map = {
        "ym2151": 0x30000000,
        "xfer": 0x50000000,
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

        # Sound chip core- has to be a Wishbone device b/c of wait states.
        self.submodules.ym2151 = CtlUnitYM2151()
        self.add_wb_slave(mem_decoder(self.mem_map["ym2151"]), self.ym2151.bus)
        self.add_memory_region("ym2151", self.mem_map["ym2151"] | self.shadow_base, 0x1000)
        self.csr_devices += ["ym2151"] # CSR bus provides IRQ logic.
        self.interrupt_devices.append("ym2151")

        # Create a memory location for xfer data area.
        xfer_mem = Memory(32, 512)
        self.submodules.xfer = SRAM(xfer_mem) # Granularity 8 bits
        self.add_wb_slave(mem_decoder(self.mem_map["xfer"]), self.xfer.bus)
        # TODO: | self.shadow_base? Or rely on cache flush?
        self.add_memory_region("xfer", self.mem_map["xfer"] | self.shadow_base, 0x200)

        # Arbiter connections-
        # Add a second port separate from the wishbone bus for memories.
        self.submodules.host = Arbiter()
        # ROM port already provided by SoCCore.
        rom_port = self.rom.mem.get_port(write_capable=True, clock_domain="arb")
        self.comb += [self.host.rom_port.dat_r.eq(rom_port.dat_r),
            rom_port.dat_w.eq(self.host.rom_port.dat_w),
            rom_port.we.eq(self.host.rom_port.wr),
            rom_port.adr.eq(self.host.rom_port.adr)]
        self.specials += rom_port
        # RAM port not provided.
        # Data Xfer Area memory was created previously- granularity 32 bits.
        xfer_port = self.xfer.mem.get_port(write_capable=True, clock_domain="arb")
        self.comb += [self.host.xfer_port.dat_r.eq(xfer_port.dat_r),
            xfer_port.dat_w.eq(self.host.xfer_port.dat_w),
            xfer_port.we.eq(self.host.xfer_port.wr),
            xfer_port.adr.eq(self.host.xfer_port.adr)]
        self.specials += xfer_port
        self.csr_devices += ["host"]
        self.interrupt_devices.append("host")

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
