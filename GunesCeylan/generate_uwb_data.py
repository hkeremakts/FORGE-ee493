"""
RAPTOR - Synthetic UWB range data generator
============================================
Pretends to be the UWB system: a robot drives through a 10 m x 10 m arena
with 4 anchors in the corners. For every time step it computes the TRUE
distance to each anchor, then adds realistic errors on purpose.

Output:
  uwb_synthetic.csv   -> the data (true values, measured values, error labels)
  arena_path.png      -> map of the arena, anchors and robot path
  ranges_over_time.png-> measured vs true distance for each anchor

All numbers in the CONFIG section are ASSUMPTIONS. Replace them with values
measured from the real DWM3001CDK boards once you have them.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")            # draw plots to files, no window needed
import matplotlib.pyplot as plt

# =============================================================================
# CONFIG - every setting in one place
# =============================================================================
SEED = 42                        # fixed random seed -> same data every run

# --- Arena and anchors -------------------------------------------------------
ANCHORS = np.array([             # (x, y) of the 4 anchors in metres
    [0.0,  0.0],                 # A1 bottom-left
    [10.0, 0.0],                 # A2 bottom-right
    [10.0, 10.0],                # A3 top-right
    [0.0,  10.0],                # A4 top-left
])
ANCHOR_HEIGHT = 2.0              # anchors mounted 2 m high (m)
TAG_HEIGHT = 0.3                 # UWB tag on the robot, 0.3 m high (m)

# --- Timing ------------------------------------------------------------------
RATE_HZ = 10                     # measurements per second (FR1.2: >= 10 Hz)
DURATION_S = 120                 # length of the recording (s)

# --- Robot path ---------------------------------------------------------------
WAYPOINTS = np.array([           # robot visits these in order, then loops
    [1.0, 1.0],                  # start (safe zone)
    [8.0, 2.0],
    [8.0, 8.0],
    [5.0, 5.0],
    [2.0, 8.0],
    [1.0, 1.0],                  # back to start
])
ROBOT_SPEED = 0.8                # m/s (target moves <= 1.0 m/s)

# --- Error 1: random noise ---------------------------------------------------
NOISE_STD = 0.05                 # 5 cm standard deviation

# --- Error 2: constant offset of each board (antenna delay) ------------------
OFFSETS = np.array([0.15, 0.22, 0.10, 0.18])   # metres, one per anchor

# --- Error 3: spikes ---------------------------------------------------------
SPIKE_PROB = 0.01                # 1 % of measurements are spikes
SPIKE_MIN, SPIKE_MAX = 0.5, 3.0  # spike size between 0.5 and 3 m (+ or -)

# --- Error 4: NLOS (anchor blocked -> reads too long, noisier) ---------------
NLOS_ANCHOR = 1                  # index 1 = A2
NLOS_START, NLOS_END = 40.0, 55.0  # seconds
NLOS_BIAS = 0.40                 # extra +40 cm while blocked
NLOS_EXTRA_NOISE = 0.15          # extra 15 cm noise while blocked

# --- Error 5: missing values (dropouts) --------------------------------------
DROPOUT_PROB = 0.02              # 2 % random missing values
DEAD_ANCHOR = 2                  # index 2 = A3 stops answering completely...
DEAD_START, DEAD_END = 80.0, 90.0  # ...between these times (s)


# =============================================================================
# STEP A - time axis
# =============================================================================
rng = np.random.default_rng(SEED)
dt = 1.0 / RATE_HZ
t = np.arange(0.0, DURATION_S, dt)          # 0.0, 0.1, 0.2, ... seconds
n_steps = len(t)
n_anchors = len(ANCHORS)


# =============================================================================
# STEP B - robot position at every time step
# =============================================================================
# Length of each straight segment between consecutive waypoints
segment_lengths = np.linalg.norm(np.diff(WAYPOINTS, axis=0), axis=1)
# Distance along the path at which each waypoint is reached: 0, L1, L1+L2, ...
cumulative = np.concatenate([[0.0], np.cumsum(segment_lengths)])
loop_length = cumulative[-1]

# Distance travelled at each time, wrapped so the robot keeps looping
s = (ROBOT_SPEED * t) % loop_length
# Convert "distance along path" into (x, y) by interpolating between waypoints
robot_x = np.interp(s, cumulative, WAYPOINTS[:, 0])
robot_y = np.interp(s, cumulative, WAYPOINTS[:, 1])


# =============================================================================
# STEP C - TRUE distance from the robot to each anchor (3D, includes height)
# =============================================================================
dx = robot_x[:, None] - ANCHORS[None, :, 0]     # shape (n_steps, 4)
dy = robot_y[:, None] - ANCHORS[None, :, 1]
dz = TAG_HEIGHT - ANCHOR_HEIGHT
true_range = np.sqrt(dx**2 + dy**2 + dz**2)


# =============================================================================
# STEP D - add the errors, one type at a time, and remember where they are
# =============================================================================
measured = true_range.copy()

# Error 2: constant offset (same every time for a given anchor)
measured += OFFSETS[None, :]

# Error 1: random noise (different every sample)
measured += rng.normal(0.0, NOISE_STD, size=measured.shape)

# Error 4: NLOS on one anchor during a time window
is_nlos = np.zeros(measured.shape, dtype=int)
nlos_rows = (t >= NLOS_START) & (t < NLOS_END)
is_nlos[nlos_rows, NLOS_ANCHOR] = 1
measured[nlos_rows, NLOS_ANCHOR] += NLOS_BIAS
measured[nlos_rows, NLOS_ANCHOR] += rng.normal(0.0, NLOS_EXTRA_NOISE,
                                               size=nlos_rows.sum())

# Error 3: spikes at random places, random size and sign
is_spike = (rng.random(measured.shape) < SPIKE_PROB).astype(int)
spike_size = rng.uniform(SPIKE_MIN, SPIKE_MAX, size=measured.shape)
spike_sign = rng.choice([-1.0, 1.0], size=measured.shape)
measured += is_spike * spike_size * spike_sign

# Error 5: missing values -> NaN ("not a number" = no measurement)
is_dropout = (rng.random(measured.shape) < DROPOUT_PROB).astype(int)
dead_rows = (t >= DEAD_START) & (t < DEAD_END)
is_dropout[dead_rows, DEAD_ANCHOR] = 1
measured[is_dropout == 1] = np.nan
is_spike[is_dropout == 1] = 0      # a missing value can't also be a spike


# =============================================================================
# STEP E - save everything to a CSV file
# =============================================================================
columns = [t, robot_x, robot_y]
header = ["time_s", "true_x_m", "true_y_m"]
formats = ["%.1f", "%.4f", "%.4f"]          # numbers with decimals
for i in range(n_anchors):
    a = f"A{i+1}"
    columns += [true_range[:, i], measured[:, i],
                is_spike[:, i], is_nlos[:, i], is_dropout[:, i]]
    header += [f"{a}_true_m", f"{a}_meas_m",
               f"{a}_spike", f"{a}_nlos", f"{a}_dropout"]
    formats += ["%.4f", "%.4f", "%d", "%d", "%d"]   # labels as 0 / 1

np.savetxt("uwb_synthetic.csv", np.column_stack(columns), delimiter=",",
           header=",".join(header), comments="", fmt=formats)


# =============================================================================
# STEP F - plots to check the data looks right
# =============================================================================
# Plot 1: arena map
fig, ax = plt.subplots(figsize=(6, 6.6))
ax.plot(robot_x, robot_y, color="tab:blue", lw=1, label="robot path")
ax.scatter(WAYPOINTS[:-1, 0], WAYPOINTS[:-1, 1], color="tab:green",
           zorder=3, label="waypoints")
ax.scatter(ANCHORS[:, 0], ANCHORS[:, 1], color="tab:red", marker="^",
           s=120, zorder=3, label="anchors")
for i, (x, y) in enumerate(ANCHORS):
    ax.annotate(f"A{i+1}", (x, y), textcoords="offset points",
                xytext=(8, 8), fontsize=11)
ax.set_xlim(-1, 11); ax.set_ylim(-1, 11); ax.set_aspect("equal")
ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
ax.set_title("Synthetic arena: anchors and robot path")
ax.grid(alpha=0.3)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
fig.tight_layout(); fig.savefig("arena_path.png", dpi=120)

# Plot 2: measured vs true range for each anchor
fig, axes = plt.subplots(n_anchors, 1, figsize=(11, 10), sharex=True)
for i, ax in enumerate(axes):
    ax.plot(t, true_range[:, i], color="black", lw=1.2, label="true")
    ax.plot(t, measured[:, i], ".", ms=2.5, color="tab:blue",
            label="measured")
    sp = is_spike[:, i] == 1
    ax.plot(t[sp], measured[sp, i], "x", color="tab:red", ms=7,
            label="spike")
    if i == NLOS_ANCHOR:
        ax.axvspan(NLOS_START, NLOS_END, color="orange", alpha=0.25,
                   label="NLOS")
    if i == DEAD_ANCHOR:
        ax.axvspan(DEAD_START, DEAD_END, color="gray", alpha=0.3,
                   label="anchor dead")
    ax.set_ylabel(f"A{i+1} range (m)")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8, ncol=5)
axes[-1].set_xlabel("time (s)")
fig.suptitle("Synthetic UWB ranges: measured vs true")
fig.tight_layout(); fig.savefig("ranges_over_time.png", dpi=120)

# Short summary in the terminal
print(f"Samples: {n_steps} time steps x {n_anchors} anchors")
print(f"Spikes:   {is_spike.sum()}")
print(f"Dropouts: {is_dropout.sum()}")
print(f"NLOS samples: {is_nlos.sum()}")
print("Saved: uwb_synthetic.csv, arena_path.png, ranges_over_time.png")
