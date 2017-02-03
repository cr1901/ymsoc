import argparse
import serial
import struct
import sys
from ymsoc.interface.uart.driver import Context

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Firmware loader for YMSoC using UART bridge.")
    parser.add_argument("-b", default=115200, help="Baud rate.")
    parser.add_argument("-v", action="store_true", help="Verify after writing.")
    parser.add_argument("device", help="Serial device to use.")
    parser.add_argument("filename", help="Firmware file to write (.bin from objdump).")

    args = parser.parse_args()

    dat = []
    with open(args.filename, "rb") as fp:
        byte_dat = fp.read()
        for i in range(len(byte_dat)//4):
            dat.append(struct.unpack('>L', byte_dat[4*i:4*(i + 1)])[0])
    firm_size = len(dat)

    # FIXME: Right now, we don't have a mechanism to get memory size of FPGA SoC.
    with Context(args.device, args.b) as ctx:
        ctx.cpu_reset_on()
        ctx.write_rom(dat, 0, firm_size)

        if args.v:
            read_back_dat = ctx.read_rom(0, firm_size)
            if read_back_dat != dat:
                print("ERROR: Read-back data doesn't match written!")
                # print("ERROR: Read-back data doesn't match written at word offset {0:0X} (byte offset {0:0X})".format(i, i >> 2))
                exit(1)

        ctx.cpu_reset_off()
