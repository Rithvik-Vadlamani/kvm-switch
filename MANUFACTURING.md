# A2 fabrication specification

100 × 100 mm; four layers F.Cu / In1.Cu GND / In2.Cu GND / B.Cu; 1.6 mm JLC04161H-7628 stackup; 1 oz outer / 0.5 oz inner; green mask, white silk; ENIG. Retain controlled impedance targets 100 Ω HDMI / 90 Ω USB and the reviewed stackup/trace dimensions. Original design uses 0.20 mm small vias and filled/capped via-in-pad construction.

All 59 exposed-pad holes under U6/U8/U10 the three new U6 ground-pin vias, and the four USB-C data vias listed in the fill file must be included in planarized copper-capped fill. Ordinary connector/header/switch holes must stay open. The fresh via-fill list identifies these 66 holes. Factory DFM and acceptance of the exact stackup and fill process remain pending.

This request is for bare boards for self-assembly. Five identical boards is the observed JLC minimum. One board is populated, with selected component spares. Use the new BOM; previous carts are stale. No payment is authorized.

Assembly and programming: follow the footprint pin-1 marks and firmware/README.md. The new AP63301 U1 has a different physical pin mapping from A0. Use the matching A2 placement file, never an A0 CPL. Physical bring-up follows PROTOTYPE_TEST.md and the deferred tests in verification/Circuit-review-A2.md.

## A2 additions and qualification status

U34/U35 supervise 3.3 V/5 V. U36 gates hub reset with MCU_NRST and the separate PA9 request; R49 holds that request low during MCU reset. C53–C55 decouple these ICs. R50 limits C8 reset-capacitor discharge current. These eight additions are in the matching BOM/CPL. Fresh reports supersede previous verification files. Do not interpret zero DRC errors as thermal, impedance, electrical-function or factory certification. The complete limits are in verification-A2/Review-results.md. Obtain a new supplier review and quote for the matching files.
