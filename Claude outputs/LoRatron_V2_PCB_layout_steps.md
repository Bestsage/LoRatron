# LoRatron V2: PCB layout steps (2026-11-20)

*Starting point: commit `1adc8b9`. The schematic has the Johanson IPD (57 parts, ERC 0). `loratron.kicad_pcb` is still the V1 4-layer, 36 × 33 mm board.*

## Decisions

- **Board:** 30 × 60 mm, 2 layers, 1.6 mm FR-4 (JLC). Drawn in landscape: **X 100 → 160, Y 50 → 80**.
- **Mounting holes:** 4 × M2.5 (H1–H4), centres **3.5 mm in from each edge**, so a 53 × 23 mm pattern:
  - H1 (103.5, 53.5)
  - H2 (156.5, 53.5)
  - H3 (103.5, 76.5)
  - H4 (156.5, 76.5)
- **Sides:**
  - Bottom-side parts are allowed, **but not in the RF area**. LR1121, IPD (U5), PE4259 (U3), TCXO (Y1), J3/J4 and all RF passives go on **top**.
  - B.Cu under them stays one unbroken GND plane.
  - Bottom parts are fine in the MCU/power area if space runs out.
- **Placement along the 60 mm:**
  - Left short edge (x ≈ 100): J3/J4 u.FL + LR1121 + IPD + switch + 2.4 GHz filter.
  - Middle: U4 ESP32-S3-MINI-1U.
  - Right short edge (x ≈ 160): USB-C J1 at the edge, U1 LDO, D1/D2, J2, SW1/SW2, D3.
- **50 Ω RF lines:** **CPWG 1.1 mm track / 0.2 mm gap to the GND pour**, with B.Cu GND underneath.
  - Calculated: 51.6–52.5 Ω for εr 4.4–4.6, 1.55 mm dielectric.
  - The 0.2 mm gap equals the normal pour clearance, so no special zone rules are needed.
  - Alternative: 1.0 mm / 0.15 mm ≈ 50 Ω, but that needs a tighter clearance on the pour.

---

## Phase 1: Strip V1 and set up the 2-layer board

1. **Open the board.** Open the project and the PCB Editor (`loratron.kicad_pcb`).
2. **Delete the V1 copper and outline.**
   - Open **Edit › Global Deletions…** and tick:
     - **Zones**
     - **Rule areas** (this also removes the old J3/J4 keepouts, which are fixed coordinates)
     - **Tracks**
     - **Vias**
     - **Board outline** (Edge.Cuts)
   - Tick "locked items" too, if the dialog has that option.
   - **Untick Footprints, Text and other Graphics.** Click **OK**.
3. **Set 2 copper layers.**
   - **File › Board Setup › Board Stackup › Physical Stackup** → **Copper layers: 2**. Board thickness stays **1.6 mm**. Click **OK**.
   - If KiCad warns about removing In1/In2, accept. They're empty now.
4. **Draw the new outline.**
   - Choose **Edge.Cuts** in the layer dropdown (top toolbar).
   - Use **Draw Rectangle**: click, move the mouse, click again.
   - Press **Esc**, then double-click the rectangle's edge and set **Start X 100, Y 50 / End X 160, Y 80**, line width 0.1. Click **OK**.
5. **Move the mounting holes.** Double-click **H1, H2, H3, H4** in turn and set their **Position X/Y** to the values in the list above.
6. **Update the board from the schematic.**
   - Open **Tools › Update PCB from Schematic** (F8).
   - Leave "Re-link footprints…by reference" **unticked**.
   - **Tick** "Delete footprints with no symbols" and "Replace footprints with those specified in the schematic".
   - Click **Update PCB**.
   - New footprints (U4 MINI, U5 IPD and others) arrive stuck to the cursor. Click to drop them **outside** the board, e.g. below it.
7. **Save, close KiCad, and tell Claude.** Claude checks the following in the file:
   - the outline
   - the holes
   - the layer count
   - that nothing from V1 copper is left
   - that the footprints match the 57-part netlist
   - the design rules (Claude then lists what to set for JLC 2-layer)

