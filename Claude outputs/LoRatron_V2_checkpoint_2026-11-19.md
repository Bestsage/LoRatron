# LoRatron V2: checkpoint (2026-11-19)

*State at commit `bda832d` ("DC-DC corrigé with claude code") on `main`. Schematic ERC: **0 violations**, 65 components. PCB not started (`loratron.kicad_pcb` is still the V1 4-layer board).*

---

## 1. Project and ground rules

- **What:** compact LoRa telemetry board for the EPFL Rocket Team (Space Race VII). It's a non-flight-critical add-on, mounted away from the main avionics.
- **V2 goal:** swap the ESP32-S3-WROOM-1U for an **ESP32-S3-MINI-1U-N8** and make a new **2-layer, 30 × 60 mm** board with the existing **4 × M2.5** mounting holes. On 2 layers the LR1121 can no longer sit under the MCU. Fix the hardware so it follows the datasheets and reference designs. Firmware is out of scope for now.
- **Tools:** KiCad 10.0.8 (Flatpak, Linux). Project: `~/Documents/Rockets/LoRa/LoRatron/`. Work directly on **`main`**.
- **Assembly:** at **the SPOT (EPFL)**, where reflow is available (stencil + hot plate). The MINI-1U and the LR1121 are LGA/QFN parts and must be reflowed.
- **Ground rules for Claude sessions:**
  - The user commits. **No Claude attribution in commits.**
  - **KiCad must be fully closed** before any direct file edit: no `~*.lck` in the project folder, no `/app/bin/kicad` process. Check the mtime too, and back up first (`*.bak_before_<what>`).
  - Be careful with schematic changes, keep existing components, and **respect the user's schematic layout**. The user prefers to make topology changes by hand in KiCad, with step-by-step guidance. Claude checks the result through the netlist.
  - Running kicad-cli: `flatpak run --filesystem=/tmp/claude-1000 --command=kicad-cli org.kicad.KiCad …`. Without `--filesystem`, the Flatpak sandbox can't see the host `/tmp`.

---

## 2. Main sheet: MCU swap (done ✓)

- **U4 = ESP32-S3-MINI-1U-N8.** Stock symbol `RF_Module:ESP32-S3-MINI-1U`, footprint `RF_Module:ESP32-S2-MINI-1U` (same 15.4 × 15.4 mm LGA, 65 pads plus a 9-segment center pad 61).
- The **WROOM (IC2) was removed.** The custom MINI-1U-N8 symbol, footprint and 3D files were never added to the library tables and aren't used.
- **Same GPIOs as V1, only the module pins changed:**

| Net | GPIO | MINI pin |
|---|---|---|
| +3.3V / GND | 3V3 / GND | 3 / 1 (all 24 GND pins joined) |
| /EN (R1 10 k + C3 1 µF, SW1) | EN | 45 |
| BOOT (R2 10 k, SW2) | IO0 | 4 |
| LED (R6 470 Ω → D3) | IO2 | 6 |
| /USB_N, /USB_P | IO19, IO20 | 23, 24 |
| NSS, MOSI, SCLK, MISO | IO10–IO13 | 14–17 |
| BUSY | IO14 | 18 |
| LORA_RST | IO21 | 25 |
| LORA_IRQ | IO47 | 27 |
| /TXDO, /RXDO (J2) | TXD0, RXD0 | 39, 40 |

- Unused MINI pins have no-connect flags. The strapping pins IO3/IO45/IO46 are left floating, which is fine.
- **Fixes made this session:**
  - `LORA_IRQ` wasn't reaching U4 pin 27. Fixed with a global label at U4.27.
  - IC1's Footprint field was missing its library nickname. It's now `custom_footrpint:QFN50P500X500X100-33N-D`, in the schematic and in `custom_symbols/LR1121IMLTRT.kicad_sym`.
  - The library footprint's **LR1121 center pad (pad 33)** had paste ratio `-25` (= −2500 %, no paste). It's now `-0.1` (−10 %). **This pad must be soldered.**
- **Power, unchanged:** VBUS / +5V (J2) → D1/D2 B5819W → TLV1117LV33 (U1) → +3.3V, with C1/C4/C6 22 µF and C2/C5/C7 100 nF. USB-C J1 (GCT USB4105) with USBLC6-2SC6 ESD protection and CC 5.1 k pull-downs.

---

## 3. RF sheet: current state (Semtech discrete design, done ✓)

