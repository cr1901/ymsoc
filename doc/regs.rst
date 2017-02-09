Register Descriptions
=====================

CSR
---

As described previously, the CSR bus is accessed using 8-bit granularity, on
32-bit word boundaries. I *highly* recommend using the ``_read/_write`` functions
in ``<generated/csr.h>`` to access CSR registers.

TMPU
^^^^

The TMPU is included by default in MiSoC, but is unused in this design. Consult
MiSoC documentation for usage.


YM2151 Event Status
^^^^^^^^^^^^^^^^^^^

+---+---+---+---+---+---+---+--------+
|D07|D06|D05|D04|D03|D02|D01|D00     |
+---+---+---+---+---+---+---+--------+
|X  |X  |X  |X  |X  |X  |0  |IRQ     |
+---+---+---+---+---+---+---+--------+

D01, SAMPLE (R)
    Always zero due to how ``csr_eventmanager`` handles pulsed interrupts.

IRQ (R)
    Logic level of the YM2151/JT51 IRQ signal.


YM2151 Event Pending
^^^^^^^^^^^^^^^^^^^^

+---+---+---+---+---+---+-------+--------+
|D07|D06|D05|D04|D03|D02|D01    |D00     |
+---+---+---+---+---+---+-------+--------+
|X  |X  |X  |X  |X  |X  |SPEND  |IRQPEND |
+---+---+---+---+---+---+-------+--------+

SPEND
    R- If 1, a sample from the YM2151/JT51 is ready.

    W- Acknowledge/clear pending.

IRQPEND
    R- If 1, the YM2151 IRQ line has gone low since last clear.

    W- Acknowledge/clear pending.


YM2151 Event Enable
^^^^^^^^^^^^^^^^^^^^

+---+---+---+---+---+---+-------+--------+
|D07|D06|D05|D04|D03|D02|D01    |D00     |
+---+---+---+---+---+---+-------+--------+
|X  |X  |X  |X  |X  |X  |SEN    |IRQEN   |
+---+---+---+---+---+---+-------+--------+

SEN
    0- Disable Sample Interrupt

    1- Enable Sample Interrupt

IRQEN
    0- Disable IRQ Interrupt

    1- Enable IRQ Interrupt


Host Control
^^^^^^^^^^^^

This is a read-only mirror of the Arbiter Control register. The CPU can use
this information to control flow purposes.


Host Incoming Transfer Size
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a read-only mirror of the Arbiter Size register. The CPU uses this to
coordinate data transfers from the host.


Host Event Status
^^^^^^^^^^^^^^^^^^^

+---+---+---+---+---+---+---+--------+
|D07|D06|D05|D04|D03|D02|D01|D00     |
+---+---+---+---+---+---+---+--------+
|X  |X  |X  |X  |X  |X  |X  |HTOGGLE |
+---+---+---+---+---+---+---+--------+

HTOGGLE
    Inverse of DAT_AVAIL bit in Arbiter Control.


Host Event Pending
^^^^^^^^^^^^^^^^^^^^

+---+---+---+---+---+---+---+--------+
|D07|D06|D05|D04|D03|D02|D01|D00     |
+---+---+---+---+---+---+---+--------+
|X  |X  |X  |X  |X  |X  |X  |HPEND   |
+---+---+---+---+---+---+---+--------+

HPEND
    R- If 1, a leading edge transition (0=>1) has been detected on DAT_AVAIL.

    W- Acknowledge/clear pending.


Host Event Enable
^^^^^^^^^^^^^^^^^^^^

+---+---+---+---+---+---+---+--------+
|D07|D06|D05|D04|D03|D02|D01|D00     |
+---+---+---+---+---+---+---+--------+
|X  |X  |X  |X  |X  |X  |X  |HEN     |
+---+---+---+---+---+---+---+--------+

HEN
    0- Disable Host Interrupt

    1- Enable Host Interrupt


Arbiter
-------

Control
^^^^^^^

Offset 0x0000 in bank 0x00.

+---+---+---+---+---+---+----------+--------+
|D31|D30|D29|D28|D27|D26|D25       |D24     |
+---+---+---+---+---+---+----------+--------+
|X  |X  |X  |X  |X  |X  |X         |X       |
+---+---+---+---+---+---+----------+--------+
|D23|D22|D21|D20|D19|D18|D17       |D16     |
+---+---+---+---+---+---+----------+--------+
|X  |X  |X  |X  |X  |X  |X         |X       |
+---+---+---+---+---+---+----------+--------+
|D15|D14|D13|D12|D11|D10|D09       |D08     |
+---+---+---+---+---+---+----------+--------+
|X  |X  |X  |X  |X  |X  |X         |X       |
+---+---+---+---+---+---+----------+--------+
|D07|D06|D05|D04|D03|D02|D01       |D00     |
+---+---+---+---+---+---+----------+--------+
|X  |X  |X  |X  |X  |X  |DAT_AVAIL |CPU_RST |
+---+---+---+---+---+---+----------+--------+

DAT_AVAIL (R/W)
    0- Host has not written to DTA.

    1- Host had written data to DTA, trigger host interrupt.

CPU_RST (R/W)
    0- Sound CPU is running

    1- Sound CPU is held in reset.


Size
^^^^^^^

Offset 0x0001 in bank 0x00

+---+---+---+---+---+---+---+---+
|D31|D30|D29|D28|D27|D26|D25|D24|
+---+---+---+---+---+---+---+---+
|X  |X  |X  |X  |X  |X  |X  |X  |
+---+---+---+---+---+---+---+---+
|D23|D22|D21|D20|D19|D18|D17|D16|
+---+---+---+---+---+---+---+---+
|X  |X  |X  |X  |X  |X  |X  |X  |
+---+---+---+---+---+---+---+---+
|D15|D14|D13|D12|D11|D10|D09|D08|
+---+---+---+---+---+---+---+---+
|S15|S14|S13|S12|S11|S10|S09|S08|
+---+---+---+---+---+---+---+---+
|D07|D06|D05|D04|D03|D02|D01|D00|
+---+---+---+---+---+---+---+---+
|S07|S06|S05|S04|S03|S02|S01|S00|
+---+---+---+---+---+---+---+---+

S0-15
    Size of the transferred data. For use by sound CPU.
