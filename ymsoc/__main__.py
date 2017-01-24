import os
import struct
import argparse
import importlib

from misoc.integration.builder import *
from misoc.integration.soc_core import *
from ymsoc.builder import YMSoCBuilder


jt51_sources = [
    "jt51.v",
    "jt51_envelope.v",
    "jt51_exptable.v",
    "jt51_lfo_lfsr.v",
    "jt51_mmr.v",
    "jt51_noise_lfsr.v",
    "jt51_phasegen.v",
    "jt51_pm.v",
    "jt51_sh.v",
    "jt51_sintable.v",
    "jt51_timers.v",
    "jt51_acc.v",
    "jt51_exp2lin.v",
    "jt51_lfo.v",
    "jt51_lin2exp.v",
    "jt51_noise.v",
    "jt51_op.v",
    "jt51_phinc_rom.v",
    "jt51_reg.v",
    "jt51_sh2.v",
    "jt51_sum_op.v"
]

def main():
    parser = argparse.ArgumentParser(description="JT51 SoC for Testing")
    parser.add_argument("--device", default=None,
                        help="Override FPGA device name.")
    # parser.add_argument("--programmer", default=None,
    #                    help="Override FPGA programmer.")
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
    bparser.add_argument("platform",
                        help="Module name of the Migen platform to build for. Must exist under ymsoc.platforms.")

    args = parser.parse_args()

    platform_module = importlib.import_module(args.platform)
    if args.device:
        platform = platform_module.Platform(device=args.device)
    else:
        platform = platform_module.Platform()

    if args.cmd == "build":
        platform.add_sources(args.jt51_dir, *jt51_sources)
        # platform.add_verilog_include_path(args.jt51_dir)
        platform.add_source(os.path.abspath(os.path.join(os.path.dirname(__file__), "extern", "wb_async_reg.v")))
        soc = platform_module.YMSoC(platform, **soc_core_argdict(args))
        builder = YMSoCBuilder(soc, **builder_argdict(args))
        builder.build()
        # print(soc.get_csr_regions())
    else:
        prog = platform.create_programmer("openocd")
        if args.f:
            prog.flash(0, os.path.join(args.soc_dir, "gateware", "top.bin"))
        else:
            prog.load_bitstream(os.path.join(args.soc_dir, "gateware", "top.bit"))


if __name__ == "__main__":
    main()
