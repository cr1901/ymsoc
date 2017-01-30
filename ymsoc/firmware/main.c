#include <generated/csr.h>
#include <generated/mem.h>

#include "ym2151.h"

int main(int argc, char * argv[])
{
    /* write_ym2151_addr(CT);
    while(YM_CHECK_BUSY);

    while(1)
    {
        write_ym2151_data(CT_BITS(0x1));
        while(YM_CHECK_BUSY);
        write_ym2151_data(CT_BITS(0x2));
        while(YM_CHECK_BUSY);
    } */

    /* Channel 1, Algorithm 7, Operator M1, 440 Hz. */
    /* Phase generator */
    write_ym2151_wait(KC_CH1, KC_BITS(0x40 + 10));
    write_ym2151_wait(KF_CH1, KF_BITS(0));
    write_ym2151_wait(MUL_CH1_M1, MUL_BITS(1));
    write_ym2151_wait(DT1_CH1_M1, DT1_BITS(0));
    write_ym2151_wait(DT2_CH1_M1, DT2_BITS(0));
    write_ym2151_wait(PMS_CH1, PMS_BITS(0));

    /* write_ym2151_wait(MUL_CH1_M2, MUL_BITS(0));
    write_ym2151_wait(DT1_CH1_M2, DT1_BITS(0));
    write_ym2151_wait(DT2_CH1_M2, DT2_BITS(0));

    write_ym2151_wait(MUL_CH1_C1, MUL_BITS(0));
    write_ym2151_wait(DT1_CH1_C1, DT1_BITS(0));
    write_ym2151_wait(DT2_CH1_C1, DT2_BITS(0));

    write_ym2151_wait(MUL_CH1_C2, MUL_BITS(0));
    write_ym2151_wait(DT1_CH1_C2, DT1_BITS(0));
    write_ym2151_wait(DT2_CH1_C2, DT2_BITS(0)); */

    /* FM operator */
    write_ym2151_wait(FB_CH1, RL_BITS(3) | FB_BITS(0) | CONECT_BITS(7));

    /* Envelope generator */
    write_ym2151_wait(AR_CH1_M1, AR_BITS(31));
    write_ym2151_wait(D1R_CH1_M1, D1R_BITS(0));
    write_ym2151_wait(D2R_CH1_M1, D2R_BITS(0));
    write_ym2151_wait(RR_CH1_M1, RR_BITS(15));
    write_ym2151_wait(KS_CH1_M1, KS_BITS(0));
    write_ym2151_wait(D1L_CH1_M1, D1L_BITS(0));
    write_ym2151_wait(TL_CH1_M1, TL_BITS(10));

    /* write_ym2151_wait(AR_CH1_M2, AR_BITS(0));
    write_ym2151_wait(D1R_CH1_M2, D1R_BITS(0));
    write_ym2151_wait(D2R_CH1_M2, D2R_BITS(0));
    write_ym2151_wait(RR_CH1_M2, RR_BITS(0));
    write_ym2151_wait(KS_CH1_M2, KS_BITS(0));
    write_ym2151_wait(D1L_CH1_M2, D1L_BITS(0));
    write_ym2151_wait(TL_CH1_M2, TL_BITS(0));

    write_ym2151_wait(AR_CH1_C1, AR_BITS(0));
    write_ym2151_wait(D1R_CH1_C1, D1R_BITS(0));
    write_ym2151_wait(D2R_CH1_C1, D2R_BITS(0));
    write_ym2151_wait(RR_CH1_C1, RR_BITS(0));
    write_ym2151_wait(KS_CH1_C1, KS_BITS(0));
    write_ym2151_wait(D1L_CH1_C1, D1L_BITS(0));
    write_ym2151_wait(TL_CH1_C1, TL_BITS(0));

    write_ym2151_wait(AR_CH1_C2, AR_BITS(0));
    write_ym2151_wait(D1R_CH1_C2, D1R_BITS(0));
    write_ym2151_wait(D2R_CH1_C2, D2R_BITS(0));
    write_ym2151_wait(RR_CH1_C2, RR_BITS(0));
    write_ym2151_wait(KS_CH1_C2, KS_BITS(0));
    write_ym2151_wait(D1L_CH1_C2, D1L_BITS(0));
    write_ym2151_wait(TL_CH1_C2, TL_BITS(0)); */

    /* Go! */
    write_ym2151_wait(KON_CH, KON_CH_BITS(0) + KON_SN_BITS(0x1));
    while(1);
}
