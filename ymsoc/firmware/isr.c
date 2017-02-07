#include <generated/csr.h>
#include <irq.h>

#include "ym2151.h"

volatile unsigned int num_samples = 0;
volatile int timera_ov = 0;
volatile int timerb_ov = 0;

void isr(void);
void handle_sample(void);


void isr(void)
{
	unsigned int irqs;

	irqs = irq_pending() & irq_getmask();

	if(irqs & (1 << YM2151_INTERRUPT))
	{
		// Fun: Set timer A to 0x3FF and uncomment the below line.
		//write_ym2151_wait(CT, CT_BITS(0x03));
		unsigned int reason = ym2151_ev_pending_read();
		if(reason & 0x01)
		{
			unsigned int timer_flags = readirq_timerab();
			if(timer_flags & TIMER_A)
			{
				timera_ov = 1;
			}

			if(timer_flags & TIMER_B)
			{
				timerb_ov = 1;
			}

			ctl_timerab(1, 1, 0, 0, timer_flags);
			ym2151_ev_pending_write(0x01);
		}

		if(reason & 0x02)
		{
			handle_sample();
			ym2151_ev_pending_write(0x02);
		}
	}
}


void handle_sample(void)
{
	num_samples++;
}
