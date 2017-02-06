#include "ym2151.h"

void load_ym2151_inst(ym2151_inst * inst, unsigned char chan)
{
    wait_ready();
    write_ym2151_wait(FB_CH1 + chan * 8, FB_BITS(inst->fb) | CONECT_BITS(inst->conect));

    // Op order: M1, M2, C1, C2
    for(int op = 0; op < 4; op++)
    {
        ym2151_op * curr_op = &inst->op[op];
        unsigned char op_offs = chan*32 + op*8;

        write_ym2151_wait(MUL_CH1_M1 + op_offs, DT1_BITS(curr_op->dt1) | MUL_BITS(curr_op->mul));
        write_ym2151_wait(TL_CH1_M1 + op_offs, TL_BITS(curr_op->tl));
        write_ym2151_wait(AR_CH1_M1 + op_offs, KS_BITS(curr_op->ks) | AR_BITS(curr_op->ar));
        write_ym2151_wait(D1R_CH1_M1 + op_offs, AMS_EN_BITS(curr_op->ams_en) | D1R_BITS(curr_op->d1r));
        write_ym2151_wait(D2R_CH1_M1 + op_offs, DT2_BITS(curr_op->dt2) | D2R_BITS(curr_op->d2r));
        write_ym2151_wait(RR_CH1_M1 + op_offs, D1L_BITS(curr_op->d1l) | RR_BITS(curr_op->rr));
    }
}

// Does *not* set KON/KOFF!
void load_ch_params(ym2151_rt * rt, unsigned char chan)
{
    wait_ready();
    unsigned char rl_bits = FB_BITS(rt->inst.fb) | CONECT_BITS(rt->inst.conect);
    write_ym2151_wait(RL_CH1 + chan, RL_BITS(rt->rl) | rl_bits);
    write_ym2151_wait(KC_CH1 + chan, KC_BITS(rt->kc));
    write_ym2151_wait(KF_CH1 + chan, KF_BITS(rt->kf));
    write_ym2151_wait(PMS_CH1 + chan, PMS_BITS(rt->pms) | AMS_BITS(rt->ams));
}


void write_ym2151_wait(unsigned char addr, unsigned char data)
{
    write_ym2151_addr(addr);
    wait_ready();
    write_ym2151_data(data);
    wait_ready();
}

void write_ym2151_no_wait(unsigned char addr, unsigned char data)
{
    write_ym2151_addr(addr);
    write_ym2151_data(data);
}
