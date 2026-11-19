# LoRatron V2: manual RF changes in KiCad (keep your layout)

Values from Semtech LR1121MB1DIS (e655, 0402) and LR1121MB2THDAS (e742). All work is on the **RF sheet**.
KiCad keys: **A** add symbol, **E** edit properties, **W** wire, **P** power symbol (GND / +3.3V), **R** rotate, **Del** delete, **M** move, **G** drag (keeps wires attached).
New parts: `Device:C`, `Device:L`, `Device:R`, `Device:FerriteBead`. Leave them as `C?`, `L?`… and annotate at the end (step 10).

Footprints for new parts: caps `Capacitor_SMD:C_0402_1005Metric`, inductors `Inductor_SMD:L_0402_1005Metric`, resistors `Resistor_SMD:R_0402_1005Metric`.

## 1. Value and footprint changes only (press E on the part)
| Part | Value now → new | Footprint | MPN (optional field) |
|---|---|---|---|
| L1 | 2.2uH → **10uH** | **Inductor_SMD:L_0603_1608Metric** | MLZ1608N100LT000 |
| L2 | 3.6nH (same) | **Inductor_SMD:L_0402_1005Metric** | LQW15AN3N6C10D |
| L3 | 47nH (same) | **Inductor_SMD:L_0402_1005Metric** | LQW15AN47NJ00D |
| L4 | 22nH → **3.3nH** | **Inductor_SMD:L_0402_1005Metric** | LQW15AN3N3C80D |
| L5 | 56nH → **22nH** | **Inductor_SMD:L_0402_1005Metric** | LQW15AN22NH00D |
| C11 | 100nF → **2.2nF** | — | GRM155R71H222KA01D |
| C12 | 100pF → **47pF** | — | GRM1555C1H470JA01D |
| C15 | 1pF → **1.6pF** | — | GRM1555C1H1R6BA01D |
| C16 | 47pF → **33pF** | — | GRM1555C1H330JA01D |
| C17 | 4.3pF → **1.2pF** | — | GRM1555C1H1R2BA01D |
| C19 | 47pF → **1.2pF** | — | GRM1555C1H1R2BA01D |
| C20 | 1.2pF → **1.5pF** | — | GRM1555C1H1R5BA01D |

## 2. Sub-GHz HP transmit (pin 32 → U3 RF1)
Target: VR_PA –[L3 ∥ 200Ω]– **pin 32** –[L4 3.3nH ∥ C17 1.2pF]– (6.8pF to GND) – 8.2nH – (NC to GND) – C18 47pF – (1.8pF to GND) – U3 RF1
1. **200 Ω across L3:** add an R (200, 0402) parallel to L3, with one end on the VR_PA side and the other on the pin 32 side.
2. **C17 becomes the trap cap.** Delete the wire from C17 to its GND symbol, and the GND symbol. Wire C17 **in parallel with L4**: one end at the pin 32 / L4-bottom node, the other at the L4-top node.
3. **Break the wire** between the L4 top node and C18. In the gap, insert in order:
   - a **C 6.8pF** to GND, at the L4-top node;
   - a series **L 8.2nH** (LQW15AN8N2J00D);
   - a **C "NC"** to GND (set **Do not populate** in its properties);
   - then C18.
4. On the U3 side of C18 (the C18–RF1 node), add a **C 1.8pF** to GND (GRM1555C1H1R8BA01D).

## 3. Sub-GHz receive balun (pins 30 P / 29 N → U3 RF2)
Target: L5 22nH between P and N. N: 1.2pF to GND (C19). P –C20 1.5pF– **node A**. N –47nH– node A. Node A: NC to GND, and C21 47pF to U3 RF2.
1. L5 stays between the P and N wires (value already changed in step 1).
2. C19 stays from **N to GND** (value already 1.2pF).
3. **C20:** delete its GND symbol and wire. Its other end becomes the new **node A**: C20 now goes in series from P to node A.
4. **C21:** disconnect it from the P line. Reconnect it from **node A** to U3 RF2. The other end stays on RF2.
5. Add an **L 47nH** (LQW15AN47NJ00D) from the **N line to node A**.
6. Add a **C "NC"** (DNP) from node A to GND.
7. Check: the P line now reaches only L5 and C20, and the switch connects only through C21 from node A.