The source of truth is Semtech's own LR1121 reference packages, from semtech.com (in `~/Downloads/`):
- `LR1121DVK1TxKS_868_915MHz_DevKit_prod_folders.zip`: **LR1121MB1DIS e655** (868/915 MHz, 0402 parts).
- `61079821.LR1121MB2THDAS_868_915_HP_e742v01a_production_folder.zip`: **LR1121MB2THDAS e742** (high-power-only, SPDT switch, TCXO, 0201 parts).

The LR1121 datasheet and user manual contain **no matching values** (only "Matching Network" boxes). V1's RF values had never been checked against a reference. The Waveshare Core1121 values were considered first and then dropped in favour of Semtech's.

### Current topology (checked against the netlist)

| Block | Chain |
|---|---|
| VR_PA bias | VR_PA (C11 2.2 nF, C12 47 pF) → **L3 47 nH ∥ R7 200 Ω** → pin 32 |
| Sub-GHz transmit (pin 32 → U3 RF1) | **L4 3.3 nH ∥ C17 1.2 pF** → C24 6.8 pF to GND → L6 8.2 nH → C18 47 pF → C25 1.8 pF to GND → U3 RF1 |
| Sub-GHz receive balun (pins 30 P / 29 N → U3 RF2) | L5 22 nH between P and N · C19 1.2 pF N→GND · C20 1.5 pF P→A · L7 47 nH N→A · C21 47 pF A→U3 RF2 |
| Antenna low-pass (U3 RFC → J4) | U3 RFC → C22 47 pF (DC block) → C27 3.3 pF to GND → L8 9.1 nH → C26 3.3 pF to GND → J4 |
| 2.4 GHz (pin 26 → J3) | C14 1.3 pF to GND → L2 3.6 nH → C15 1.6 pF to GND → L9 3.6 nH → C29 0.7 pF to GND → C16 33 pF → J3 |
| DC-DC | DCC_SW → **L1 10 µH (TDK MLZ1608N100LT000, 0603)** → VREG, C10 470 nF |
| Supply decoupling | C8/C9 100 nF (VBAT_RF / VBAT) · **C30 47 pF** · **C28 10 µF (0603)** |
| TCXO | Y1 ECS-TXO-32CSMV (pin 1 = GND, correct) powered from VTCXO with C23 100 nF; OSC_OUT → R5 220 Ω → C13 10 pF → XTA; XTB NC |
| RF switch | U3 PE4259: DIO5 (IC1.20) → net V1 → U3.4; DIO6 (IC1.19) → net V2 → U3.6 |

**Deliberately left out (optional):** the ferrite + 470 pF on VTCXO, the 100 Ω + 1 nF on V1/V2, and the empty (DNP) pads.

**Parts to buy for the RF sheet:**
- Inductors: Murata **LQW15AN** wirewound (0402), not generic multilayer.
- Capacitors: **C0G** (Murata GRM1555C1H…).
- L1: TDK MLZ1608N100LT000.
- Full MPN list in `LoRatron_V2_RF_manual_steps.md`.

---

## 4. Decision: switch sub-GHz to the Johanson IPD (to do)

**Part:** Johanson **0900PC16J0042001E**, an impedance-matched IPD for the Semtech **LR1110/LR1120/LR1121**.
- **Package:** 2.0 × 1.6 mm, 10 pads, bottom-only terminations, so it needs reflow.
- **Lifecycle:** Active (released Feb 2022).
- **Pins:**
  - Chip side: 1 RFO_HP_LF, 2 RFO_LP_LF, 3 RFI_P, 4 RFI_N.
  - Antenna side (50 Ω): 9 TX_HP, 8 TX_LP, 6 RX.
  - GND: 5, 7, 10.
- **Specs:** 863–870 and 902–928 MHz. Transmit loss 1.0 dB typ (1.4 max), receive loss 1.7 dB typ (2.3 max), return loss ≥ 10 dB. Harmonics ≥ 33–38 dB down (2nd–4th at 868). 2 W CW.
- **Stock:** LCSC **C19842466** (129 in stock, ~$1). DigiKey lists it with a 15–17-week manufacturer lead time.
- **Cost vs the discrete design:** about −0.5 dB transmit power and −0.7 dB receive sensitivity. Small.

