# LoRatron PCB: handout for future sessions

*State as of 2026-11-19. Board fully routed, poured and stitched; ready for DRC, Gerber export and a JLC quote.*

## Context
- **What:** compact LoRa telemetry board for EPFL Rocket Team Space Race VII. It's a non-flight-critical add-on, mounted away from the main AV.
- **Parts:** ESP32-S3-WROOM-1U-N16R8 plus a bare Semtech LR1121 (sub-GHz + 2.4 GHz). External antennas on u.FL, no PCB antenna. The module's own u.FL is unused.
- **Tools and repo:** KiCad 10.0.8 (Flatpak, Linux). Project folder `~/Documents/Rockets/LoRa/LoRatron/`. Git branch **V1_Rares**; the friend's files stay untouched.
- **Ground rules:**
  - Allan commits himself. **No Claude attribution in commits.**
  - Be extra careful with schematic changes, and keep the existing components.
  - **KiCad must be closed** before any file edit. Check there's no `~*.lck` and that the mtime is unchanged, and back up first (`loratron.kicad_pcb.bak_before_*`).

## Board
- **Size:** 36 × 33 mm, outline (106.43, 52.1)–(142.43, 85.1), corner fillets R 2.5. M2.5 holes (pad Ø4.5, GND) at (109, 54.65), (139.85, 54.65), (109, 82.55), (139.85, 82.55).
- **Stackup:** 4 layers, JLC04161H-7628. F.Cu signals / In1 GND (solid) / In2 GND (priority zone under RF) / B.Cu signals. GND pours on F and B (clearance 0.3, thermal reliefs).
- **Sides:**
  - **Front:** ESP32 (IC2), USB-C J1 (GCT USB4105), ESD U2, LDO U1 (SOT-223), D1/D2 ORing diodes, C1–C7, R1–R4, R6, SW1 (EN), SW2 (BOOT/IO0), LED D3, J2 (4-pin: 1 +5V, 2 RXD0, 3 TXD0, 4 GND).
  - **Back, under the ESP32:** LR1121 (IC1) with its RF chain. J3 = 2.4 GHz u.FL (RFIO_HF path: C14/L2/C15/C16). J4 = sub-GHz u.FL through the PE4259 switch U3 (TX = RFO_HP_LF, RX = RFI_P_LF0). Also Y1 TCXO, L1 (DC-DC inductor) and the decoupling caps.
- **Rules:**
  - **Clearance:** Default 0.15; **Power class 0.2** (+5V, VBUS, +3.3V, /LDO_IN, /RF/VR_PA).
  - **Tracks:** min 0.15.
  - **Vias:** 0.6/0.3; hole-to-hole 0.3; hole clearance 0.3; copper-to-edge 0.3.
  - **Widths used:** signals 0.2–0.25; **RF 0.35 mm** (≈50 Ω microstrip on this stackup); power 0.4–0.5.

## Netlist facts worth knowing
- **ESP32 to LR1121** (module pin → GPIO, from the WROOM-1 pinout; check against the schematic):
  - SPI: NSS 18 (IO10), MOSI 19 (IO11), SCLK 20 (IO12), MISO 21 (IO13).
  - Control: BUSY 22 (IO14), LORA_RST 23 (IO21), LORA_IRQ 24 (IO47).
  - LR1121 side: SPI on DIO1–4 (pins 24 NSS, 23 SCK, 22 MOSI, 21 MISO); BUSY = pin 25, NRESET = pin 6, IRQ = pin 9.
- **RF switch:** LR1121 DIO5/DIO6 → nets V1/V2 → U3 pins 4/6. Set the matching RF-switch table in firmware.
- **TCXO:** Y1 is powered from LR1121 VTCXO (pin 3), coupled to XTA via 10 pF + 220 Ω (R5). Set **VTCXO = 1.8 V in firmware**.
- **USB:** native USB on IO19/IO20 (module pins 13/14). The ESP32-S3 is full-speed only (12 Mbps), so no impedance control is needed. CC1/CC2 have 5.1 kΩ pull-downs (R3, R4).
- **Power:** VBUS (USB) and +5V (J2) each go through a Schottky (D1/D2) → /LDO_IN → U1 → +3.3V. USB is for programming; in flight the board is powered from J2.
- **Indicators/buttons:** LED D3 on IO2 via R6; SW2 = BOOT (IO0, pull-up R2); SW1 = EN reset (R1 pull-up, C3).

## Layout decisions (don't undo by accident)
- **J1 fan-out:** J1's pins alternate D−/D+/D−/D+, with only 1.5 mm to the ESP32 pins, so every J1 signal pin has its own via (column at x = 115.12).
  - D− merges on the back, left of the column; D+ merges on the right.
  - Next to U2, D− and D+ have short under-body links, and VBUS drops through a via under U2's body.
- **Moved this session:**
  - R4 (CC2 pull-down) moved below J1, to (109.3, 75.2, −90).
  - D1 moved +0.2 mm in x (was overlapping H3's courtyard).
  - C8 moved to (128.9, 67.6), with its GND via at (130.0, 67.6). This frees the only via spot that feeds 3.3 V to LR1121 pin 2.
- **Paste:**
  - LR1121 EP (IC1 pad 33): paste ratio set to **−10%**. It was −25, which KiCad reads as −2500%, meaning no paste. **This pad must be soldered.**
  - The ESP32 center pads (41–49) stay unsoldered. They're tied to GND only so DRC passes.
- **Keepouts:**
  - Back RF area x 118.9–133.6, y 52.1–66.75: keep digital routing out.
  - The u.FL rule areas on J3/J4 are footprint zones stored in absolute coordinates, so they don't follow if you move the footprint.
- **Assembly:** back side first (paste + hot plate), then front by iron, at the EPFL makerspace.

## DRC: expected items to exclude
- **J1 hole clearance (8):** inherent to the USB4105 footprint.
- **J1 thermal-relief "spoke count":** those GND pads are tied to the shield legs by traces.
- **Silkscreen overlap:** cosmetic.

## Open items
1. **Before ordering:** compare RF matching values and the DC-DC inductor (2.2 µH) with Semtech's LR1121 reference design.
2. Firmware: VTCXO 1.8 V, the RF-switch table for DIO5/DIO6, the SPI/IRQ pins above.
3. Optional: silkscreen cleanup (reference overlaps, mostly in the back RF area), teardrops, and a small +3.3 V copper area around the U1 tab for heat (not needed at ~0.3 W).
4. JLC order: 4 L, FR-4, 1.6 mm, JLC04161H-7628, tented vias, HASL lead-free (or ENIG for flatter QFN pads). Optional: stencil for the back paste layer.

## Tips for a future Claude session
- Read this file and work on a copy of `loratron.kicad_pcb` with KiCad closed.
- In the KiCad 10 file, pad angles are stored as absolute angles; back footprints store mirrored local coordinates.
- Konnect MCP (KiCad IPC) only exposed its starter tools here, so edits were done on the saved file.
- The helper scripts from the 2026-11-19 session lived in a temporary workspace and are not saved anywhere; regenerate as needed.
