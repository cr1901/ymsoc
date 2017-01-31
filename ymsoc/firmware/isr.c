#include <generated/csr.h>
#include <irq.h>

volatile unsigned int num_samples = 0;

void isr(void);
void handle_sample(void);


void isr(void)
{
	unsigned int irqs;

	irqs = irq_pending() & irq_getmask();

	if(irqs & (1 << YM2151_INTERRUPT))
	{
		unsigned int reason = ym2151_ev_pending_read();
		if(reason & 0x01)
		{
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
