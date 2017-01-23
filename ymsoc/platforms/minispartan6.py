# import Fraction

from migen import *
from migen.build.platforms import minispartan6
from migen.build.openocd import OpenOCD

from ymsoc.core import YMSoCCore

class _CRG(Module):
    def __init__(self, platform, clk_freq):
        pass


# Passing platform as an input argument is technically redundant. This is a design decision
# so that __main__.py can set platform-specific behavior before insantiating
# the core.
class YMSoC(YMSoCCore):
    def __init__(self, platform, **kwargs):
        clk_freq = 32*1000000
        YMSoCCore.__init__(self, platform, clk_freq, integrated_rom_size=0x8000, **kwargs)

        self.submodules.crg = _CRG(platform, clk_freq)
        self.clock_domains.cd_ym2151 = ClockDomain()
        self.clock_domains.cd_sys = ClockDomain()


# Extend w/ OpenOCD support.
class PlatformExtension(minispartan6.Platform):
    def __init__(self, **kwargs):
        minispartan6.Platform.__init__(self, **kwargs)

    def create_programmer(self):
        if self.programmer == "openocd":
            return OpenOCD("board/minispartan6.cfg")
        else:
            minispartan6.Platform.create_programmer(self)

Platform = PlatformExtension
