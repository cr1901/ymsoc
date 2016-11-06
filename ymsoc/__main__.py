import os
import struct
import argparse
import importlib

from migen import *
from migen.genlib.io import CRG

from misoc.integration.soc_core import *
from misoc.integration.builder import *
from misoc.cores.gpio import GPIOOut


class YMSoC(SoCCore):
    def __init__(self, platform, **kwargs):
        SoCCore.__init__(self, platform,
            clk_freq=int((1/(platform.default_clk_period))*1000000000),
            integrated_rom_size=0x8000,
            integrated_main_ram_size=16*1024,
            with_uart=False,
            with_timer=False,
            **kwargs)
        self.submodules.crg = CRG(platform.request(platform.default_clk_name))
        self.csr_devices.append("leds")
        self.submodules.leds = GPIOOut(platform.request("user_led"))


class YMSoCBuilder(Builder):
    def __init__(self, soc, output_dir=None,
                 compile_software=True, compile_gateware=True,
                 gateware_toolchain_path=None,
                 csr_csv=None):
        Builder.__init__(self, soc, output_dir, compile_software,
            compile_gateware, gateware_toolchain_path, csr_csv)

    def _initialize_rom(self):
        bios_file = os.path.join(self.output_dir, "software", "fm-driver",
                                 "fm-driver.bin")
        if self.soc.integrated_rom_size:
            with open(bios_file, "rb") as boot_file:
                boot_data = []
                while True:
                    w = boot_file.read(4)
                    if not w:
                        break
                    boot_data.append(struct.unpack(">I", w)[0])
            self.soc.initialize_rom(boot_data)


def main():
    parser = argparse.ArgumentParser(description="JT51 SoC for Testing")
    subparsers = parser.add_subparsers(dest="cmd")

    pparser = subparsers.add_parser("program",
        help="Write bitstream and/or firmware to board.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    bparser = subparsers.add_parser("build", help="Build for Migen platform.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    pparser.add_argument("-f", help="Write bitstream to flash.",
        action="store_true")
    pparser.add_argument("--programmer", default=None,
                        help="Override FPGA programmer.")
    pparser.add_argument("--soc-dir", default=None, help="SoC directory root.")

    builder_args(bparser)
    soc_core_args(bparser)
    bparser.add_argument("--jt51-dir", default="./jt51",
                        help="Path to JT51 core directory")


    parser.add_argument("--device", default=None,
                        help="Override FPGA device name.")
    parser.add_argument("platform",
                        help="Module name of the Migen platform to build for.")
    args = parser.parse_args()

    platform_module = importlib.import_module(args.platform)
    if args.device:
        platform = platform_module.Platform(device=args.device)
    else:
        platform = platform_module.Platform()

    if args.cmd == "build":
        platform.add_source_dir(args.jt51_dir)

        soc = YMSoC(platform, **soc_core_argdict(args))

        builder = YMSoCBuilder(soc, **builder_argdict(args))
        builder.software_packages = []
        builder.add_software_package("libcompiler-rt")
        builder.add_software_package("libbase")
        builder.add_software_package("fm-driver", os.path.abspath(os.path.join(os.path.dirname("."), "firmware")))
        builder.build()
        # print(soc.get_csr_regions())
    else:
        prog = platform.create_programmer()
        if args.f:
            prog.flash(0, os.path.join(args.soc_dir, "gateware", "top.bin"))
        else:
            prog.load_bitstream(os.path.join(args.soc_dir, "gateware", "top.bit"))


if __name__ == "__main__":
    main()
