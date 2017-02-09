#include <generated/csr.h>
#include <generated/mem.h>
#include <irq.h>

#include <ym2151.h>

#define CHAN 1

extern volatile unsigned int num_samples;
extern volatile int timera_ov;
extern volatile int timerb_ov;
extern volatile int host_flag;

int main(int argc, char * argv[])
{
    irq_setie(1);
    ym2151_ev_enable_write(0x03);
    host_ev_enable_write(0x01);
    irq_setmask((1 << YM2151_INTERRUPT) | (1 << HOST_INTERRUPT));
    panic_ym2151();

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
                .ar = 15, .ams_en = 0, .d1r = 0, .dt2 = 0,
                .d2r = 0, .d1l = 0, .rr = 0
            },
            {
                .dt1 = 0, .mul = 0, .tl = 127, .ks = 0,
                .ar = 0, .ams_en = 0, .d1r = 0, .dt2 = 0,
                .d2r = 0, .d1l = 0, .rr = 0
            },
            {
                .dt1 = 0, .mul = 0, .tl = 127, .ks = 0,
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

    load_ym2151_inst(&sine, CHAN);
    load_ch_params(&sine_rt, CHAN);

    load_timerab(0x3FE, 0, TIMER_A);
    ctl_timerab(1, 1, 1, 0, TIMER_A);

    while(!timera_ov)
    {

    }

    ctl_timerab(0, 0, 0, 0, TIMER_A);

    /* Go! */
    write_ym2151_wait(KON_CH, KON_CH_BITS(CHAN) | KON_SN_BITS(0x5));

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

        if(host_flag == 0x5555AAAA)
        {
            host_flag = 0;
            // Xfer something back as test.
            break;
        }
    }
#endif
}