## Phase 1 result (checked 2026-11-20, commit `bface37`)

- 2 copper layers; outline (100,50)→(160,80); no copper left.
- H1–H4 at 3.5 mm from the edges.
- 57 footprints, matching the netlist.
- All parts on F.Cu.
- Design rules are already JLC-safe. To do: add **1.1 mm** to the pre-defined track widths.

## Phase 2: RF corner placement (paused 2026-11-20, positions not computed yet)

Working plan so far. Not final; the exact coordinates still need the collision check and a rendered preview.

**Orientation:**
- **IC1 at about (117.5, 65), rotated 90° CCW.**
  - RF pins (25–32) face the **left** edge.
  - Top edge: SPI + V1/V2 (pins 17–24).
  - Bottom edge: VR_PA, VBAT_RF, VTCXO, XTA, NRESET (pins 1–8).
  - Right edge: IRQ, DC-DC, VBAT (pins 9–16).
- **U4 MINI, rotated 0°, right of IC1** (courtyard from x ≈ 124.5). Its LoRa pins are at its bottom-left corner. Power/USB-C go on the right edge.

**Sub-GHz chain** (left, all at y ≈ 65–67):
- **U5 IPD** at about (113.25, 66.0), rot 90. Pads 1–4 face IC1 pins 32–29 with 0.45 mm gaps.
- **C18/C21** at about x 111.1, y 66.85 / 65.15. They're spread 1.7 mm apart so a GND via for U3 pin 2 fits between them.
- **U3** at about (108.55, 66.0), rot 180. RF1/RF2 face the IPD; RFC, V1 and V2 face left.
- **C22** next, then **L8** turning down to **J4**, which sits about 3–4 mm in from the left edge, above H3.
- **C26/C27** on the nodes, outside the J4 courtyard.
- **L3 ∥ R7** feed: tapped from the pin-32 stub, going down below the IPD. C11/C12 sit below them.

**2.4 GHz chain:**
- Leave pin 26 to the left, C14 at the node, then go **up**: L2 → C15 → L9 → C29 → C16 in a vertical column at x ≈ 113.4.
- **J3** at about (113.4, 54), above the column. All of this stays away from the sub-GHz chain.

**Routing topology (decided):**
- **V1/V2:** V1 and V2 are on opposite sides of RFC at U3, so one RF crossing is unavoidable.
  - **V1 hops under the RFC line on B.Cu** (2 vias, ~1.5 mm), right next to U3. It's the only B.Cu trace in the RF area.
  - Then V1 and V2 run together on F.Cu **around the bottom and the right side of the IC1 cluster**, and enter pins 20/19 from the top-right.
- **IRQ, NRESET and BUSY go to B.Cu right at IC1** (via next to the pin) and run on B.Cu to U4.
  - This avoids crossing the V1/V2 ring, the SPI lines and the USB pair.
  - The LR1121 and ESP32 pin orders don't match, so BUSY and the SCLK/MOSI pair would cross anyway.
- **SPI (NSS/SCLK/MOSI/MISO) on F.Cu:** they leave the top of IC1, run right above the V1/V2 entry, then down into U4's bottom-left corner.
  - SCLK and MOSI cross once. Fix with a hop, or by swapping IO11/IO12 in the schematic (firmware pin map only).
- **+3.3V crosses the V1/V2 ring once, on B.Cu.** Inside the ring it feeds pin 15 (C9 100 nF + C28 10 µF) and pin 2 (C30 47 pF + C8 100 nF).
- **TCXO Y1** below IC1, around (118.6, 72). The XTA chain (C13 → R5) runs horizontally between IC1 and Y1; VTCXO goes straight down from pin 3.
- **DC-DC:** L1 (vertical) right next to pins 14/12, C10 right of L1.

---

## Phase 2a: RF corner placement (computed 2026-11-20)

