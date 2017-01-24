#include <generated/csr.h>
#include <generated/mem.h>

#include "ym2151.h"

int main(int argc, char * argv[])
{
    unsigned char i = 0;
    //write_ym2151_addr(0x1B);

    while(1)
    {
        write_ym2151_wait(0x1B, 0x40);
        write_ym2151_wait(0x1B, 0x80);
        //write_ym2151_data(0x40);
        //wait_ym2151();
        //write_ym2151_data(0x80);
        //wait_ym2151();
        //write_ym2151_data(0xC0);
        //wait_ym2151();
        //write_ym2151_data(0x00);
        //wait_ym2151();
    }
}
