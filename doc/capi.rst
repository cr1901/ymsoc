Programmer's API
================

To Be Written

Interrupts
----------

YMSoC CPU has three implemented interrupts coming from two peripherals:

``YM2151_INTERRUPT``
    The YM2151/JT51 uses interrupt line 0, and can interrupt the CPU for two
    reasons, the line being shared between them. The first interrupt occurs when
    the YM2151's IRQ line goes low. The second interrupt occurs when the YM2151
    has just output a sample. The IRQ interrupt is level-triggered, while
    sample is edge-triggered.

    As of this writing, samples cannot be read by the sound CPU, thus only
    the IRQ interrupt is meaningful.

``HOST_INTERRUPT``
    An interrupt is sent to notify the sound CPU that a host (either over a bridge
    or a host CPU in an FPGA design) wants to send data. This interrupt is
    triggered when the Arbiter's control register bit ``DAT_AVAIL`` is toggled
    from zero to one. This interrupt uses line 1, and is edge-triggered. See
    ``HTOGGLE`` control bit for more details.

    TODO: The CPU can clear ``DAT_AVAIL`` as acknowledgment of data receipt
    my writing to the to-be-implement ``SND_ACK`` register.

A fourth interrupt source coming from a third peripheral is planned:

``DAC_INTERRUPT``
    The interface to the DAC will eventually be switchable between a direction
    connection to the YM2151 and a buffer/queue to which the sound CPU can send
    post-processed 16-bit samples. This interrupt, using line 2, will occur
    when the DAC queue needs samples.
