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

#define YM_CHECK_BUSY (read_ym2151() & YM_BUSY)


typedef struct ym2151_op
{
    unsigned char dt1;
    unsigned char mul;
    unsigned char tl;
    unsigned char ks;
    unsigned char ar;
    unsigned char ams_en;
    unsigned char d1r; // Decay Rate
    unsigned char dt2;
    unsigned char d2r; // Sustain Rate
    unsigned char d1l; // Sustain Level
    unsigned char rr;
} ym2151_op;

typedef struct ym2151_inst
{
    ym2151_op op[4];
    unsigned char fb;
    unsigned char conect;
} ym2151_inst;

typedef struct ym2151_rt
{
    ym2151_inst inst;
    unsigned char rl;
    unsigned char kc;
    unsigned char kf;
    unsigned char pms;
    unsigned char ams;
    unsigned char kon;
} ym2151_rt; // Register Runtime Info. "Inherit" this struct to add custom info.
// I suggest creating an array of 8 so you can have a mirror of registers.


void load_ym2151_inst(ym2151_inst * inst, unsigned char chan);
void load_ch_params(ym2151_rt * rt, unsigned char chan); // Do not use for updating, only for reset/init.

void write_ym2151_wait(unsigned char addr, unsigned char data);
void write_ym2151_no_wait(unsigned char addr, unsigned char data);
inline void write_ym2151_addr(unsigned char addr);
inline void write_ym2151_data(unsigned char data);
inline unsigned char read_ym2151(void);
inline void wait_ready(void);

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

inline void wait_ready(void)
{
    while(YM_CHECK_BUSY);
}


#endif
