


Installation/Prerequisites
==========================

YMSoC requires ``python3`` to build, along with the libraries specified in
``requirements.txt``. To install::

    cd $YMSOC_ROOT && pip3 install -r requirements.txt

1. ``migen`` will abstract away FPGA toolchain differences, and generate Verilog.
    I prefer Migen to guard against mistakes I tend to make in Verilog, such
    as providing defaults for combinational-always and FSM creation.

2. ``misoc`` abstracts away creating the SoC, bus interface and peripherals. It
    also abstracts compiling software for a platform's SoC by providing headers,
    and Makefile environment variables.

3. ``pyserial`` is required for the provided UART driver to function.

In addition, Migen and MiSoC require an FPGA toolchain to be installed, preferably
on the default path. MiSoC additionally requires your usual host of POSIX utilities,
particularly ``m4`` and ``make``.

A GCC targeting LatticeMico32 (``lm32-elf-gcc``) must also be on your path to compile the firmware.

Since this is a sound chip application, JT51, an FPGA Yamaha FM synth implementation
also needs to be provided. JT51 can be downloaded `here`_.

.. _here: http://opencores.org/project,jt51


Building a SoC
==============

To Be Written. Unfortunately, the build process is in flux. If you have
all the prerequisites, try the following command::

    PYTHONPATH=$(YMSOC) python3 -m ymsoc --device xc6slx25 build --jt51-dir $(JT51) --output-dir $(YMSOC)/build --no-compile-gateware ymsoc.platforms.sim
