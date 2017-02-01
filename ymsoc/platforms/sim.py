# import Fraction

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer
from migen.build.platforms import minispartan6
from migen.build.openocd import OpenOCD

from ymsoc.core import YMSoCCore

# This is a mock minispartan6 platform I use for simulation. It's the easiest
# way for me to create a stub for now.

class _CRG(Module):
    def __init__(self, platform, clk_freq):
        self.clock_domains.cd_ym2151 = ClockDomain()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

        clk = platform.request("clk32")

        # Power on Reset (vendor agnostic)
        int_rst = Signal(reset=1)
        self.sync.por += int_rst.eq(0)
        self.comb += [
            self.cd_sys.clk.eq(clk),
            self.cd_por.clk.eq(clk),
            self.cd_sys.rst.eq(int_rst)
        ]

        ym_clk = Signal(1)
        cnt = Signal(2)
        self.sync += [If(cnt == 3,
                        cnt.eq(0),
                        ym_clk.eq(~ym_clk)).
                    Else(
                        cnt.eq(cnt + 1)
                    )]

        self.comb += [self.cd_ym2151.clk.eq(ym_clk)]

        reset_cnt = Signal(4, reset=8)
        self.comb += [self.cd_ym2151.rst.eq(reset_cnt != 0)]
        self.sync += [
            If(reset_cnt != 0,
                reset_cnt.eq(reset_cnt - 1))]

        # self.comb += [self.cd_ym2151.clk.eq(clk)]
        # self.specials += AsyncResetSynchronizer(self.cd_ym2151, ResetSignal("sys"))


# Passing platform as an input argument is technically redundant since each
# platform gets its own source file. This is a design decision
# so that __main__.py can set platform-specific behavior before insantiating
# the core.
class YMSoC(YMSoCCore):
    def __init__(self, platform, **kwargs):
        clk_freq = 32*1000000
        YMSoCCore.__init__(self, platform, clk_freq, integrated_rom_size=0x4000,
            integrated_sram_size=4096,
            integrated_main_ram_size=0,
            **kwargs)
        self.submodules.crg = _CRG(platform, clk_freq)


# Extend w/ OpenOCD support.
class PlatformExtension(minispartan6.Platform):
    def __init__(self, **kwargs):
        minispartan6.Platform.__init__(self, **kwargs)

    def create_programmer(self):
        if self.programmer == "openocd":
            return OpenOCD("board/minispartan6.cfg")
        else:
            return minispartan6.Platform.create_programmer(self)

Platform = PlatformExtension
