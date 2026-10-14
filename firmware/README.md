# Two-computer switch firmware

Target: STM32F030C8T6, 64 KiB flash and 8 KiB RAM. This firmware is a prototype implementation. It builds and passes host-side state-machine tests; it has not been run on assembled hardware.

On power-up, host 1 is selected. Each debounced button press alternates between hosts. A held button produces one change. Both HDMI switches and the USB multiplexer use the same host selection.

Switching disables HDMI and USB, holds the USB hub in reset and removes its VBUS-detect indication. After 150 ms the selector changes and hub reset is released. After a further 100 ms HDMI is enabled. USB is enabled only when the selected host's data connector supplies VBUS. USB presence changes use the same disconnect and reset sequence. A watchdog resets the MCU if the main loop stops servicing it.

The HDMI path switches DDC and hot-plug detect with video. There is no EDID emulation. Operating systems can detect a monitor disconnect during a host change. Charging and USB Power Delivery are not implemented.

## Build and test

Use an Arm GNU embedded toolchain and GNU Make:

```sh
make CROSS=/path/to/arm-none-eabi-
cc -std=c11 -Wall -Wextra -Werror control.c test_control.c -o test_control
./test_control
cc -std=c11 -Wall -Wextra -Werror control.c test_outputs.c -o test_outputs
./test_outputs
```

The provided build produces `kvm.elf`, `kvm.hex`, `kvm.bin` and `kvm.map`. The binary is linked at flash address `0x08000000`. The Intel HEX file includes its address. The reset vector is at the start of flash. No bootloader, external crystal, option-byte change or readout protection is required.

## Programming through J4

| J4 pin | Signal | Connection |
|---|---|---|
| 1 | +3.3 V | Programmer target-voltage reference |
| 2 | SWDIO | Programmer SWDIO |
| 3 | GND | Programmer ground |
| 4 | SWCLK | Programmer SWCLK |
| 5 | NRST | Programmer target reset |

Pin 1 is the square pad. Connect by pin number, not cable color. J4 is a 1x5, 2.54 mm header; use a breakout cable if the programmer has an STDC14 or other connector. Power the board from its regulated 12 V input. Pin 1 is a voltage reference and is not intended to power the board from the programmer.

Use STM32CubeProgrammer or an equivalent SWD programmer, selecting STM32F030C8T6. Connect under reset if a watchdog-running device is difficult to attach to. Program `kvm.hex`, or program `kvm.bin` at `0x08000000`. Verify flash contents after programming, then disconnect and power-cycle. Keep readout protection disabled for prototype debugging.

For factory programming, include the firmware file, this pinout, the exact MCU part number, programming address, verify-after-write instruction and normal-power-cycle test in the assembly request. Confirm that JLCPCB accepts the fixture and firmware format before paying for the service.

## Validation performed

Compilation uses `-Wall -Wextra -Werror`. The host tests cover initial enable timing, both switching directions, selected-host USB unplug/replug, repeated requests during a transition, timer wraparound and randomized request/presence sequences. They check that selection changes only while the switched paths are disabled. The GPIO regression test executes the actual output-write routine against a register model and checks that video remains continuously enabled when the USB cable is absent. Watchdog startup follows ST's sequence: start the watchdog/LSI clock before waiting for prescaler and reload updates.

These tests validate state-machine logic. They do not validate MCU electrical levels, oscillator startup, USB enumeration, HDMI timing, PCB impedance or power integrity. Those require the assembled prototype.

## Reference documents

- [STM32F030x4/x6/x8/xC datasheet](https://www.st.com/resource/en/datasheet/stm32f030c8.pdf)
- [STM32F0 reference manual RM0360](https://www.st.com/resource/en/reference_manual/rm0360-stm32f0x1-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)
- [ST CMSIS STM32F030x8 register definitions](https://github.com/STMicroelectronics/cmsis-device-f0/blob/master/Include/stm32f030x8.h)
- [JLCPCB programming service](https://jlcpcb.com/help/article/pcba-programming-service)

- [ST watchdog initialization reference](https://github.com/STMicroelectronics/stm32f0xx-hal-driver/blob/master/Src/stm32f0xx_hal_iwdg.c)

## A2 hardware reset interface

PA9 now drives HUB_RESET_REQ, an input of U36. It remains push-pull. U36 releases HUB_RESET_N only when MCU_NRST and the request are high. R49 pulls the request down during reset; U34/U35 supervise the supply rails. C8 remains as a reset filter with 1 kohm series resistor R50 in its ground leg. The original switching state machine is retained. `test_startup.c` exercises actual GPIO initialization, including safe latches before output mode and preservation of SWD pins. The independent state exploration and mutation results are included in the A2 verification package. Hardware reset waveforms and actual MCU execution are still untested.

Unused GPIOA pins and GPIOB/C/F digital input buffers are disabled with analog mode, including unused/unbonded pins. Active inputs/outputs and PA13/PA14 SWD remain configured as required. Register addresses and RCC bits were checked against ST cmsis-device-f0/stm32f030x8.h. The embedded build is 980 bytes of flash plus 4 bytes of static RAM; actual stack use has not been measured.