Checked by script:
- no courtyard overlaps
- every pad-to-pad gap between different nets ≥ 0.2 mm
- nothing within 0.3 mm of the edge, nothing within 0.3 mm of a hole pad
- all planned trace paths have room

Preview: `LoRatron_V2_RF_corner_preview.png`. Red = RF, blue = signals, orange = +3.3V, grey = GND, magenta = courtyards.

### Positions

Double-click each part and type **Position X, Position Y, Orientation**. KiCad may show 270° as −90°.

| Ref | X | Y | Rot | Role |
|---|---|---|---|---|
| IC1 | 117.5 | 65.0 | 90 | LR1121, RF pins face left |
| U5 | 113.25 | 66.0 | 90 | IPD; pads 1–4 face IC1 pins 32–29 |
| C18 | 111.1 | 66.85 | 0 | TX DC block |
| C21 | 111.1 | 65.15 | 180 | RX DC block |
| U3 | 108.55 | 66.0 | 180 | PE4259 |
| C22 | 105.05 | 66.0 | 180 | antenna DC block |
| C27 | 102.4 | 66.0 | 0 | DNP shunt |
| L8 | 103.6 | 67.6 | 90 | 0 Ω |
| C26 | 105.1 | 68.15 | 180 | DNP shunt |
| J4 | 103.6 | 71.2 | 270 | u.FL sub-GHz, signal pad up |
| C14 | 112.3 | 63.75 | 180 | 2.4 GHz filter |
| L2 | 113.4 | 62.3 | 270 | 2.4 GHz filter |
| C15 | 112.0 | 61.8 | 180 | 2.4 GHz filter |
| L9 | 113.4 | 60.25 | 270 | 2.4 GHz filter |
| C29 | 112.0 | 59.75 | 180 | 2.4 GHz filter |
| C16 | 113.4 | 58.2 | 90 | 2.4 GHz DC block |
| J3 | 113.4 | 54.0 | 90 | u.FL 2.4 GHz, signal pad down |
| L3 | 114.5 | 68.6 | 180 | PA choke (VR_PA → pin 32) |
| R7 | 114.5 | 69.6 | 180 | in parallel with L3 |
| C12 | 114.9 | 71.1 | 270 | VR_PA 47 pF |
| C11 | 113.85 | 71.1 | 270 | VR_PA 2.2 nF |
| C30 | 116.15 | 69.8 | 90 | VBAT_RF 47 pF |
| C8 | 116.3 | 71.6 | 180 | VBAT_RF 100 nF (on the +3.3V feed) |
| C23 | 117.7 | 70.6 | 0 | VTCXO 100 nF |
| C13 | 119.3 | 69.3 | 0 | XTA 10 pF |
| R5 | 121.15 | 69.3 | 180 | OSC_OUT 220 Ω |
| Y1 | 120.0 | 73.3 | 0 | TCXO |
| L1 | 121.55 | 64.75 | 270 | DC-DC 10 µH |
| C10 | 121.55 | 67.15 | 90 | VREG 470 nF |
| C9 | 121.75 | 62.75 | 180 | VBAT 100 nF |
| C28 | 123.45 | 63.3 | 90 | 10 µF bulk |

**Keep x > 125.9 free for U4.** The V1/V2 lines and the +3.3V feed run up the right side at x ≈ 124.2–125.6.

### Vias to place

All vias are 0.6 / 0.3 mm.

| Via at | Net | Purpose |
|---|---|---|
| (106.45, 64.55) and (106.45, 67.45) | V1 | B.Cu hop under the RFC line, between U3 and C22 |
| (114.3, 62.4) | BUSY | from pin 25, to B.Cu |
| (118.25, 68.55) | LORA_RST | straight under pin 6, to B.Cu |
| (120.55, 67.55) | LORA_IRQ | from pin 9, to B.Cu |
| (110.62, 66.0) | GND | U3 pin 2 + IPD pad 7, between C18 and C21 |
| (113.6, 64.4) | GND | IPD pad 5; also fences the 2.4 GHz node from the sub-GHz node |
| (113.25, 67.7) | GND | IPD pad 10 |
| one per GND pad | GND | C14/C15/C29 (left of each), C11/C12/C30/C8/C23/C26/C27/C9/C10/C28, U3, J3/J4 GND pads, Y1 GND pads |
| 3 × 3 grid | GND | IC1 centre pad (0.3 mm drill) |

