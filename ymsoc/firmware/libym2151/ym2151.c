#include "ym2151.h"

void load_ym2151_inst(ym2151_inst * inst, unsigned char chan)
{
    wait_ready();
    write_ym2151_wait(FB_CH1 + chan, FB_BITS(inst->fb) | CONECT_BITS(inst->conect));

    // Op order: M1, M2, C1, C2
    for(int op = 0; op < 4; op++)
    {
        ym2151_op * curr_op = &inst->op[op];
        unsigned char op_offs = chan + op*8;

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
    unsigned char rl_bits = FB_BITS(rt->inst->fb) | CONECT_BITS(rt->inst->conect);
    write_ym2151_wait(RL_CH1 + chan, RL_BITS(rt->rl) | rl_bits);
    write_ym2151_wait(KC_CH1 + chan, KC_BITS(rt->kc));
    write_ym2151_wait(KF_CH1 + chan, KF_BITS(rt->kf));
    write_ym2151_wait(PMS_CH1 + chan, PMS_BITS(rt->pms) | AMS_BITS(rt->ams));
}

void panic_ym2151(void)
{
    for(int chan=0; chan < 8; chan++)
    {
        write_ym2151_wait(FB_CH1 + chan, FB_BITS(0) | CONECT_BITS(0));
        for(int op = 0; op < 4; op++)
        {
            unsigned char op_offs = chan + op*8;
            write_ym2151_wait(MUL_CH1_M1 + op_offs, DT1_BITS(0) | MUL_BITS(0));
            write_ym2151_wait(TL_CH1_M1 + op_offs, TL_BITS(127));
            write_ym2151_wait(AR_CH1_M1 + op_offs, KS_BITS(0) | AR_BITS(0));
            write_ym2151_wait(D1R_CH1_M1 + op_offs, AMS_EN_BITS(0) | D1R_BITS(0));
            write_ym2151_wait(D2R_CH1_M1 + op_offs, DT2_BITS(0) | D2R_BITS(0));
            write_ym2151_wait(RR_CH1_M1 + op_offs, D1L_BITS(0) | RR_BITS(15));
        }
        write_ym2151_wait(KON_CH, KON_CH_BITS(chan) | KON_SN_BITS(0xF));
        write_ym2151_wait(KON_CH, KON_CH_BITS(chan) | KON_SN_BITS(0x0));
    }
}


void load_timerab(unsigned int pda, unsigned char pdb, int flag)
{
    if(flag & TIMER_A)
    {
        write_ym2151_wait(CLKA, CLKA_BITS(pda >> 2));
        write_ym2151_wait(CLKA2, CLKA2_BITS(pda));
    }

    if(flag & TIMER_B)
    {
        write_ym2151_wait(CLKB, CLKB_BITS(pdb));
    }
}

void ctl_timerab(unsigned char clear_ov, unsigned char irq_en, unsigned char load, unsigned char keyon, int flag)
{
    unsigned char ov_mask = clear_ov ? F_RESET_BITS(flag) : 0;
    unsigned char irq_mask = irq_en ? IRQEN_BITS(flag) : 0;
    unsigned char load_mask = load ? LOAD_BITS(flag) : 0;
    unsigned char csm_mask = CSM_BITS(keyon);
    write_ym2151_wait(LOAD,  csm_mask | ov_mask | irq_mask | load_mask);
}


void write_ym2151_wait(unsigned char addr, unsigned char data)
{
    write_ym2151_addr(addr);
    wait_ready();
    write_ym2151_data(data);
    wait_ready();
}
