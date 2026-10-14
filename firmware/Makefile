CROSS ?= arm-none-eabi-
CFLAGS = -mcpu=cortex-m0 -mthumb -Os -g3 -std=gnu11 -Wall -Wextra -Werror -ffreestanding -fno-builtin -ffunction-sections -fdata-sections
all: kvm.bin kvm.hex
kvm.elf: main.c startup.c control.c control.h stm32f030c8.ld
	$(CROSS)gcc $(CFLAGS) -nostdlib -Wl,--gc-sections,-Map=kvm.map -T stm32f030c8.ld main.c startup.c control.c -lgcc -o $@
	$(CROSS)size $@
kvm.bin: kvm.elf
	$(CROSS)objcopy -O binary $< $@
kvm.hex: kvm.elf
	$(CROSS)objcopy -O ihex $< $@
clean:
	rm -f kvm.elf kvm.bin kvm.hex kvm.map
.PHONY: all clean
