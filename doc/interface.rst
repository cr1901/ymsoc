Interfacing to External Designs
===============================

Although there is currently no way to generate a generic verilog output (I haven't
written code for it yet), the top level Arbiter contains a ``host_bus`` that
can be used to interface to either a larger FPGA design, or a serial or parallel
bus that connects to another computer system.

Bridges
-------

To make interfacing easy for the latter category, one can use FPGA bridges. I
provide a low-speed UART bridge for testing. In the future, I would like to provide
a USB bridge for streaming samples from the YM2151/JT51 to a host. A MIDI interface
would be a nice-to-have too.

UART
^^^^

The UART commands have the following format, where "Dn" is "byte n", written
little-endian order (LS bit first):

+-----+---------+---------+
| D00 | D01-D02 | D03-D06 |
+-----+---------+---------+
| CMD | ADDR    | DATA    |
+-----+---------+---------+

CMD
    Read or write to the sound CPU via the arbiter, based on the below format.

ADDR
    16-bit address to write into the bank or read, little endian format (LSB first).
    *This is despite the sound CPU being big endian.*

DATA
    If writing, 32-bit data to write into the bank, little endian format (LSB first).
    *This is despite the sound CPU being big endian.*

    If reading, data from the addressed memory location will be sent back in
    little endian format, and these four bytes are not required.

CMD Format
^^^^^^^^^^

+----+----+----+----+-----+-----+-----+----+
| D7 | D6 | D5 | D4 | D3  | D2  | D1  | D0 |
+----+----+----+----+-----+-----+-----+----+
| X  | X  | X  | X  | A19 | A18 | A17 | RW |
+----+----+----+----+-----+-----+-----+----+

A19
    Reserved for other banks.

A18-A17
    00- ROM bank

    01- Reserved (Arbiter RAM bank)

    10- DTA

    11- Arbiter Registers

RW
    0- Read

    1- Write

As shown above, the UART bridge can only write/read 32-bits at a time, and
can only transfer one word at a time. Changing less than a single word requires
reading the address in question and masking the appropriate bits. The bridge is
meant for simplicity of implementation on FPGA, rather than speed or software
convenience.
