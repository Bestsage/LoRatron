# LoRatron V2: adding the Johanson IPD (2026-11-20)

*Part: **Johanson 0900PC16J0042001E** (LCSC C19842466). Source: datasheet Rev 1.1 (`~/Downloads/IPD-0900PC16J0042001E-Rev1.1.pdf`). Checked against the netlist at commit `1cf40bb`.*

---

## 0. Decision and what it costs

**Decision (2026-11-20):** sub-GHz goes through the IPD on the **high-power PA**: RFO_HP_LF → IPD pin 1 → TX_HP pin 9 → PE4259. The Semtech discrete transmit/receive network is removed. 2.4 GHz is unchanged.

**What it costs.**
- The datasheet characterises TX_HP for 902–928 MHz only (TX_LP is the 863–870 path). The TX_HP plot still shows a good match at 868: return loss about −12 to −15 dB, with the dip centred near 1 GHz.
- So expect **~1–2 dB more loss** than the discrete network: about **+20 dBm at the u.FL** instead of ~+21, and ~0.7 dB worse receive.
- Accepted in exchange for one part instead of nine and a much simpler 2-layer RF layout.
- Johanson wasn't contacted. If you ever want exact numbers, their S-parameter file answers it (johansontechnology.com/ask-a-question).

**Pinout check.**
- The terminal table and top view (p. 3) agree with the measurement diagrams (p. 5). Those are drawn as the top view rotated 180°.
- Pin 1 is RFO_HP and pin 9 is TX_HP; pins 3/4 are RFI_P/N and pin 6 is RX; pins 5, 7, 10 are GND.

### Do this as soon as the IPDs arrive (before assembly, ideally before ordering the PCB)

The datasheet doesn't say whether the IPD has a DC path to GND. The PA bias (VR_PA ≈ 3.1 V through L3) goes straight into IPD pin 1. If pin 1 were DC-shorted to GND, the PA would get no bias, and VR_PA would be loaded down through L3.

Check one loose part with a multimeter, using fine probes under the microscope at the SPOT:

| Measure | Expected for our wiring | If not |
|---|---|---|
| Pin 1 ↔ GND (5/7/10) | open (MΩ) | needs a series DC-block cap before pin 1. Stop and tell Claude |
| Pin 3 ↔ GND, pin 4 ↔ GND | open | same: tell Claude before assembly |
| Pin 9 ↔ GND, pin 6 ↔ GND | either is fine | C18/C21 already block DC towards the PE4259 |

Johanson's ports are "impedance-matched to the Semtech chipset" and connect straight to its pins, so "open" is the likely result. This check costs 5 minutes and rules out the one failure that would kill the transmit path.

---

## 1. What changes, at a glance

**Delete (9 parts):** L4, C17, C24, L6, C25 (transmit match) and L5, C19, C20, L7 (receive balun).

**Keep unchanged:**
- L3 47 nH ∥ R7 200 Ω (VR_PA feed to pin 32) and C11/C12.
- **C18 47 pF and C21 47 pF.** They become DC blocks between the IPD and the PE4259 (3.9 Ω at 868 MHz, negligible). The PE4259 needs 0 V DC on its RF ports.
- U3 PE4259, C22, J4, and the V1/V2 control lines.

**Change:**
- **L8 9.1 nH → 0 Ω (0402)**, and **C26, C27 → DNP**.
- The IPD already contains the harmonic filter (Johanson states it meets ETSI/FCC on its own). The pads stay on the board as a spare π network.
- If a spectrum check ever shows harmonics too high, put back the original 3.3 pF / 9.1 nH / 3.3 pF.

**Add:** U5 = 0900PC16J0042001E.

### New sub-GHz chain

```
VR_PA ─ C11/C12 ─ L3 47n ∥ R7 200 ─┐
                                   IC1.32 RFO_HP_LF ── U5.1   U5.9 TX_HP ── C18 47p ── U3.1 RF1 ┐
                                   IC1.31 RFO_LP_LF    (NC)   U5.2 (NC)  U5.8 TX_LP (NC)       ├ U3.5 RFC ─ C22 47p ─ [C27 DNP / L8 0Ω / C26 DNP] ─ J4
                                   IC1.30 RFI_P ────── U5.3   U5.6 RX ───── C21 47p ── U3.3 RF2 ┘
                                   IC1.29 RFI_N ────── U5.4
                                                       U5.5, U5.7, U5.10 ── GND
```

