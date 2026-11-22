"""
RAPTOR - Step 2: Gating filter for UWB ranges
=============================================
Reads uwb_synthetic.csv (made by generate_uwb_data.py) and, for each anchor,
decides for every measurement: ACCEPT or REJECT.

It uses ONLY the measured columns (A1_meas_m ... A4_meas_m), and only
values from the PAST, exactly like it would run live on the robot.
The answer-key columns (true values and labels) are used only at the end
to grade the filter.

Output:
  uwb_gated.csv        -> gated ranges + reason code for each value
  gating_result.png    -> plot: accepted vs rejected values
  printed report       -> how many spikes caught, good values lost, etc.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =============================================================================
# CONFIG - gating rules (all tunable)
# =============================================================================
# Rule 1: possible range of values ---------------------------------------------
# Shortest possible distance = height difference (robot right under anchor)
# Longest possible distance  = arena diagonal in 3D
HEIGHT_DIFF = 2.0 - 0.3                       # anchor height - tag height (m)
ARENA_DIAGONAL_3D = np.sqrt(10**2 + 10**2 + HEIGHT_DIFF**2)   # ~14.2 m
RANGE_MARGIN = 0.5                            # tolerance for offset + noise (m)
MIN_RANGE = HEIGHT_DIFF - RANGE_MARGIN        # ~1.2 m
MAX_RANGE = ARENA_DIAGONAL_3D + RANGE_MARGIN  # ~14.7 m

# Rule 2: possible change between samples --------------------------------------
MAX_SPEED = 1.5        # fastest the robot could move (m/s), with margin
NOISE_MARGIN = 0.30    # extra allowance for noise (m)

# Recovery: avoid getting "stuck" after a real, sudden change ------------------
RECOVERY_COUNT = 3     # this many rejections in a row ...
RECOVERY_TOL = 0.30    # ... that agree with each other within 0.30 m
                       # -> accept them as the new real level

# Reason codes saved for every value
OK, MISSING, OUT_OF_RANGE, JUMP = 0, 1, 2, 3
REASON_NAMES = {OK: "accepted", MISSING: "missing",
                OUT_OF_RANGE: "out of range", JUMP: "jump"}


# =============================================================================
# THE FILTER - processes one anchor, one sample at a time
# =============================================================================
def gate_anchor(times, ranges):
    """Return (gated_ranges, reasons) for one anchor.
    gated_ranges: the value if accepted, NaN if rejected or missing."""
    n = len(ranges)
    gated = np.full(n, np.nan)
    reasons = np.zeros(n, dtype=int)

    last_value = None      # last accepted value (the "reference")
    last_time = None       # when it was accepted
    recent_jumps = []      # values rejected as jumps, in a row

    for k in range(n):
        r, t = ranges[k], times[k]

        # --- Check 0: is there a value at all? ---------------------------
        if np.isnan(r):
            reasons[k] = MISSING
            continue                     # nothing to check; keep reference

        # --- Rule 1: is the value physically possible? -------------------
        if r < MIN_RANGE or r > MAX_RANGE:
            reasons[k] = OUT_OF_RANGE
            continue

        # --- First valid value ever: accept it as the starting reference -
        if last_value is None:
            gated[k], last_value, last_time = r, r, t
            continue

        # --- Rule 2: could the distance change this much in this time? ---
        elapsed = t - last_time                      # grows during gaps
        allowed = MAX_SPEED * elapsed + NOISE_MARGIN
        if abs(r - last_value) <= allowed:
            gated[k], last_value, last_time = r, r, t   # accept
            recent_jumps = []
            continue

        # --- Rejected as a jump. Check recovery: ---------------------------
        # several jumps in a row that agree with each other are probably
        # a REAL change (or a wrong reference), not random spikes.
        reasons[k] = JUMP
        recent_jumps.append(r)
        if len(recent_jumps) >= RECOVERY_COUNT:
            last_n = recent_jumps[-RECOVERY_COUNT:]
            if max(last_n) - min(last_n) <= RECOVERY_TOL:
                gated[k], last_value, last_time = r, r, t   # accept, reset
                reasons[k] = OK
                recent_jumps = []

    return gated, reasons


# =============================================================================
# LOAD the data
# =============================================================================
data = np.genfromtxt("uwb_synthetic.csv", delimiter=",", names=True)
t = data["time_s"]
N_ANCHORS = 4

# =============================================================================
# RUN the filter on each anchor
# =============================================================================
gated = np.zeros((len(t), N_ANCHORS))
reasons = np.zeros((len(t), N_ANCHORS), dtype=int)
for i in range(N_ANCHORS):
    gated[:, i], reasons[:, i] = gate_anchor(t, data[f"A{i+1}_meas_m"])

# =============================================================================
# GRADE the filter using the answer key
# =============================================================================
print("=" * 66)
print(f"Gating rules: range {MIN_RANGE:.2f}-{MAX_RANGE:.2f} m, "
      f"max jump = {MAX_SPEED} m/s x dt + {NOISE_MARGIN} m")
print("=" * 66)
print(f"{'Anchor':<7}{'spikes':>8}{'caught':>8}{'missed':>8}"
      f"{'good lost':>11}{'RMS before':>12}{'RMS after':>11}")

total = dict(spikes=0, caught=0, missed=0, lost=0)
for i in range(N_ANCHORS):
    a = f"A{i+1}"
    meas, true = data[f"{a}_meas_m"], data[f"{a}_true_m"]
    spike = data[f"{a}_spike"] == 1
    nlos = data[f"{a}_nlos"] == 1
    present = ~np.isnan(meas)
    rejected = present & np.isnan(gated[:, i])

    caught = (spike & rejected).sum()
    missed = (spike & ~rejected).sum()
    # "good" = present, not a spike, not NLOS -> should have been accepted
    good = present & ~spike & ~nlos
    lost = (good & rejected).sum()

    err_before = (meas - true)[present]
    err_after = (gated[:, i] - true)[~np.isnan(gated[:, i])]
    rms_b = np.sqrt(np.mean(err_before**2))
    rms_a = np.sqrt(np.mean(err_after**2))

    print(f"{a:<7}{spike.sum():>8}{caught:>8}{missed:>8}{lost:>11}"
          f"{rms_b:>11.3f}m{rms_a:>10.3f}m")
    total["spikes"] += spike.sum(); total["caught"] += caught
    total["missed"] += missed; total["lost"] += lost

print("-" * 66)
print(f"Total spikes {total['spikes']}: caught {total['caught']}, "
      f"missed {total['missed']}  |  good values wrongly rejected: "
      f"{total['lost']}")
print("Reason counts (all anchors):",
      {REASON_NAMES[c]: int((reasons == c).sum()) for c in REASON_NAMES})

# =============================================================================
# SAVE the result
# =============================================================================
cols, header, fmts = [t], ["time_s"], ["%.1f"]
for i in range(N_ANCHORS):
    cols += [gated[:, i], reasons[:, i]]
    header += [f"A{i+1}_gated_m", f"A{i+1}_reason"]
    fmts += ["%.4f", "%d"]
np.savetxt("uwb_gated.csv", np.column_stack(cols), delimiter=",",
           header=",".join(header), comments="", fmt=fmts)

# =============================================================================
# PLOT
# =============================================================================
fig, axes = plt.subplots(N_ANCHORS, 1, figsize=(11, 10), sharex=True)
for i, ax in enumerate(axes):
    a = f"A{i+1}"
    meas, true = data[f"{a}_meas_m"], data[f"{a}_true_m"]
    ax.plot(t, true, color="black", lw=1.2, label="true")
    ax.plot(t, gated[:, i], ".", ms=2.5, color="tab:blue", label="accepted")
    rng_bad = reasons[:, i] == OUT_OF_RANGE
    jump = reasons[:, i] == JUMP
    ax.plot(t[rng_bad], meas[rng_bad], "s", mfc="none", color="tab:purple",
            ms=7, label="rejected: out of range")
    ax.plot(t[jump], meas[jump], "x", color="tab:red", ms=7,
            label="rejected: jump")
    ax.set_ylabel(f"{a} range (m)")
    ax.grid(alpha=0.3)
axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.45), ncol=4,
               fontsize=9)
axes[-1].set_xlabel("time (s)")
fig.suptitle("Step 2 - Gating: accepted vs rejected values", y=0.995)
fig.tight_layout(); fig.savefig("gating_result.png", dpi=120)
print("Saved: uwb_gated.csv, gating_result.png")
