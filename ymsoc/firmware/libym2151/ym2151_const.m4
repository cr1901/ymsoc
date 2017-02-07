#ifndef YM2151_CONST
#define YM2151_CONST
divert(-1)dnl

# https://www.gnu.org/software/m4/manual/m4-1.4.15/html_node/Improved-forloop.html#Improved-forloop
define(`forloop', `ifelse(eval(`($2) <= ($3)'), `1',
  `pushdef(`$1')_$0(`$1', eval(`$2'),
    eval(`$3'), `$4')popdef(`$1')')')dnl
define(`_forloop',
  `define(`$1', `$2')$4`'ifelse(`$2', `$3', `',
    `$0(`$1', incr(`$2'), `$3', `$4')')')

# Registers are of the form NAME_CHX_{MX, CX}
define(`reg_addr_op', `eval($1 + $2 + $3 - 1, `16')')
define(`reg_define_op', `#define $1_CH'`$3'`_$2 $4')
define(`reg_define_wrap_op', `reg_define_op(`$1', `$2', $3, 0x`'reg_addr_op($1, $2, $3))')

# Registers are of the form NAME_CHX
define(`reg_addr_ch', `eval($1 + $2 - 1, `16')')
define(`reg_define_ch', `#define $1_CH'`$2'` $3')
define(`reg_define_wrap_ch', `reg_define_ch(`$1', `$2', 0x`'reg_addr_ch($1, $2))')

# Shift bits to appropriate location.
define(`valid_bits', `eval((1 << $1) - 1, `16')')
define(`define_bits',
``#define $1_BITS(_x) (((unsigned char) (_x) & 0x'valid_bits($2)`) << $3)'')

# Iterate over operators and channels.
define(`for_op',
`for_chan_op(`$1', `M1')
for_chan_op(`$1', `M2')
for_chan_op(`$1', `C1')
for_chan_op(`$1', `C2')dnl'
)

# Create a define for each channel.
define(`for_chan', `forloop(`i', `1', `8', `reg_define_wrap_ch(`$1', i)
')')

# Create a define for each channel, given operator.
define(`for_chan_op', `forloop(`i', `1', `8', `reg_define_wrap_op(`$1', `$2', i)
')')

# gen_reg_const(name, addr, bits, bits_offset)
# Create a constant unique to each operator.
define(`gen_reg_const_op',
`define(`$1', $2)dnl
/* Constant definitions for `$1' */
for_op(`$1')
define_bits(`$1', $3, $4)

')

# Same, but for each channel.
define(`gen_reg_const_chan',
`define(`$1', $2)dnl
/* Constant definitions for `$1' */
for_chan(`$1')
define_bits(`$1', $3, $4)

')

# Single constant.
define(`gen_reg_const',
`define(`$1', $2)dnl
/* Constant definitions for `$1' */
#define $1 $2
define_bits(`$1', $3, $4)

')

# Defines-required by macros...
define(`M1', 0)
define(`M2', 8)
define(`C1', 16)
define(`C2', 24)

# Begin constant defines.
divert`'dnl

gen_reg_const(`TEST0', 0x01, 6, 2)dnl
gen_reg_const(`LFO_RESET', 0x01, 1, 1)dnl
gen_reg_const(`TEST1', 0x01, 1, 0)dnl
gen_reg_const(`KON_SN', 0x08, 4, 3)dnl
gen_reg_const(`KON_CH', 0x08, 3, 0)dnl
gen_reg_const(`NE', 0x0f, 1, 7)dnl
gen_reg_const(`NFRQ', 0x0f, 5, 0)dnl
gen_reg_const(`CLKA', 0x10, 8, 0)dnl
gen_reg_const(`CLKA2', 0x11, 2, 0)dnl
gen_reg_const(`CLKB', 0x12, 8, 0)dnl
gen_reg_const(`CSM', 0x14, 1, 7)dnl
gen_reg_const(`F_RESET', 0x14, 2, 4)dnl
gen_reg_const(`IRQEN', 0x14, 2, 2)dnl
gen_reg_const(`LOAD', 0x14, 2, 0)dnl
gen_reg_const(`LFRQ', 0x18, 8, 0)dnl
gen_reg_const(`PMD', 0x19, 8, 0)dnl
gen_reg_const(`AMD', 0x19, 8, 0)dnl
gen_reg_const(`W', 0x1b, 2, 0)dnl
gen_reg_const(`CT', 0x1b, 2, 6)dnl
gen_reg_const_chan(`RL', 32, 2, 6)dnl
gen_reg_const_chan(`FB', `RL', 3, 3)dnl
gen_reg_const_chan(`CONECT', `RL', 3, 0)dnl
gen_reg_const_chan(`KC', 40, 7, 0)dnl
gen_reg_const_chan(`KF', 48, 6, 2)dnl
gen_reg_const_chan(`PMS', 56, 3, 4)dnl
gen_reg_const_chan(`AMS', `PMS', 2, 0)dnl
gen_reg_const_op(`DT1', 64, 3, 4)dnl
gen_reg_const_op(`MUL', DT1, 4, 0)dnl
gen_reg_const_op(`TL', 96, 7, 0)dnl
gen_reg_const_op(`AR', 128, 5, 0)dnl
gen_reg_const_op(`KS', AR, 2, 6)dnl
gen_reg_const_op(`D1R', 160, 5, 0)dnl
gen_reg_const_op(`AMS_EN', D1R, 1, 7)dnl
gen_reg_const_op(`DT2', 192, 2, 6)dnl
gen_reg_const_op(`D2R', DT2, 5, 0)dnl
gen_reg_const_op(`D1L', 224, 4, 4)dnl
gen_reg_const_op(`RR', D1L, 4, 0)dnl

#endif
