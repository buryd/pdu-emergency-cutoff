# PDU Emergency Cutoff — configuration

# --- Pins (see hardware/PINMAP.md) ---
PIN_CT_ADC = 26          # GP26 ADC0
PIN_BTN_LEARN = 10
PIN_BTN_SAVE = 11
PIN_BTN_RESET = 12
PIN_TRIP = 15
PIN_LED_ARMED = 16
PIN_LED_TRIPPED = 17
PIN_LED_LEARN = 18

# DLI switch port: True = GPIO low commands cutoff
TRIP_ACTIVE_LOW = True

# --- Current thresholds ---
# Factory / startup baseline for this rack PDU
DEFAULT_BASELINE_AMPS = 0.4
TRIP_RATIO = 1.30          # 30% above baseline → 0.52 A at factory default

# --- CT / ADC scaling ---
# SCT-013-005: 5 A → ~1 V RMS typical (burden-dependent).
# After bias adapter, measure Vrms of the AC component at GP26 and set:
#   AMPS_PER_ADC_VOLT = 5.0 / Vrms_at_5A
# Start conservative; calibrate with a meter at ~0.4 A.
ADC_VREF = 3.3
AMPS_PER_ADC_VOLT = 5.0    # tune during commissioning

# --- Sampling ---
SAMPLE_HZ = 2000
RMS_WINDOW_SAMPLES = 200   # 100 ms at 2 kHz
TRIP_DEBOUNCE_MS = 200
LEARN_SECONDS = 5.0

# Safe trip if CT signal looks invalid (optional)
TRIP_ON_SENSOR_FAULT = False

BASELINE_PATH = "baseline.json"
