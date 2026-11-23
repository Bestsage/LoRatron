# LoRatron V2: checkpoint (2026-11-20)

*State at commit `bface37` on `main`. This replaces `LoRatron_V2_checkpoint_2026-11-19.md` as the place to start. The older file still has the background: project goals, power/link budget, firmware notes.*

---

## Where we are

| Area | Status |
|---|---|
| Schematic | ✅ Sub-GHz switched to the **Johanson IPD U5 (0900PC16J0042001E)**. 57 parts, **ERC 0**. Netlist verified (commit `1adc8b9`). |
| IPD library parts | ✅ Footprint `custom_footrpint:Johanson_IPD_0900PC16J0042001E` (checked). Symbol `Johanson_IPD:0900PC16J0042001E` (in `sym-lib-table`). |
| PCB Phase 1 | ✅ V1 copper stripped. **2 layers**, 1.6 mm. Outline **(100,50)→(160,80)**. Holes H1–H4 at 3.5 mm in from the edges. F8 update done. **All 57 parts on top** (commit `bface37`). |
| PCB Phase 2 (placement) | 🟡 **RF corner positions computed and checked** (31 parts, table in the layout steps file, Phase 2a). **The user is typing them into KiCad by hand** (started end of 2026-11-20). MCU/power placement not started. |
| Routing, DRC, Gerbers, order | ⬜ Not started. |

## What changed in the schematic (RF sheet)

- **Removed:** L4, C17, C24, L6, C25, L5, C19, C20, L7.
- **Added:** U5 IPD, connected as follows:
  - 1 → RFO_HP (IC1.32, L3, R7)
  - 3 → RFI_P (IC1.30)
  - 4 → RFI_N (IC1.29)
  - 9 → IPD_TX → C18 → U3 RF1
  - 6 → IPD_RX → C21 → U3 RF2
  - 5/7/10 → GND
  - 2/8 → no-connect
- **Changed:** L8 = 0R; C26/C27 = DNP (spare π pads).
- **Known trade-off:** the datasheet only specifies the IPD's TX_HP path for 902–928 MHz. We're using it at 869.5 MHz on purpose; the plot suggests it works with ~1–2 dB more loss. Accepted.

## To resume (next session starts here)

1. **Verify the RF corner placement the user typed in.** KiCad must be closed (no `~*.lck`).
   - Read `loratron.kicad_pcb` and compare the 31 RF parts' position and rotation against the **Phase 2a table** in `LoRatron_V2_PCB_layout_steps.md`.
   - Re-run the collision check (courtyards, pad gaps ≥ 0.2 mm, edge/holes). The previous script and footprint data were in the old session's scratchpad, which may be gone: rebuild them from the board file if needed.
   - Report any part that's off, with the value to retype. When it's clean, the user commits.
2. **Place U4 and the power section:**
   - U4 MINI, rot 0, courtyard starting at x > 125.9. Its LoRa pins (SPI/BUSY/RST/IRQ) are at its bottom-left corner and USB at the bottom centre.
   - Power on the right edge: USB-C J1 at the edge, then U1 LDO, D1/D2, U2 ESD, J2, SW1/SW2, D3.
   - Bottom-side parts are allowed here, but not in the RF area.
3. Then do the vias and routing from the Phase 2a "Vias to place" and "Trace paths" lists.

Background, from `LoRatron_V2_PCB_layout_steps.md` → "Phase 2" / "Phase 2a":

- **IC1:** rot 90 at about (117.5, 65), RF pins facing the left edge.
- **Sub-GHz chain:** IPD → C18/C21 → U3 → C22 → L8 → J4, going left.
- **2.4 GHz chain:** vertical column up to J3 at about (113.4, 54).
- **U4 MINI:** rot 0, right of IC1.
- **Routing topology:**
  - V1 hops under the RFC line on B.Cu, then V1/V2 run around the bottom/right of IC1.
  - IRQ, NRESET and BUSY go on B.Cu to U4.
  - +3.3V crosses the V1/V2 ring once on B.Cu.

**RF lines:**
- Every RF run in the corner is < 2 mm, so pad-width traces (≈ 0.5 mm) are fine there.
- On any longer 50 Ω line, use CPWG **1.1 mm track / 0.2 mm gap** (≈ 52 Ω).
- B.Cu stays solid GND under the RF parts. The only exception is the V1 hop, which is planned.

## Still open

1. **Placement and routing** (Phase 2 onwards), then DRC, Gerbers, and a JLC 2-layer quote with stencil.
2. **Buy the IPD from DigiKey** (712-0900PC16J0042001ECT-ND, ~$0.72). LCSC C19842466 is out of stock. Order 4–5.
3. **Multimeter check on a loose IPD before assembly:** pins 1, 3 and 4 to GND must read **open**.
4. **Optional schematic tweak:** swap ESP32 IO11/IO12 (MOSI/SCLK) so the SPI lines don't cross.
5. **BOM MPNs for RF parts.** List in `LoRatron_V2_RF_manual_steps.md`; drop the 9 removed parts.
6. **Firmware (later):**
   - HP PA settings
   - RF-switch table for DIO5/DIO6
   - VTCXO ≥ 1.8 V (3.0 V suggested)
   - band 869.4–869.65 MHz

## Files

| File | What |
|---|---|
| `Claude outputs/LoRatron_V2_Johanson_IPD_steps.md` | IPD guide: decision, footprint/symbol/schematic steps, layout notes, BOM |
| `Claude outputs/LoRatron_V2_PCB_layout_steps.md` | PCB decisions, Phase 1 steps/result, Phase 2 plan, **Phase 2a RF corner table + vias + trace paths** |
| `Claude outputs/LoRatron_V2_RF_corner_preview.png` | Picture of the computed RF corner placement |
| `Claude outputs/LoRatron_V2_checkpoint_2026-11-19.md` | Previous checkpoint: background, link budget, power, firmware |
| `custom_symbols/Johanson_IPD.kicad_sym.bak_before_symbol` | Backup of the empty symbol file before Claude wrote it (can be deleted) |

## Ground rules (unchanged)

- The user commits; no Claude attribution.
- **KiCad fully closed** before Claude edits any file: no `~*.lck`, check the mtime, make a `.bak_before_*` backup first.
- The user makes KiCad edits by hand from step-by-step guidance. Claude checks the result from the saved files and netlist.