**Schematic change plan:**
- **Removed:** L4, C17, C24, L6, C25 (transmit filter) and L5, C19, C20, L7 (receive balun).
- **Kept:**
  - L3 47 nH + R7 200 Ω (PA bias) and C11/C12 (VR_PA).
  - C18 and C21 as 47 pF DC blocks between the IPD and the PE4259.
  - U3 PE4259.
- **IPD connections:**
  - IPD.1 → IC1.32
  - IPD.3 → IC1.30, IPD.4 → IC1.29
  - IPD.9 → C18 → U3 RF1, IPD.6 → C21 → U3 RF2
  - IPD.2 → IC1.31 (unused LP PA) and IPD.8 TX_LP: leave unconnected, or follow Johanson's reference.
- **Antenna low-pass (C27/L8/C26):** becomes optional, since the IPD includes the harmonic filter. Keep the pads, or drop it.
- **Still needed:**
  - [ ] Create the KiCad symbol and footprint (pads from the datasheet: L 2.00, W 1.60, pad a 0.235 × b 0.24, pitch p 0.5, g 0.265).
  - [ ] **Request Johanson's full reference design** (johansontechnology.com/ask-a-question). The datasheet doesn't give the land pattern, whether the external PA choke is still needed, or whether the IPD blocks DC on its outputs.

---

## 5. 2.4 GHz: keep as is, no amplifier

- **The 2.4 GHz port is already 50 Ω.** The LR1121 datasheet says RFIO_HF is matched to 50 Ω internally, so the 5-part network is a harmonic filter. No LR1121-specific 2.4 GHz IPD exists: Johanson's 2000PC15C0040001E is for the LR1110's Wi-Fi scan and GNSS receive paths. The generic Johanson 2450LP14B100 low-pass could replace the 5 parts, but it isn't stocked at LCSC and Semtech's network is already correct.
- **Link-budget comparison:** LR1121 sensitivity from the datasheet at 125 kHz bandwidth, 2 dBi antenna on the rocket, free space, 20 dB margin. Use these for comparison only.

| Setup | Ground antenna | SF7 (5.5 kbps) | SF9 (1.8 kbps) | SF12 (0.3 kbps) |
|---|---|---|---|---|
| 868 MHz, +21 dBm conducted | omni 2 dBi | ~87 km | ~165 km | ~430 km |
| 2.4 GHz, 10 dBm EIRP | omni 2 dBi | ~3 km | ~6 km | ~16 km |
| 2.4 GHz, 10 dBm EIRP | patch 14 dBi | ~12 km | ~24 km | ~65 km |
| 2.4 GHz, 20 dBm EIRP (with PA) | omni 2 dBi | ~10 km | ~19 km | ~52 km |

- **Why 868 MHz comes out ahead:** about 9 dB less path loss, about 6.5 dB better LR1121 sensitivity at sub-GHz, and more allowed power at 869.4–869.65 MHz (500 mW ERP, 10 % duty cycle).
- **Where 2.4 GHz is useful:** continuous, higher-rate telemetry at short to medium range, at ≤ 10 dBm EIRP. Use a directional ground antenna (patch/helical) for range.
- **Decision:** no 2.4 GHz amplifier.

**Options evaluated and rejected:**
- **Johanson 0868BM15C0001:** a balun matched to TI CC110x/CC1101. Wrong impedance and architecture for the LR1121, and 2.1 dB loss.
- **Skyworks AS179-92LF:** a functional equivalent of the PE4259, so no benefit.
- **AT2401C (RFX2401C clone):** a 2.4 GHz amplifier. It adds parts, current and control lines for no usable gain under the limits above.

---

## 6. Transmit power and current

| Path | LR1121 max | At the u.FL (estimate) | Transmit current |
|---|---|---|---|
| Sub-GHz HP PA | +22 dBm | ~+21 dBm (discrete), ~+20.5 dBm (with IPD) | ~118 mA at +22 dBm |
| 2.4 GHz HF PA | +13 dBm | ~+12–13 dBm | ~26 mA |

- **+22 dBm needs VBAT ≥ 3.3 V** (VR_PA about 3.1 V, plus 200 mV dropout). The 3.3 V LDO is right at that edge, so expect +20–21 dBm if the rail sags. This is why C28 (10 µF) is next to the LR1121.
- **Firmware for full sub-GHz power:**
  - High-power PA.
  - PA supply from VBAT.
  - TxPower 22.
  - PaDutyCycle 4.
  - HpMax 7.
