# HDMI/USB KVM switch

A four-layer board and STM32F030 firmware for sharing two HDMI displays and a four-port USB 2.0 hub between two computers. I designed the switching hardware and firmware, including supply supervision, hub reset control, and a timed disconnect sequence.

## Start here

- [Firmware and host-side tests](firmware/README.md)
- [Editable KiCad project](KVM_Switch.kicad_pro)
- [Prototype test plan](PROTOTYPE_TEST.md)
- [A2 verification results](verification-A2/Review-results.md)
- [Manufacturing notes](MANUFACTURING.md)

Current published design: A2, September 2026. It uses external regulated 12 V power. The USB-C host connectors carry USB 2.0 data; they do not provide USB-C video or USB Power Delivery.

The firmware switches with a 150 ms disconnect interval followed by 100 ms of settling, handles host detection, debounces the selection button, and uses watchdog recovery. The verification package contains state exploration and mutation results, plus PCB checks.

## Build and test

The firmware needs GNU Make and the GNU Arm toolchain. Run `make -C firmware` to build the STM32 image. The firmware README describes the host-side checks.

This is a prototype design. Firmware/model tests and static PCB checks do not establish USB enumeration, HDMI interoperability, signal integrity, or physical operating limits. The board has not been qualified on assembled hardware.