---

## Before you start

Make a restore point:

```bash
git -C ~/Documents/Rockets/LoRa/LoRatron commit -am "RF: before Johanson IPD"
```

If it's already clean, skip this.

---

## 2. Footprint (KiCad 10, Footprint Editor)

1. **Start the footprint.**
   - Open the Footprint Editor. In the left library tree, select **`custom_footrpint`**.
   - **File › New Footprint** → name `Johanson_IPD_0900PC16J0042001E`, type **SMD**.
2. **Place pad 1.** **Place › Add Pad**, click anywhere, Esc, then double-click the pad and set:
   - Pad type **SMD**, shape **Rounded rectangle** (corner 25 %), or plain Rectangle.
   - Number **1**, position **X −0.75, Y 0.70**, size **X 0.25, Y 0.40**.
   - Layers F.Cu / F.Paste / F.Mask (the SMD default). Leave mask and paste margins at 0, i.e. take the board defaults.
3. **Make the other pads.** Select pad 1, then **Ctrl+D** (duplicate) and double-click the copy to set its number and position. Repeat for all 10:

   | Pad | Function | X | Y | Size X × Y |
   |---|---|---|---|---|
   | 1 | RFO_HP_LF | −0.75 | +0.70 | 0.25 × 0.40 |
   | 2 | RFO_LP_LF | −0.25 | +0.70 | 0.25 × 0.40 |
   | 3 | RFI_P | +0.25 | +0.70 | 0.25 × 0.40 |
   | 4 | RFI_N | +0.75 | +0.70 | 0.25 × 0.40 |
   | 5 | GND | +0.90 | 0 | **0.40 × 0.25** |
   | 6 | RX | +0.75 | −0.70 | 0.25 × 0.40 |
   | 7 | GND | +0.25 | −0.70 | 0.25 × 0.40 |
   | 8 | TX_LP | −0.25 | −0.70 | 0.25 × 0.40 |
   | 9 | TX_HP | −0.75 | −0.70 | 0.25 × 0.40 |
   | 10 | GND | −0.90 | 0 | **0.40 × 0.25** |

   (Top view, KiCad +Y = down. Pads 1–4 are the bottom row and go towards the LR1121. Pads 9, 8, 7, 6 are the top row, left to right.)
4. **Graphics:**
   - **F.Fab:** a rectangle from (−1.0, −0.8) to (1.0, 0.8). Add a short diagonal line in the bottom-left corner to mark pin 1.
   - **F.Courtyard:** a rectangle from (−1.30, −1.10) to (1.30, 1.10).
   - **F.SilkS:** a small circle (Ø 0.2) at (−1.15, 1.05), next to pad 1. Nothing under the body.
5. **Properties.** **Edit › Footprint Properties**: Reference `U**`, Value `0900PC16J0042001E`, attribute **SMD**.
6. **Check and save.**
   - **Inspect › Footprint Checker** should show no errors.
   - **File › Save** into `custom_footrpint`.

> I derived this land pattern from the part's terminal dimensions (0.235 × 0.24 mm, 0.5 mm pitch, 2.0 × 1.6 mm body). The pads reach ~0.1 mm beyond the body edge for the solder fillet. Johanson's own pattern is only in their reference package.

---

## 3. Symbol (Symbol Editor)

1. **Create the library.** **File › New Library** → **Project** table → save as `custom_symbols/Johanson_IPD.kicad_sym`.
2. **Create the symbol.** Select the new library → **File › New Symbol** → name `0900PC16J0042001E`, reference designator `U`. Leave the other options at their defaults.
3. **Pins.** Use **Place › Pin**, all **electrical type Passive**, length 2.54 mm, on a 2.54 mm grid:

   | Side | Pin | Name |
   |---|---|---|
   | Left, pointing right | 1 | RFO_HP_LF |
   | | 2 | RFO_LP_LF |
   | | 3 | RFI_P |
   | | 4 | RFI_N |
   | Right, pointing left | 9 | TX_HP |
   | | 8 | TX_LP |
   | | 6 | RX |
   | Bottom, pointing up | 5 | GND |
   | | 7 | GND |
   | | 10 | GND |

   For the GND pins, either place three separate pins, or stack them: put all three on the same spot and make 7 and 10 invisible. Three visible pins is simpler to wire.
