# import Fraction

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer
from migen.build.platforms import minispartan6
from migen.build.openocd import OpenOCD

from ymsoc.core import YMSoCCore

class _CRG(Module):
    def __init__(self, platform, clk_freq):
        self.clock_domains.cd_ym2151 = ClockDomain()
        self.clock_domains.cd_sys = ClockDomain()

        clk_in = platform.request("clk32")
        clk_bufio2_in = Signal()
        clk_dcm_in = Signal()
        clk_sys_bufg_in = Signal() # BUFG *should be inferred?*
        clk_ym2151_bufg_in = Signal()

        dcm = Signal(5) # Required, but ignored signals.
        dcm_locked = Signal(1)

        # Do the clk dance
        self.specials += Instance("IBUFG", i_I=clk_in, o_O=clk_bufio2_in)
        self.specials += Instance("BUFIO2", p_DIVIDE=1,
                                  p_DIVIDE_BYPASS="TRUE", p_I_INVERT="FALSE",
                                  i_I=clk_bufio2_in, o_DIVCLK=clk_dcm_in)
        self.specials += Instance("DCM_SP", p_CLKIN_PERIOD=1000000000/clk_freq,
            p_CLK_FEEDBACK="1X", p_CLKDV_DIVIDE=8, i_CLKIN=clk_dcm_in, i_RST=0,
            # i_CLKFB=clk_sys_bufg_in
            i_CLKFB=ClockSignal("sys"),  # Would BUFGs be inferred if I
            # directly drove clocks from DCM?
            o_CLK0=clk_sys_bufg_in, o_CLK90=dcm[0], o_CLK180=dcm[1],
            o_CLK270=dcm[2], o_CLK2X=dcm[3], o_CLK2X180=dcm[4],
            o_CLKDV=clk_ym2151_bufg_in,
            # o_STATUS skipped- not needed.
            o_LOCKED=dcm_locked)
        self.specials += Instance("BUFG", name="sys_bufg", i_I=clk_sys_bufg_in,
            o_O=self.cd_sys.clk)
        self.specials += Instance("BUFG", name="ym2151_bufg",
            i_I=clk_ym2151_bufg_in, o_O=self.cd_ym2151.clk)

        # Required in general case, but not here.
        self.specials += AsyncResetSynchronizer(self.cd_sys, dcm_locked)
        self.specials += AsyncResetSynchronizer(self.cd_ym2151, ResetSignal("sys"))


# Passing platform as an input argument is technically redundant since each
# platform gets its own source file. This is a design decision
# so that __main__.py can set platform-specific behavior before insantiating
# the core.
class YMSoC(YMSoCCore):
    def __init__(self, platform, **kwargs):
        clk_freq = 32*1000000
        YMSoCCore.__init__(self, platform, clk_freq, integrated_rom_size=0x8000,
            integrated_sram_size=0x8000, integrated_main_ram_size=0, **kwargs)
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
