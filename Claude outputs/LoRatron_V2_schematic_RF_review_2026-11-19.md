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

## 2. RF chain vs reference

Reference: the Waveshare Core1121-XF schematic, a production LR1121 module with the same PE4259 SPDT, HP-PA-only topology and an 850–930 MHz sub-GHz band. It matches Semtech's block diagram (DS §4.7, Fig. 4-1) and follows the Semtech UM rule (§9.2) quoted under item A.
Assumes the sub-GHz band is **868 MHz**.

### A. HP PA TX path (pin 32 RFO_HP_LF → U3 RF1)

| | Current | Reference |
|---|---|---|
| Choke VR_PA → pin 32 | L3 47 nH | **68 nH high-Q**, with **200 Ω in parallel**. Semtech UM §9.2: "best practice to place a 200 Ohm resistor in parallel to the HP PA choke inductor" |
| VR_PA decoupling | C11 100 nF + C12 100 pF | **2.2 nF + 68 pF** |
| Match / harmonic filter | L4 22 nH series → C17 4.3 pF shunt → C18 47 pF DC block | pin 32 → **6.8 nH ∥ 4.3 pF** (series trap) → **15 pF** shunt → **22 nH** series → shunt (DNP pad) → **12 pF** series → **6.8 pF** shunt → RF1 |

The current network has 2 elements where the reference has 7. Expect a wrong load at the PA and weak suppression of the 2nd and 3rd harmonics at +22 dBm.

### B. RX path (pins 30 RFI_P_LF0 / 29 RFI_N_LF0 → U3 RF2). The input is differential.

| Current | Reference (lumped balun) |
|---|---|
| L5 56 nH P–N; C19 47 pF N→GND (AC-grounds N); C20 1.2 pF P→GND; C21 47 pF P→RF2 | **56 nH** P–N; **5.1 pF** N→GND; **47 nH** N→A; **1.2 pF** P→A; **1 pF** A→GND; **47 pF** A→RF2 |

The current circuit AC-grounds the N input, so it isn't a proper balun. Expect lost sensitivity.

### C. 2.4 GHz path (pin 26 RFIO_HF → J3). DS Fig. 4-1 calls this a "Harmonics Filter".

| Current | Reference |
|---|---|
| 1.3 pF shunt → 3.6 nH → 1 pF shunt → 47 pF → J3 | **1.3 pF** shunt → **3.6 nH** → **1.6 pF** shunt → **3.6 nH** (∥ DNP pad) → **0.7 pF** shunt → **33 pF** → J3 |

### D. Antenna side of the switch (U3 RFC → J4)
Reference: a π low-pass of **4.3 pF – 15 nH – 4.3 pF** at the antenna port. Current design: only C22 47 pF. Keep C22 as the DC block (PE4259 RF ports need 0 V DC) and add the π.

### E. Smaller items (reference does them, cheap)
- Switch control V1/V2: add a **100 Ω series resistor + 1 nF to GND** on each line.
- VBAT_RF (pin 2): add a **56 pF** (47 pF is fine) next to the 100 nF. My own suggestion, not from the reference: add a **10 µF** bulk cap near the LR1121. On 2 layers it will sit farther from the LDO caps, and it sees PA current pulses.
- VTCXO: the reference uses a ferrite (BLM15PG100SN1D) + 1 nF at the pin and 100 nF at the TCXO. Your 220 Ω + 10 pF coupling into XTA with XTB NC is fine. Keep it.
- Optional: low-capacitance ESD diode (RClamp1561P) on each u.FL.

### F. DC-DC inductor (L1 2.2 µH): still open
Not given in the LR1121 DS rev 2.0 or UM rev 1.2. The SX126x family that the LR11xx radio is derived from uses **15 µH**. Get the value from Semtech's LR1121 reference design BOM (semtech.com) before ordering. VREG cap C10 470 nF matches the reference.

**General:** these values were tuned on someone else's layout. Give every series and shunt position its own 0402 pad, including the DNP ones, so the network can be re-tuned with a VNA if one is available.

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