## 4. 2.4 GHz filter (pin 26 → J3)
Target: pin 26 – (C14 1.3pF) – L2 3.6nH – (C15 1.6pF) – [3.6nH ∥ NC] – (0.7pF to GND) – C16 33pF – J3
1. Break the wire between the C15/L2 node and C16.
2. Insert a series **L 3.6nH** (LQW15AN3N6C10D), plus a **C "NC"** (DNP) in parallel with it.
3. After it, add a **C 0.7pF** to GND (GRM1555C1HR70BA01D), then C16 → J3.

## 5. Antenna low-pass (U3 RFC → J4)
Target: U3 RFC – (3.3pF to GND) – 9.1nH – (3.3pF to GND) – C22 47pF – J4
1. Break the wire between U3 RFC (pin 5) and C22.
2. Insert:
   - a **C 3.3pF** to GND at the RFC side;
   - a series **L 9.1nH** (LQW15AN9N1J00D);
   - a **C 3.3pF** to GND (GRM1555C1H3R3BA01D);
   - then C22 → J4.

## 6. RF switch control (V1 / V2)
At IC1 DIO5 (pin 20) and DIO6 (pin 19), labels V1 and V2 currently go straight to U3.
1. At IC1, rename the labels on pins 20 and 19 to **RFSW0** and **RFSW1**. Keep the U3-side labels as V1 / V2.
2. Add **R 100 Ω** between RFSW0 and V1, and **R 100 Ω** between RFSW1 and V2.
3. Add a **C 1nF** to GND on V1 and on V2 (GRM155R71H102KA01D).

## 7. Supplies
1. **VBAT_RF** (pin 2, next to C8): add a **C 47pF** from +3.3V to GND (GRM1555C1H470JA01D).
2. Add a **C 10uF** (footprint **C_0603_1608Metric**, GRM188R61A106ME69D) from +3.3V to GND near the LR1121.

## 8. TCXO supply (split VTCXO)
Target: IC1 VTCXO (pin 3) – (470pF to GND) – ferrite – **TCXO_VDD** – (C23 100nF) – Y1 VDD
1. Up at Y1, rename the **VTCXO** label on the Y1 VDD / C23 wire to **TCXO_VDD**.
2. Add **FerriteBead** (value `10R`, MPN BLM15AG100SN1D, footprint `Inductor_SMD:L_0402_1005Metric`) between a **VTCXO** label and a **TCXO_VDD** label.
3. Add a **C 470pF** (GRM1555C1H471JA01D) from VTCXO to GND.
4. **PWR_FLAG:** the floating PWR_FLAG on the left has a **VTCXO** label. Rename that label to **TCXO_VDD**. Otherwise ERC flags Y1's power pin as not driven.

## 9. Check
- No wire should still join C17 or C20 to GND.
- C21 should no longer touch the P line.

## 10. Finish
1. **Annotate**: Tools → Annotate Schematic, with **Keep existing annotations**. New parts get C24+, L6+, R7+, FB1.
2. **ERC**: should be 0.
3. Save and close KiCad. I'll check the netlist against the Semtech topology.

### Parts to add (summary)
| Qty | Part | Value | Where |
|---|---|---|---|
| 1 | R | 200 Ω | across L3 |
| 2 | R | 100 Ω | V1, V2 |
| 1 | C | 6.8 pF | HP, L4 top to GND |
| 1 | L | 8.2 nH | HP series |
| 3 | C | NC (DNP) | HP shunt, Rx node A, across the 2.4 G 3.6 nH |
| 1 | C | 1.8 pF | HP, switch side to GND |
| 1 | L | 47 nH | Rx, N to A |
| 1 | L | 3.6 nH | 2.4 G series |
| 1 | C | 0.7 pF | 2.4 G to GND |
| 2 | C | 3.3 pF | antenna π |
| 1 | L | 9.1 nH | antenna π |
| 2 | C | 1 nF | V1, V2 |
| 1 | C | 47 pF | VBAT_RF |
| 1 | C | 10 µF 0603 | bulk |
| 1 | C | 470 pF | VTCXO |
| 1 | FerriteBead | 10R | VTCXO → TCXO_VDD |
