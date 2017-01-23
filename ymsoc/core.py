from migen import *

from misoc.integration.soc_core import *

from ymsoc.ymctl import CtlUnitYM2151


class YMSoCCore(SoCCore):
    mem_map = {
        "ym2151": 0x30000000,
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
        # self.submodules.crg = CRG(platform.request(platform.default_clk_name))

        self.submodules.ym2151 = CtlUnitYM2151()
        self.add_wb_slave(mem_decoder(self.mem_map["ym2151"]), self.ym2151.bus)
        self.add_memory_region("ym2151", self.mem_map["ym2151"] | self.shadow_base, 0x1000)
        self.csr_devices += ["ym2151"] # CSR bus provides IRQ logic.
        self.interrupt_devices.append("ym2151")
