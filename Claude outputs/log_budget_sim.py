"""LoRatron V2 log-budget simulation: does 8 MB of flash (ESP32-S3-MINI-1U-N8) hold a flight log?

Run: python3 log_budget_sim.py   (needs numpy)
Edit the CONFIG blocks below to match your real firmware once it exists.

Flight model: same approximated rocket as roll_sim.py (4.63 kg, ~500 N for 1.2 s, CdA 37 cm^2),
plus dual-deploy descent (drogue at apogee, main at MAIN_ALT).
"""
import numpy as np

# ---------------------------------------------------------------- flight model
m0, mprop, tb, T0, CdA, rho, g = 4.63, 0.42, 1.2, 500.0, 37e-4, 1.2, 9.81
V_DROGUE, V_MAIN, MAIN_ALT = 20.0, 6.0, 150.0      # descent rates [m/s], main deploy altitude [m]


def flight_timeline():
    dt, t, h, v = 0.001, 0.0, 0.0, 0.0
    while True:
        m = m0 - mprop * min(t, tb) / tb
        T = T0 if t < tb else 0.0
        a = (T - 0.5 * rho * CdA * v * abs(v)) / m - g
        v += a * dt; h += v * dt; t += dt
        if t > tb and v <= 0:
            break
    t_apo, h_apo = t, h
    t_main = t_apo + (h_apo - MAIN_ALT) / V_DROGUE
    t_land = t_main + MAIN_ALT / V_MAIN
    return dict(apogee_m=h_apo, t_apogee=t_apo, t_main=t_main, t_land=t_land)


# ---------------------------------------------------------------- flash budget
FLASH = 8 * 1024 * 1024
RESERVED = 0x10000            # bootloader + partition table + NVS + phy_init (64 kB)
APP = 2 * 1024 * 1024         # one 2 MB factory app, no OTA (custom partitions.csv)
LOG_PART = FLASH - RESERVED - APP
ARDUINO_DEFAULT_8MB_SPIFFS = 0x160000   # what the stock Arduino "8MB" table leaves for data (~1.4 MB)

# ---------------------------------------------------------------- record sizes (bytes)
# binary = packed struct incl. 1 B type tag + 4 B timestamp; csv = typical printf line
REC = {
    #            binary  csv
    'imu':       (17,     75),   # ax ay az gx gy gz int16
    'imu_highg': (23,     95),   # + high-g accel xyz int16
    'baro':      (11,     30),   # pressure int32, temp int16
    'gps':       (29,     90),   # lat lon alt int32, vN vE vD int16, sats, fix
    'lora_stat': (13,     40),   # seq, RSSI, SNR, tx/rx flag, packet len
    'lora_raw':  (64,    140),   # full packet copy (~50 B payload + header)
    'state':     (12,     40),   # FSM state / events / battery voltage
}


def scenario(name, rates_flight, rates_pad, fmt, pad_min, landed_min, pretrig_s, tl, full_rate_always=False):
    """Bytes written for one launch day. rates_* = {record: Hz}."""
    col = 0 if fmt == 'bin' else 1
    bps_flight = sum(REC[k][col] * hz for k, hz in rates_flight.items())
    bps_pad = sum(REC[k][col] * hz for k, hz in rates_pad.items())
    t_flight = tl['t_land'] + 60          # liftoff -> landed + 1 min margin at full rate
    if full_rate_always:
        total = bps_flight * (pad_min * 60 + t_flight + landed_min * 60)
    else:
        total = (bps_pad * pad_min * 60          # waiting on the rail
                 + bps_flight * pretrig_s         # RAM ring buffer dumped at liftoff
                 + bps_flight * t_flight          # boost -> landing
                 + bps_pad * landed_min * 60)     # waiting for recovery
    return dict(name=name, fmt=fmt, bps_flight=bps_flight, bps_pad=bps_pad, total=total,
                fill=total / LOG_PART, fullrate_min=LOG_PART / bps_flight / 60)


if __name__ == '__main__':
    tl = flight_timeline()
    print(f"Flight: apogee {tl['apogee_m']:.0f} m at {tl['t_apogee']:.1f} s, main at {tl['t_main']:.0f} s, "
          f"landing at {tl['t_land']:.0f} s")
    print(f"Log partition: {LOG_PART/2**20:.2f} MiB of 8 MiB "
          f"(stock Arduino 8MB table would leave only {ARDUINO_DEFAULT_8MB_SPIFFS/2**20:.2f} MiB)\n")

    PAD = dict(imu=1, baro=1, gps=1, lora_stat=1, state=1)       # 1 Hz "heartbeat" while waiting
    LEAN = dict(imu=100, baro=50, gps=5, lora_stat=5, state=10)
    HEAVY = dict(imu_highg=1000, baro=100, gps=10, lora_stat=10, lora_raw=10, state=10)
    PAD_MIN, LANDED_MIN = 90, 30                                  # pessimistic launch-day waits

    runs = [
        scenario('A  lean, binary, phase-gated', LEAN, PAD, 'bin', PAD_MIN, LANDED_MIN, 5, tl),
        scenario('B  heavy (1 kHz IMU), binary, phase-gated', HEAVY, PAD, 'bin', PAD_MIN, LANDED_MIN, 5, tl),
        scenario('C  heavy, CSV text, phase-gated', HEAVY, PAD, 'csv', PAD_MIN, LANDED_MIN, 5, tl),
        scenario('D  lean, binary, full rate the whole 2 h', LEAN, PAD, 'bin', PAD_MIN, LANDED_MIN, 0, tl, True),
        scenario('E  heavy, binary, full rate the whole 2 h', HEAVY, PAD, 'bin', PAD_MIN, LANDED_MIN, 0, tl, True),
        scenario('F  heavy, CSV, full rate the whole 2 h', HEAVY, PAD, 'csv', PAD_MIN, LANDED_MIN, 0, tl, True),
    ]
    print(f"{'scenario':46s} {'flight rate':>12s} {'launch day':>11s} {'% of log':>9s} {'full-rate fits':>15s}")
    for r in runs:
        print(f"{r['name']:46s} {r['bps_flight']/1024:8.1f} kB/s {r['total']/2**20:8.2f} MiB "
              f"{100*r['fill']:8.1f}% {r['fullrate_min']:11.1f} min")

    # UART ceiling: the board can't log more than the AV can send it
    for baud in (115200, 460800, 921600):
        bps = baud / 10
        print(f"UART {baud:>6d} baud saturated: {bps/1024:6.1f} kB/s -> partition full in {LOG_PART/bps/60:6.1f} min")