### Trace paths

All RF runs in the corner are < 2 mm. Use **pad-width traces (≈ 0.5 mm)** for them; 50 Ω width only matters on longer lines.

**Sub-GHz chain:**
- IC1 32→29 ↔ U5 1–4: straight 0.45 mm stubs.
- U5 9 → C18 → U3 RF1; U5 6 → C21 → U3 RF2.
- U3 RFC → C22 → node at y 66.0. From the node: C27 to the left, L8 down. L8 → J4 signal pad, with C26 on that node.

**2.4 GHz chain:**
- Pin 26 → left 1.5 mm to C14 at y 63.75.
- Then up the column L2 → L9 → C16 → J3, with C15/C29 hanging left.

**PA feed:**
- Tap the pin-32 stub at x ≈ 114.2 and run down to the left pads of L3/R7 (RFO_HP).
- Pin 1 → diagonal down-left to the right pads of L3/R7 (VR_PA) → down to C12, then left to C11.

**Bottom of IC1** (0.2 mm traces):
- Pin 2 straight down to C30 top.
- **+3.3V feed** comes up at x ≈ 115.55, between R7/C12 and C30, into the C30 top pad. C8 sits on this feed.
- Pin 3 VTCXO: down to y 69.9, right to x 118.3, down to the Y1 VTCXO pad; C23 sits on it.
- Pin 4 XTA: down to y 69.3, right to C13 → R5 → Y1 OSC_OUT pad.

**Right side of IC1:**
- Pin 14 → L1 top pad; pin 12 → L1 bottom pad → C10.
- Pin 15 → C9 left pad.
- C9 +3.3V → over the top of C9 at y ≈ 61.9 → C28 top pad.

**V1/V2 ring:**
- V2 leaves U3 pin 6 and goes down at x ≈ 107.3. V1 goes via the hop and down at x 106.45.
- Both run right along y ≈ 77.2 / 78.0 (V2 inner), up the right side at x ≈ 124.9 / 125.6, then left along y ≈ 61.0 / 60.5.
- They drop into pin 19 (V2) and pin 20 (V1).

**+3.3V bus:**
- From C8, down x 115.55 to y ≈ 76.2, right to x ≈ 124.2, up to C28.
- It enters from the power side through one B.Cu hop under the V1/V2 ring.

**SPI:**
- Pins 21–24 go straight up and turn right at y ≈ 60.0 / 59.5 / 59.0 / 58.5 (MISO lowest, NSS highest).
- They pass above the V1/V2 lines, then go on to U4.

---

## Phase 2a check (2026-11-21, commit `7544b50`)

DRC: 1 clearance error (C13), 8 J1 hole-clearance errors (inherent to the USB4105 footprint, expected exclusions), dangling GND vias (expected, no pour yet), 3 mounting-hole mismatches.

