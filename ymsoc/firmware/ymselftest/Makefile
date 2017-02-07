include ../include/generated/variables.mak
include $(MISOC_DIRECTORY)/software/common.mak

INCLUDES += -I$(LIBYM2151_DIRECTORY)
# CFLAGS += -DSTOP_TEST

OBJECTS=main.o isr.o

all: ymselftest.bin

%.bin: %.elf
	$(OBJCOPY) -O binary $< $@
	chmod -x $@
	$(PYTHON) -m misoc.tools.mkmscimg $@

ymselftest.elf: $(YMSELFTEST_DIRECTORY)/linker.ld $(OBJECTS)

%.elf:
	$(LD) --gc-sections $(LDFLAGS) -T $< -N -o $@ \
		../libbase/crt0-$(CPU).o \
		$(OBJECTS) \
		-L../libbase \
		-L../libym2151 \
		-lbase-nofloat \
		-lym2151
	chmod -x $@
	lm32-elf-objdump -d ymselftest.elf > ymselftest.asm

main.o: $(YMSELFTEST_DIRECTORY)/main.c
	$(compile)

%.o: $(YMSELFTEST_DIRECTORY)/%.c
	$(compile)

%.o: $(YMSELFTEST_DIRECTORY)/%.S
	$(assemble)

clean:
	$(RM) $(OBJECTS) ymselftest.elf ymselftest.bin .*~ *~

.PHONY: all clean main.o