- **Band plan:** use **869.4–869.65 MHz (e.g. 869.525 MHz)** for full power at 868 MHz. 915 MHz is not an EU band. On 2.4 GHz, set the conducted power to about +8 dBm with a 2 dBi antenna (≈ 10 dBm EIRP).

---

## 7. 2-layer layout plan (next big step)

- **Board:** 30 × 60 mm, 2 layers, 1.6 mm FR-4, 4 × M2.5 holes. **Hole positions still to be decided** (corners at 3.5 mm in, or a given pattern).
- **Start from the existing `loratron.kicad_pcb`:**
  1. Strip the V1 routing, zones and outline.
  2. Board Setup: 2 layers.
  3. Update PCB from Schematic (F8).
  4. **Delete the J3/J4 u.FL rule areas.** They're stored in absolute coordinates and won't follow the footprints.
- **RF lines:** **CPWG 1.0 mm track / 0.15 mm gap** on 1.6 mm (≈ 50 Ω; check with the KiCad calculator or JLC's tool). The old 0.35 mm traces would be ≈ 69 Ω on 2 layers. Keep RF runs very short and put the u.FLs right at the end of each network.
- **B.Cu stays solid GND** under the LR1121, the RF networks, the IPD, the TCXO and the switch. Add a via fence every ≤ 2–3 mm along the RF lines, and give each shunt part its own GND via.
- **Placement along the 60 mm:**
  - One short edge: J3/J4 + LR1121 + IPD/RF.
  - Middle: MINI-1U.
  - Far short edge: USB-C, LDO, D1/D2, J2, buttons, LED.
  - SPI runs on F.Cu between the blocks, away from the RF.
- **LR1121:**
  - Center pad 33: 3 × 3 vias (0.3 mm drill), paste −10 %.
  - DC-DC loop (DCC_SW–L1–VREG, pins 12–14) tight and away from the TCXO and RF.
  - TCXO right at pins 3–4.
  - C8/C9/C28/C30 next to pins 2/15.
  - IPD as close to pins 29–32 as Johanson's layout shows.
- **MINI-1U:** center GND pads get vias and **are soldered** (unlike the WROOM in V1). The module's own u.FL is unused.
- **LDO (SOT-223):** give the tab some copper (about 0.3–0.6 W).
- **Assembly:** a single side if possible, so it's one reflow pass. USB-C shield legs, J2 and the buttons by iron.

---

## 8. Open items

1. **IPD:** request Johanson's reference design, create the symbol and footprint, and update the RF sheet (section 4).
2. **Mounting hole positions** for 30 × 60.
3. **PCB layout** (section 7), then DRC, Gerbers and a JLC 2-layer quote (+ stencil).
4. **BOM:** add MPNs for the RF parts (LQW15AN, GRM1555 C0G, MLZ1608, PE4259, IPD, TCXO). The kicad-happy LCSC search works without a key. DigiKey/Mouser searches need `DIGIKEY_CLIENT_ID` / `MOUSER_SEARCH_API_KEY`, which aren't set.
5. **Firmware (later):**
   - TCXO supply: VTCXO 1.8 V in V1 notes. The ECS-TXO-32CSMV minimum is 1.7 V, so a higher setting such as 3.0 V gives more margin.
   - RF switch table for DIO5/DIO6 (check against the PE4259 truth table).
   - The N8 has **no PSRAM**.
   - PA settings from section 6.

---

## 9. Files

| File | What |
|---|---|
| `Claude outputs/LoRatron_handout_2026-11-19.md` | V1 handout (4-layer, WROOM). Its layout notes are V1-only |
| `Claude outputs/LoRatron_V2_schematic_RF_review_2026-11-19.md` | MINI swap review, RF comparison vs Semtech, 2-layer notes |
| `Claude outputs/LoRatron_V2_RF_manual_steps.md` | Step-by-step RF edits in KiCad with MPNs |
| `Claude outputs/LoRatron_V2_checkpoint_2026-11-19.md` | This document |
| `~/Downloads/LR1121DVK1TxKS_…zip`, `~/Downloads/61079821.LR1121MB2THDAS_…zip` | Semtech reference designs (schematic, BOM, Altium layout, Gerbers) |
| `~/Downloads/IPD-0900PC16J0042001E-Rev1.1.pdf`, `~/Downloads/HwkBwf3z.pdf` | Johanson IPD datasheet and product sheet |
| `~/Downloads/LR1121_data_sheet_V1_1.pdf` | LR1121 datasheet Rev 1.1 (no matching values) |