Fixes to make:
1. **C13 is at rot 180, the table says 0.** Set it to **0**. Delete the 5 `Net-(C13-Pad2)` segments and the XTA segments right of (117.815, 68.715). Re-route XTA from (117.815, 68.715) to the C13 **left** pad, and C13 right pad → R5 left pad (straight, 0.3 mm). This clears the 0.125 mm clearance error.
2. **Via at (106.45, 67.45) is on V2; it must be V1's landing via.** Delete it and the V2 segment (107.25, 66.65)→(106.45, 67.45). V1: B.Cu from the via at (106.45, 64.55) straight down to a new via at (106.45, 67.45), then F.Cu down x 106.45. V2: from U3 pin 6 go to x 107.3 and straight down on F.Cu.
3. **RFO_HP tap missing.** Connect the pin-32 stub at (114.2, 66.75) straight down to (114.2, 68.3) then to L3 pad 2 (114.015, 68.6), 0.3 mm.
4. **U5 pad 7 (GND) is floating.** Track (112.55, 65.75) → (112.2, 65.75) → (111.95, 66.0) → GND via (110.62, 66.0), 0.25 mm.
5. **IC1 pin 13 (GND) is boxed in by the DC-DC traces.** Add a 0.25 mm stub from pin 13 (120.0, 64.75) left into the exposed pad.
6. **IC1 exposed pad has no vias.** Add 9 GND vias 0.6/0.3 at x 116.5 / 117.5 / 118.5 × y 64.0 / 65.0 / 66.0.
7. **H2/H3/H4 have pad numbers 2/3/4 instead of 1** (parity warnings). Select them → right-click → *Update Footprint from Library* (keeps position).

## Phase 2b: MCU / power / USB placement (computed 2026-11-21)

### Schematic pin remap (U4 only, firmware pin map only), do this first
Removes every SPI crossing and the long B.Cu BUSY/IRQ/RST runs.

| Net | old U4 pin | new U4 pin |
|---|---|---|
| BUSY | 18 (IO14) | **13 (IO9)** |
| SCLK | 16 (IO12) | **15 (IO11)** |
| MOSI | 15 (IO11) | **16 (IO12)** |
| LORA_IRQ | 27 | **10 (IO6)** |
| LORA_RST | 25 | **11 (IO7)** |

SPI then goes through the GPIO matrix (fine, LR1121 max is 16 MHz). USB (IO19/20) and UART0 (IO43/44) stay as they are. After the edit: F8, *Replace footprints* unticked.
Then delete the BUSY via at (114.3, 62.4) and its 2 segments: BUSY goes on F.Cu with the SPI bundle.

### Positions (U4 stays at 138.925, 64.275, rot 0)

Top (F.Cu):

| Ref | X | Y | Rot | Note |
|---|---|---|---|---|
| J1 | 156.325 | 65.0 | 90 | USB-C, opening at the right edge (PCB-edge line on x 160) |
| J2 | 149.5 | 53.1 | 180 | JST-SH, opening at the top edge (0.5 mm inset so the MP tabs stay on the board) |
| U2 | 144.5 | 75.0 | 180 | USB ESD; D+ top row, D− bottom row |
| R4 | 149.7 | 63.2 | 180 | CC2 5.1k |
| R3 | 150.4 | 68.9 | 270 | CC1 5.1k |
| SW1 | 141.3 | 52.5 | 0 | EN/reset |
| C3 | 136.6 | 52.6 | 90 | EN cap |
| R1 | 143.9 | 55.45 | 0 | EN pull-up |
| SW2 | 131.0 | 52.5 | 180 | BOOT |
| R2 | 134.8 | 55.4 | 0 | BOOT pull-up |
| D3 | 122.0 | 55.2 | 0 | LED |
| R6 | 125.2 | 55.2 | 0 | LED resistor |

Bottom (B.Cu): in Properties set **Side: Back**, then type the orientation.

| Ref | X | Y | Rot | Check after placing |
|---|---|---|---|---|
| U1 | 146.0 | 65.5 | 180 | tab on the LEFT, 3 pins on the right, pin 3 (IN) lowest |
| D1 | 149.6 | 70.3 | 0 | cathode bar on the LEFT |
| D2 | 151.0 | 58.5 | 90 | cathode bar at the BOTTOM |
| C6 | 145.5 | 70.9 | 180 | LDO_IN pad on the right |
| C7 | 145.5 | 72.9 | 180 | LDO_IN pad on the right |
| C4 | 145.2 | 60.3 | 0 | +3.3V pad on the left |
| C5 | 145.2 | 58.3 | 0 | +3.3V pad on the left |
| C1 | 133.4 | 60.0 | 0 | +3.3V pad on the left |
| C2 | 133.4 | 62.0 | 0 | +3.3V pad on the left |