4. **Body.** Draw a rectangle (**Place › Rectangle**) around the pins, background fill.
5. **Fields.** **File › Symbol Properties**:

   | Field | Value |
   |---|---|
   | Footprint | `custom_footrpint:Johanson_IPD_0900PC16J0042001E` |
   | Datasheet | `https://www.johansontechnology.com/products/other/ceramic-passive-component/0900pc16j0042001e/` |
   | Description | `Impedance-matched IPD for Semtech LR11xx, 863-870 / 902-928 MHz` |
   | Manufacturer | `Johanson Technology` |
   | MPN | `0900PC16J0042001E` |
   | LCSC | `C19842466` |

6. **Save.**

---

## 4. Schematic edits (RF sheet)

1. **Delete parts.** Delete **L4, C17, C24, L6, C25, L5, C19, C20, L7** and the wires that only served them. Leave GND symbols that other parts still use.
2. **Place U5.** **Place › Add Symbol (A)** → `Johanson_IPD:0900PC16J0042001E`.
   - Put it between IC1's RF pins and the PE4259, chip-side pins (left) towards IC1.
   - Set the reference to **U5** (U1–U4 are taken).
3. **Wire (W) or use labels.**
   - **U5.1** → the IC1.32 RFO_HP_LF node, the one that also has **L3.2 and R7.2**.
   - **U5.3** → **IC1.30** RFI_P.
   - **U5.4** → **IC1.29** RFI_N.
   - **U5.9** TX_HP → **C18 pin 1**. C18 pin 2 stays on U3.1 RF1.
   - **U5.6** RX → **C21 pin 1**. C21 pin 2 stays on U3.3 RF2.
   - **U5.5, U5.7, U5.10** → GND.
4. **No-connect flags (Q).** Put them on **U5.2** and **U5.8**. IC1.31 already has one.
5. **Values and DNP.**
   - **L8**: Value `0R`. Keep the 0402 footprint and buy a 0 Ω 0402 resistor.
   - **C26, C27**: in Symbol Properties tick **Do not populate**.
6. **Check.** **Tools › Annotate** (nothing should change), then **Inspect › ERC**. Target: 0 violations.
7. **Hand over.** **Save**, **close KiCad completely**, and tell Claude. Claude exports the netlist and checks every connection above.

---

## 5. Layout notes (for the PCB step)

**Placement against the LR1121:**
- The LR1121's top edge, read left to right, is pads 32, 31, 30, 29 (x = −1.75 … −0.25 mm from the IC centre).
- The IPD's pads 1–4 are in the same order at the same pitch.
- Place U5 **unrotated, directly above IC1, centred at x = −1.0 mm** relative to IC1. Pads 1–4 then face pads 32–29 one-to-one, with ~0.4 mm straight stubs.

**Connections:**
- **L3/R7 feed:** tap the pin-32 stub right at the pad and run the feed away from the RF path.
- **Antenna side** (pads 9, 6 on the far edge) → C18/C21 → PE4259. Keep it short, using 50 Ω CPWG (1.0 mm / 0.15 mm gap); neck down only at the pads.
- **GND pads 5, 7, 10:** one via each, right at the pad. B.Cu solid under the IPD/LR1121/switch.

**2.4 GHz:**
- Pin 26 sits ~1 mm to the right of the IPD.
- Route the 2.4 GHz network away to the right and put GND vias between the two RF areas.

**Assembly:**
- Reflow only, SAC305 paste.
- Keep the IPDs in a sealed bag; the datasheet says use within 1 week of opening.

---

## 6. BOM / ordering

| Ref | Part | Note |
|---|---|---|
| U5 | Johanson 0900PC16J0042001E | **LCSC C19842466 is out of stock as of 2026-11-20.** Order from **DigiKey 712-0900PC16J0042001ECT-ND** (cut tape, ~281k in stock, ~$0.72 at qty 1) or Mouser 609-0900PC16J004201E. Re-check the stock before ordering. **Order 4–5**: 1 for the multimeter check, spares for losses |
| L8 | 0 Ω 0402 | was 9.1 nH |
| C26, C27 | DNP | keep the pads |
| L4, L6, L5, L7, C17, C19, C20, C24, C25 | removed | drop from the RF MPN list in `LoRatron_V2_RF_manual_steps.md` |
