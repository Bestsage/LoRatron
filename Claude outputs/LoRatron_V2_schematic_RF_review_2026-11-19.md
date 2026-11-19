# LoRatron V2: schematic and RF review (2026-11-19)

Target: ESP32-S3-MINI-1U-N8 + LR1121, **2-layer, 30 × 60 mm**, 4 × M2.5. Work on `main`.
Checked: the `loratron.kicad_sch` / `rf.kicad_sch` saved at 15:16, the netlist and ERC from kicad-cli.

## 1. MINI swap: what to fix

| # | Severity | Issue | Fix |
|---|---|---|---|
| 1 | **Blocker** | `LORA_IRQ` reaches only IC1.9 (DIO9). U4 pin 27 (IO47) isn't connected. ERC: "Label connected to only one pin". | Wire U4 pin 27 to the `LORA_IRQ` label. |
| 2 | **Blocker for layout** | IC1's Footprint field is `QFN50P500X500X100-33N-D` with no library nickname. ERC: "footprint library ''". Update PCB from Schematic can't load it. | Set it to `custom_footrpint:QFN50P500X500X100-33N-D`. |
| 3 | **Blocker for assembly** | The library footprint's EP (pad 33) still has `solder_paste_margin_ratio -25` = −2500 %, so no paste. The −10 % fix was only applied on the V1 board instance. A fresh layout pulls the broken library version. | Set it to `-0.1` in `custom_footpint.pretty/QFN50P500X500X100-33N-D.kicad_mod`, or under Footprint Properties → Clearance overrides in the editor. |
| 4 | ERC | 27 unused U4 pins are flagged "pin not connected". | Add no-connect flags. IO3/IO45/IO46 are strapping pins and are fine floating. |
| 5 | OK | 3V3 = pin 3; EN = pin 45 (10 k + 1 µF); IO0 = pin 4 (BOOT, 10 k); IO2 = pin 6 (LED, 470 Ω); USB D−/D+ = pins 23/24; TXD0/RXD0 = 39/40; SPI 14–17, BUSY 18, RST 25; all 24 GND pins on GND. The pin numbers match both KiCad's stock symbol and Espressif's own MINI-1U symbol. | — |
| 6 | Tidy | The custom `ESP32-S3-MINI-1U-N8` .kicad_sym, .kicad_mod and .stp aren't in the library tables and aren't used. | Delete them, or leave them untracked. |

Y1 (ECS-TXO-32CSMV) pin 1 tied to GND is **correct**: datasheet pins are 1 GND, 2 GND, 3 Out, 4 VDD. VDD is 1.7–3.465 V.

## 2. RF chain vs **Semtech reference designs** (updated 2026-11-19)

Sources: Semtech production packages from semtech.com, in `~/Downloads`:
- **LR1121MB1DIS e655v01a** (868/915 MHz DVK, **0402** passives): schematic + BOM.
- **LR1121MB2THDAS e742v01a** (868/915 MHz, **HP-only Tx, SPDT switch, TCXO**, 0201 passives, BOM rev 19.11.2024): schematic + BOM.

The HP Tx network and the antenna low-pass filter are **identical on both boards**. Values below are from the 0402 board (e655) unless stated.
These **replace the Waveshare values** in the first version of this review. Waveshare's sub-GHz Tx/Rx values differ from Semtech's and were dropped.

### A. HP PA Tx (pin 32 RFO_HP_LF → U3 RF1)
| Position | Current | Semtech |
|---|---|---|
| Choke VR_PA → pin 32 | L3 47 nH | **47 nH** LQW15AN47NJ00D ✓ |
| Across the choke | — | **200 Ω** (R33) |
| VR_PA decoupling | C11 100 nF, C12 100 pF | **2.2 nF + 47 pF** |
| Series trap at pin 32 | — | **3.3 nH (LQW15AN3N3C) ∥ 1.2 pF** |
| Shunt | — | **6.8 pF** |
| Series | L4 22 nH | **8.2 nH** (LQW15AN8N2J) |
| Shunt | C17 4.3 pF | **NC pad** (C11 on e655) |
| Series DC block | C18 47 pF | **47 pF** ✓ |
| Shunt (switch side) | — | **1.8 pF** |

