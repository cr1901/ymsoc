#include <generated/csr.h>
#include <generated/mem.h>
#include <irq.h>

#include "ym2151.h"


extern volatile unsigned int num_samples;
extern volatile int timerb_ov;


int main(int argc, char * argv[])
{
    irq_setie(1);
    ym2151_ev_enable_write(0x03);
    irq_setmask((1 << YM2151_INTERRUPT));

#ifdef STOP_TEST
    wait_ready();
    write_ym2151_wait(KON_CH, KON_CH_BITS(0) | KON_SN_BITS(0x0));

    while(1)
    {

    }
#else

    ym2151_inst sine =
    {
        .op = {
            {
                .dt1 = 0, .mul = 1, .tl = 0, .ks = 0,
                .ar = 1, .ams_en = 0, .d1r = 0, .dt2 = 0,
                .d2r = 0, .d1l = 0, .rr = 15
            },
            {
                .dt1 = 0, .mul = 0, .tl = 0, .ks = 0,
                .ar = 0, .ams_en = 0, .d1r = 0, .dt2 = 0,
                .d2r = 0, .d1l = 0, .rr = 0
            },
            {
                .dt1 = 0, .mul = 0, .tl = 0, .ks = 0,
                .ar = 0, .ams_en = 0, .d1r = 0, .dt2 = 0,
                .d2r = 0, .d1l = 0, .rr = 0
            },
            {
                .dt1 = 0, .mul = 0, .tl = 0, .ks = 0,
                .ar = 0, .ams_en = 0, .d1r = 0, .dt2 = 0,
                .d2r = 0, .d1l = 0, .rr = 0
            }
        },

        .fb = 0,
        .conect = 7
    };

    ym2151_rt sine_rt =
    {
        .inst = &sine,
        .rl = 3,
        .kc = 0x40 + 10,
        .kf = 0,
        .pms = 0,
        .ams = 0
    };

    load_ym2151_inst(&sine, 0);
    load_ch_params(&sine_rt, 0);

    load_timerab(0, 16, TIMER_B);
    irqen_timerab(TIMER_B);
    start_timerab(TIMER_B);

    while(YM_CHECK_BUSY);
    write_ym2151_wait(CT, CT_BITS(0x01));

    while(!timerb_ov)
    {

    }

    start_timerab(0);
    irqen_timerab(0);

    while(YM_CHECK_BUSY);
    write_ym2151_wait(CT, CT_BITS(0x03));

    while(1)
    {

    }


    /* Go! */
    write_ym2151_wait(KON_CH, KON_CH_BITS(0) | KON_SN_BITS(0x1));

    unsigned char i = 0;
    while(1)
    {
        if(num_samples == 32000)
        {
            i = ((i + 1) & 0x03);
            while(YM_CHECK_BUSY);
            write_ym2151_addr(CT);
            while(YM_CHECK_BUSY);
            write_ym2151_data(CT_BITS(i));
            num_samples = 0;
        }
    }
#endif
}
