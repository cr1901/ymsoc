#include <generated/csr.h>
#include <generated/mem.h>

int main(int argc, char * argv[])
{
    int a;
    //leds_out_write(0x01);

    (* (char *) YM2151_BASE) = 0x1B;
    (* (char *) (YM2151_BASE + 4)) = 0x40;

    while(1)
    {
        (void) a;
    }
}