Checked by script: no courtyard overlaps on either side; pads ≥ 0.2 mm apart; every planned track below ≥ 0.15 mm from other nets. The J2/U4 bbox touches only at J2's notch, and the real outlines don't overlap.
Previews: `LoRatron_V2_phase2b_top_preview.png`, `LoRatron_V2_phase2b_bottom_preview.png`.

### Why the power section goes on the bottom
- The SOT-223 doesn't fit on top anywhere without blocking the USB or SPI paths.
- Under U4 it's > 15 mm from the RF chain. B.Cu under the RF corner (x < 124) stays solid GND.
- It's a linear regulator: no switching noise. The only switcher is the LR1121 DC-DC, already placed.
- Assembly: reflow the bottom first, or hand-solder it (SOT-223, 0805, SOD-123 are easy).

### Vias (0.6/0.3)
| At | Net | Purpose |
|---|---|---|
| (130.6, 60.025) | +3.3V | B.Cu trunk → U4 pin 3; C1/C2 on B.Cu next to it |
| (124.3, 62.5) | +3.3V | B.Cu hop under SPI + V1/V2 ring → C28 top pad |
| (142.1, 55.5), (136.5, 55.4) | +3.3V | R1 / R2 pull-ups |
| (151.45, 62.25), (151.55, 67.75) | VBUS | J1 VBUS pad pairs → B.Cu |
| (142.05, 75.0) | VBUS | U2 pin 5 |
| (146.95, 75.0) | GND | U2 pin 2 |
| (148.9, 62.15) | GND | R4 GND (lands in U1 pin 1 GND on B.Cu) |
| (151.0, 56.2) | +5V | J2 pin 1 → D2 on B.Cu |
| (147.9, 57.9), (149.0, 56.25) | TXDO | B.Cu hop: the J2 pinout is mirrored vs. U4, so TX must cross RX once |
| (130.6, 65.975) / (130.6, 66.825) | IRQ / RST | B.Cu landing next to U4 pins 10 / 11 |

### Trace paths
- **SPI + BUSY (F.Cu, 0.2):**
  - BUSY: pin 25 → left to x 114.5 → up to y 58.0.
  - NSS/SCLK/MOSI/MISO: straight up to y 58.5 / 59.0 / 59.5 / 60.0.
  - All five run right, then down at x **128.4 / 127.95 / 127.5 / 127.05 / 126.6**.
  - Into U4: BUSY→13 (y 68.525), NSS→14, SCLK→15 (y 70.225). MOSI under the corner at y 72.4 → pin 16; MISO at y 72.9 → pin 17.
- **V1/V2 ring:** unchanged (x 124.9 / 125.6, y 77.2 / 78.0, y 61.0 / 60.5).
- **IRQ/RST (B.Cu, 0.2):**
  - IRQ: via (120.55, 67.55) → right on y 67.55 → angle up → via (130.6, 65.975).
  - RST: via (120.25, 68.25) → (121.0, 69.1) → right on y 69.1 → angle up → via (130.6, 66.825).
  - Short F.Cu stubs into pins 10/11.
- **+3.3V:**
  - B.Cu 0.5 from C5/C4 and the U1 tab along y 58.3 under U4 → via (130.6, 60.025) → B.Cu diagonal → via (124.3, 62.5) → C28.
  - Inside the ring (F.Cu 0.3): C28 → down x **124.3** → y 76.2 → left → x 115.55 → up to C8. This replaces the old "enters from the bottom" hop.
- **BOOT:** pin 4 → left to x 129.7 → up → SW2 left pad. R2 hangs off SW2's right pad.
- **IO2:** pin 6 → left to x 129.1 → up to y 57.2 → left → R6 → D3.
- **EN:** pin 45 → right to x 146.7 → up to y 55.45 → R1 pin 2, SW1 lower pads, C3.
- **UART:**
  - RX: pin 40 → x 147.3 → up to y 57.1 → right → J2 pin 2.
  - TX: pin 39 → x 147.9 → up to the via (147.9, 57.9) → B.Cu → via (149.0, 56.25) → J2 pin 3.
