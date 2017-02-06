include ../include/generated/variables.mak
include $(MISOC_DIRECTORY)/software/common.mak

OBJECTS=main.o isr.o ym2151.o

all: fm-driver.bin

%.bin: %.elf
	$(OBJCOPY) -O binary $< $@
	chmod -x $@
	$(PYTHON) -m misoc.tools.mkmscimg $@

fm-driver.elf: $(FM-DRIVER_DIRECTORY)/linker.ld $(OBJECTS)

%.elf:
	$(LD) $(LDFLAGS) -T $< -N -o $@ \
		../libbase/crt0-$(CPU).o \
		$(OBJECTS) \
		-L../libbase \
		-L../libcompiler-rt \
		-lbase-nofloat -lcompiler-rt
	chmod -x $@
	lm32-elf-objdump -d fm-driver.elf > fm-driver.asm

main.o: $(FM-DRIVER_DIRECTORY)/main.c $(FM-DRIVER_DIRECTORY)/ym2151.h
	$(compile)

%.o: $(FM-DRIVER_DIRECTORY)/%.c
	$(compile)

%.o: $(FM-DRIVER_DIRECTORY)/%.S
	$(assemble)

$(FM-DRIVER_DIRECTORY)/ym2151.h: ym2151_const.h

ym2151_const.h: $(FM-DRIVER_DIRECTORY)/ym2151_const.m4
	m4 $< > $@

clean:
	$(RM) $(OBJECTS) fm-driver.elf fm-driver.bin .*~ *~

.PHONY: all clean main.o
