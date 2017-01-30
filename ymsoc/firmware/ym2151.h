#ifndef YM2151_H
#define YM2151_H

#include <generated/mem.h>
#include "ym2151_const.h"

/* YM2151_BASE will be created by MiSoC. */
#define YM_ADDR (volatile unsigned char *) YM2151_BASE
#define YM_DATA (volatile unsigned char *) (YM2151_BASE + 4)

/* Read constants. */
#define YM_BUSY 0x80
#define YM_IST 0x03

#define YM_CHECK_BUSY read_ym2151() & YM_BUSY


void write_ym2151_wait(unsigned char addr, unsigned char data);
void write_ym2151_no_wait(unsigned char addr, unsigned char data);
inline void write_ym2151_addr(unsigned char addr);
inline void write_ym2151_data(unsigned char data);
inline unsigned char read_ym2151(void);
inline void wait_ym2151(void);


void write_ym2151_wait(unsigned char addr, unsigned char data)
{
    write_ym2151_addr(addr);
    wait_ym2151();
    write_ym2151_data(data);
    wait_ym2151();
}

void write_ym2151_no_wait(unsigned char addr, unsigned char data)
{
    write_ym2151_addr(addr);
    write_ym2151_data(data);
}

inline void write_ym2151_addr(unsigned char addr)
{
    (* YM_ADDR) = addr;
}

inline void write_ym2151_data(unsigned char data)
{
    (* YM_DATA) = data;
}

inline unsigned char read_ym2151(void)
{
    return (* YM_DATA);
}

inline void wait_ym2151(void)
{
    while(YM_CHECK_BUSY);
}



#endif