- **USB (F.Cu, 0.25), no vias:**
  - Join D+ B6 and A6 behind the pad row (loop at x 153.6, under the connector body).
  - Join D− A7 and B7 in front (x 151.7).
  - D+ leaves at y 64.25 → down x 149.0. D− leaves at y 65.75 → down x 149.6.
  - Both go left through U2 (y 74.05 / 75.95), then on to U4 pins 24 / 23.
- **CC:** B5 → R4 right pad. A5 → x 150.4 → down to R3 top pad. R3 GND → J1 shell pad.
- **B.Cu power (0.5):**
  - J1 VBUS vias → x 151.9 / 151.5 → D1 anode. U2's VBUS via → y 76.2 → D1 anode.
  - D1 cathode and D2 cathode (down x 150.6) → U1 pin 3. C6/C7 on LDO_IN.
  - Pour a B.Cu +3.3V area around the U1 tab for heat.

---

## Phase 2c check (2026-11-21, board saved 13:06)

Verified from saved file: U4 pin remap matches (BUSY 13, SCLK 15, MOSI 16, IRQ 10, RST 11), parity 0 issues,
all 21 Phase 2b parts at planned position/rotation/side (C5 at x 145.5 instead of 145.2 - fine). Bottom-side
orientations correct: U1 tab left / pin 3 IN lowest, D1 cathode left, D2 cathode bottom. No clearance errors.
H2-H4 pad numbers fixed. Remaining DRC: J1 hole_clearance x8 (footprint, expected), GND vias dangling (no pour yet),
R3 lib_footprint_mismatch (Update Footprint from Library), silk warnings.

Still unconnected (non-GND) - add these (all checked >= 0.18 mm to other nets):

| # | Net | Layer | Width | Points |
|---|---|---|---|---|
| 1 | BUSY | F | 0.3 | delete via (114.3,62.4) + its 2 stubs, then (115.0,63.25) (115.0,61.161) (118.061,58.1) (126.0,58.1) (128.6,60.7) (128.6,67.6) (129.525,68.525) (131.925,68.525) |
| 2 | /USB_P | F | 0.3 | U2 pad 4 (143.363,74.05) -> pad 3 (145.637,74.05) straight under U2 |
| 3 | /USB_N | F | 0.3 | U2 pad 6 (143.363,75.95) -> pad 1 (145.637,75.95) |
| 4 | VBUS | B | 0.5 | via (142.05,75.0) (143.25,76.2) (150.45,76.2) (151.25,75.4) D1 pad 2 (151.25,70.3) |
| 5 | /LDO_IN | B | 0.5 | D2 pad 1 (151.0,60.15) (150.65,60.5) (150.65,67.3) (150.15,67.8) U1 pin 3 (149.15,67.8) |
| 6 | +3.3V | B | 0.6 | U1 tab (142.85,65.5) -> U1 pin 2 (149.15,65.5) |
| 7 | +3.3V | F | 0.3 | R2 pad 2 (135.625,55.4) -> via (136.5,55.4) |
| 8 | +3.3V | F | 0.3 | R1 pad 1 (143.075,55.45) -> via (142.1,55.5) |
| 9 | +3.3V | F | 0.2 | C30 pad 2 (116.15,69.32) (115.56,69.32) (115.56,71.4) into C8 pad 2 - IC1 pin 2/C30 island is otherwise unfed |
| 10 | GND | via 0.6/0.3 | - | U4 centre pad: (138.1,63.45) (139.75,63.45) (138.1,65.1) (139.75,65.1) - in the gaps between the 1.2 mm sub-pads |

After that, only GND remains unconnected -> next step is the GND pours (F.Cu + B.Cu), then stitching.
Preview: LoRatron_V2_phase2c_fixes_preview.png (green = to add).
