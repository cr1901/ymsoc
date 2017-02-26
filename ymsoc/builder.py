import os
import struct

from misoc.integration.builder import *

# We need to override the default firmware/libraries. At some point the default
# firmware can perhaps be switched out.
class YMSoCBuilder(Builder):
    def __init__(self, soc, output_dir=None,
                 compile_software=True, compile_gateware=True,
                 gateware_toolchain_path=None,
                 csr_csv=None):
        Builder.__init__(self, soc, output_dir, compile_software,
            compile_gateware, gateware_toolchain_path, csr_csv)

        self.software_packages = []
        self.add_software_package("libbase")
        self.add_software_package("libcompiler-rt")
        self.add_software_package("libym2151",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "firmware",
            "libym2151")))
        self.add_software_package("ymselftest",
            os.path.abspath(os.path.join(os.path.dirname(__file__),
            "firmware", "ymselftest")))

    def _initialize_rom(self):
        bios_file = os.path.join(self.output_dir, "software", "ymselftest",
                                 "ymselftest.bin")
        if self.soc.integrated_rom_size:
            with open(bios_file, "rb") as boot_file:
                boot_data = []
                while True:
                    w = boot_file.read(4)
                    if not w:
                        break
                    boot_data.append(struct.unpack(">I", w)[0])
            self.soc.initialize_rom(boot_data)
