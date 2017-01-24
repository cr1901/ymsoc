include ../include/generated/variables.mak
include $(MISOC_DIRECTORY)/software/common.mak

OBJECTS=main.o isr.o

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

main.o: $(FM-DRIVER_DIRECTORY)/main.c
	$(compile)

%.o: $(FM-DRIVER_DIRECTORY)/%.c
	$(compile)

%.o: $(FM-DRIVER_DIRECTORY)/%.S
	$(assemble)

clean:
	$(RM) $(OBJECTS) fm-driver.elf fm-driver.bin .*~ *~

.PHONY: all clean main.o