### B. Rx (pin 30 RFI_P_LF0 / pin 29 RFI_N_LF0 → U3 RF2): lumped balun
| Position | Current | Semtech |
|---|---|---|
| P ↔ N | L5 56 nH | **22 nH** (LQW15AN22NH) |
| N → GND | C19 47 pF | **1.2 pF** (MB2 0201: 1.0 pF) |
| N → node A | — | **47 nH** (LQW15AN47NJ) |
| P → node A (series) | C20 1.2 pF to GND | **1.5 pF, series P→A** |
| A → GND | — | **NC pad** |
| A → switch RF2 | C21 47 pF from P | **47 pF from A** |

### C. 2.4 GHz (pin 26 RFIO_HF → J3)
| Position | Current | e655 (0402) | e742 (0201, 2024, tuned for 2.4 G Tx) |
|---|---|---|---|
| Shunt at pin | C14 1.3 pF ✓ | 1.3 pF | 0.8 pF |
| Series | L2 3.6 nH ✓ | 3.6 nH | 4.3 nH |
| Shunt | C15 1 pF | **1.6 pF** | 1.6 pF |
| Series (∥ NC pad) | — | **3.6 nH** | 3.6 nH |
| Shunt | — | **0.7 pF** | 1.8 pF |
| Series DC block | C16 47 pF | **33 pF** | 33 pF |
Use the e655 column, since it's tuned with 0402 parts like yours. Leave pad room to try the e742 values.

### D. Antenna low-pass after the switch (U3 RFC → J4), identical on both boards
RFC → **3.3 pF** shunt → **9.1 nH** series (LQW15AN9N1J) → **3.3 pF** shunt → **47 pF** series (C22) → J4.

### E. Switch control (PE4259 kept; Semtech e742 uses the BGS12WN6 SPDT)
**100 Ω series + 1 nF to GND** on each control line (V1, V2).

### F. Power and clock
| Item | Current | Semtech |
|---|---|---|
| DC-DC L1 | 2.2 µH 0805 | **10 µH TDK MLZ1608N100LT000 (0603)**; 15 µH MLZ1608N150L is the listed 2nd option. Replaces my earlier "15 µH" note. |
| VREG | C10 470 nF | 470 nF ✓ |
| VBAT_RF (pin 2) | C8 100 nF | **100 nF + 47 pF** |
| VBAT (pin 15) | C9 100 nF | 100 nF ✓ |
| Bulk | 22 µF at the LDO | 10 µF + 4×1 µF on VDD_RADIO → add **10 µF** near the LR1121 |
| VTCXO | C23 100 nF | **470 pF at pin 3 → ferrite BLM15AG100SN1D (0402 equivalent of BLM03AG100SN1D) → 100 nF at the TCXO** |
| TCXO → XTA | 10 pF + 220 Ω | **10 pF + 220 Ω** ✓ |

### Parts
Use Murata **LQW15AN** wirewound inductors and Murata **GRM1555C1H** C0G capacitors (0402), as in the e655 BOM. Change the RF inductor footprints from 0603 to **0402**.

## 3. RF on a 2-layer 1.6 mm board

- **The 0.35 mm traces from V1 are ~69 Ω on 2 layers.** They were 50 Ω only with In1 GND 0.2 mm below.
- **50 Ω options on 1.6 mm FR-4 (εr 4.5):** microstrip ≈ 3.0 mm (impractical); **CPWG 1.0 mm track / 0.15 mm gap** (or 1.25 / 0.2). On a 0.8 mm board: CPWG 0.8 / 0.15. Check with the KiCad calculator (Coplanar wave guide with ground plane) or JLC's impedance tool.
- **Keep RF lines short.** If the network-to-u.FL run is under ~5 mm, the width matters little. Put J3/J4 right at the end of each network.
- **B.Cu stays solid GND.** No tracks under the LR1121, the networks, the TCXO or the switch. Any B.Cu jumpers go elsewhere and stay short.
- **F.Cu GND pour around the RF:**
  - Fence vias every ≤ 2–3 mm along both sides of each RF line.
  - Each shunt cap gets its own GND via right at its pad.
- **LR1121 EP:** 3×3 vias (0.3 mm drill) to B GND, tented from the back; paste −10 %.
- **DC-DC:** keep the DCC_SW → L1 → VREG loop tight at pins 12–14, away from the TCXO and the RF networks.
- **TCXO:** right at pins 3–4, with a short XTA trace and GND around it.
- **Placement:**
  - One short edge: J3/J4 + LR1121 + RF.
  - Middle: MINI-1U. Its center GND pads get vias and solder, unlike the WROOM's.
  - Far short edge: USB-C, LDO, D1/D2, J2, buttons.
  - Route SPI on F.Cu between the two blocks, clear of the RF networks.
