include paths.mak

# RTL- Source dir of m-labs version of lm32
# JT51- Source dir of JT51
# YMSOC- Root of YMSoC

SOURCES = lm32_config.v
SOURCES += $(RTL)/lm32_adder.v $(RTL)/lm32_addsub.v $(RTL)/lm32_cpu.v
SOURCES += $(RTL)/lm32_dcache.v $(RTL)/lm32_debug.v $(RTL)/lm32_decoder.v
SOURCES += $(RTL)/lm32_dp_ram.v $(RTL)/lm32_icache.v
SOURCES += $(RTL)/lm32_instruction_unit.v $(RTL)/lm32_interrupt.v
SOURCES += $(RTL)/lm32_jtag.v $(RTL)/lm32_load_store_unit.v
SOURCES += $(RTL)/lm32_logic_op.v $(RTL)/lm32_mc_arithmetic.v
SOURCES += $(RTL)/lm32_multiplier.v $(RTL)/lm32_ram.v $(RTL)/lm32_shifter.v
SOURCES += $(RTL)/lm32_itlb.v $(RTL)/lm32_dtlb.v
SOURCES += $(RTL)/lm32_top.v

SOURCES += $(JT51)/jt51.v $(JT51)/jt51_envelope.v $(JT51)/jt51_exptable.v
SOURCES += $(JT51)/jt51_lfo_lfsr.v $(JT51)/jt51_mmr.v $(JT51)/jt51_noise_lfsr.v
SOURCES += $(JT51)/jt51_phasegen.v $(JT51)/jt51_pm.v $(JT51)/jt51_sh.v
SOURCES += $(JT51)/jt51_sintable.v $(JT51)/jt51_timers.v $(JT51)/jt51_acc.v
SOURCES += $(JT51)/jt51_exp2lin.v $(JT51)/jt51_lfo.v $(JT51)/jt51_lin2exp.v
SOURCES += $(JT51)/jt51_noise.v $(JT51)/jt51_op.v $(JT51)/jt51_phinc_rom.v
SOURCES += $(JT51)/jt51_reg.v $(JT51)/jt51_sh2.v $(JT51)/jt51_sum_op.v

SOURCES += $(YMSOC)/build/gateware/top.v $(YMSOC)/ymsoc/extern/wb_async_reg.v

all: sim

$(YMSOC)/build/gateware/top.v: $(YMSOC)/ymsoc/*.py $(YMSOC)/ymsoc/platforms/sim.py $(YMSOC)/ymsoc/firmware/*.c
	cd $(YMSOC)
	PYTHONPATH=$(YMSOC) python3 -m ymsoc --device xc6slx25 build --jt51-dir $(JT51) --output-dir $(YMSOC)/build --no-compile-gateware ymsoc.platforms.sim

ymsoc_tb.vvp: ymsoc_tb.v $(YMSOC)/build/gateware/top.v $(YMSOC)/build/gateware/mem.init $(YMSOC)/build/software/fm-driver/fm-driver.bin
	iverilog -o ymsoc_tb.vvp -I. -I$(RTL) -I$(JT51) ymsoc_tb.v $(SOURCES)
	cp $(YMSOC)/build/gateware/mem.init .
	lm32-elf-objdump -d $(YMSOC)/build/software/fm-driver/fm-driver.elf > fm-driver.asm

sim: ymsoc_tb.vvp
	vvp ymsoc_tb.vvp
