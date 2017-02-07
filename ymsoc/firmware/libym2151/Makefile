include ../include/generated/variables.mak
include $(MISOC_DIRECTORY)/software/common.mak

OBJECTS=ym2151.o

all: libym2151.a

libym2151.a: $(OBJECTS) $(LIBYM2151_DIRECTORY)/ym2151.h
	$(AR) crs libym2151.a $(OBJECTS)

%.o: $(LIBYM2151_DIRECTORY)/%.c
	$(compile)

%.o: $(LIBYM2151_DIRECTORY)/%.S
	$(assemble)

$(LIBYM2151_DIRECTORY)/ym2151.h: $(BUILDINC_DIRECTORY)/ym2151_const.h

$(BUILDINC_DIRECTORY)/ym2151_const.h: $(LIBYM2151_DIRECTORY)/ym2151_const.m4
	m4 $< > $@

.PHONY: all clean

clean:
	$(RM) $(OBJECTS)
	$(RM) libym2151.a
