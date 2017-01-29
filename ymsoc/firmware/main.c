#include <generated/csr.h>
#include <generated/mem.h>

#include "ym2151.h"

int main(int argc, char * argv[])
{
    write_ym2151_addr(0x1B);
    while(YM_CHECK_BUSY);

    while(1)
    {
        write_ym2151_data(0x40);
        while(YM_CHECK_BUSY);
        write_ym2151_data(0x80);
        while(YM_CHECK_BUSY);
    }
}
