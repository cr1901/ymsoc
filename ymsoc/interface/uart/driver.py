import sys
import serial
import struct
import contextlib

(ROM, RAM, SHARED, CTL) = (0x00 << 1, 0x01 << 1, 0x02 << 1, 0x03 << 1)


class Context:
    def __init__(self, device, baud_rate=115200):
        self.device = device
        self.baud_rate = baud_rate

    def __enter__(self):
        self.drv = Driver(self.device, self.baud_rate)
        return self.drv

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.drv.handle.close()


class Driver:
    # Somewhere along the line I screwed up and despite LM32 being BE,
    # input data to UART needs to be LE...
    def __init__(self, device, baud_rate=19200):
        self.handle = serial.Serial(device, baud_rate)
        self.write_bytes = struct.Struct("<BHL")
        self.read_bytes = struct.Struct("<BH")
        self.read_data = struct.Struct("<L")

    def write_word(self, cmd, addr, data):
        # print(self.write_bytes.pack(cmd | 0x01, addr, data))
        self.handle.write(self.write_bytes.pack(cmd | 0x01, addr, data))

    def read_word(self, cmd, addr):
        self.handle.write(self.read_bytes.pack(cmd & 0xFE, addr))
        return self.read_data.unpack(self.handle.read(4))[0]

    # Takes array of unsigned ints, 32 bit.
    def write_rom(self, data, start, end):
        i = 0
        for offs in range(start, end):
            self.write_word(ROM, offs, data[i])
            i = i + 1

    def read_rom(self, start, end):
        data = []
        for offs in range(start, end):
            data.append(self.read_word(ROM, offs))
        return data

    def cpu_reset_on(self):
        self.write_word(CTL, 0, 1)

    def cpu_reset_off(self):
        self.write_word(CTL, 0, 0)
