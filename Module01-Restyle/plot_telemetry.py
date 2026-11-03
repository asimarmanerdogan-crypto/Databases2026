# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.10,<4"]
# ///
"""Plot the module's generated CSV without changing the recorded SQL reports.

Run from the repository root:
    uv run --no-project --script Module01-Restyle/plot_telemetry.py
"""
import csv
import runpy
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

HERE = Path(__file__).resolve().parent
CSV = HERE / "telemetry.csv"
if not CSV.exists():
    runpy.run_path(str(HERE / "generate_telemetry.py"), run_name="__main__")

bins = defaultdict(lambda: defaultdict(list))
alarms = defaultdict(int)
peaks = defaultdict(float)
counts = defaultdict(int)
with CSV.open(newline="", encoding="utf-8") as source:
    for row in csv.DictReader(source):
        timestamp = datetime.fromisoformat(row["ts"])
        bucket = timestamp.replace(minute=timestamp.minute // 15 * 15, second=0)
        machine, vibration = row["machine"], float(row["vib_rms"])
        bins[machine][bucket].append(vibration)
        counts[machine] += 1
        alarms[machine] += vibration > 2.0
        peaks[machine] = max(peaks[machine], vibration)

assert dict(counts) == {"cnc-01": 57600, "cnc-02": 57600, "cnc-03": 57600}
assert sum(alarms.values()) == 11714, "CSV differs from the recorded SQL results"
assert dict(peaks) == {"cnc-01": 2.398, "cnc-02": 3.168, "cnc-03": 2.55}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "svg.fonttype": "none", "savefig.facecolor": "#0b1420",
    "text.color": "#e2e8f0", "axes.labelcolor": "#94a3b8",
    "xtick.color": "#94a3b8", "ytick.color": "#94a3b8",
})
fig, axes = plt.subplots(3, 1, figsize=(12, 8.8), sharex=True, sharey=True)
fig.set_facecolor("#0b1420")
fig.subplots_adjust(left=.09, right=.96, top=.80, bottom=.17, hspace=.42)
fig.text(.09, .955, "MODULE 01  /  TELEMETRY", color="#5eead4", fontsize=11,
         fontfamily="DejaVu Sans Mono")
fig.text(.09, .91, "Vibration over 48 hours", fontsize=25, weight="bold")
fig.text(.09, .873, "172,800 simulated readings  ·  3 machines  ·  3-second sampling",
         color="#94a3b8", fontsize=11)
colors = ["#38bdf8", "#2dd4bf", "#a5b4fc"]
for ax, machine, color in zip(axes, sorted(bins), colors):
    times = sorted(bins[machine])
    centers = [t + timedelta(minutes=7, seconds=30) for t in times]
    values = [bins[machine][t] for t in times]
    means = [sum(v) / len(v) for v in values]
    ax.set_facecolor("#101e2e")
    ax.fill_between(centers, [min(v) for v in values], [max(v) for v in values],
                    color=color, alpha=.15, linewidth=0)
    ax.plot(centers, means, color=color, linewidth=1.8)
    ax.axhline(2.0, color="#fbbf24", linewidth=1, linestyle=(0, (5, 4)))
    ax.set_title(machine.upper(), loc="left", fontsize=11, weight="bold", color=color, pad=9)
    ax.set_title(f"{alarms[machine]:,} alarm readings  |  peak {peaks[machine]:.3f}",
                 loc="right", fontsize=9, color="#cbd5e1", pad=9)
    ax.set_ylim(.5, 3.4)
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.grid(axis="y", color="#334155", alpha=.45, linewidth=.6)
    ax.set_ylabel("vib_rms", fontsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="both", length=0, pad=8)
axes[-1].set_xlim(min(bins["cnc-01"]), max(bins["cnc-01"]) + timedelta(minutes=15))
axes[-1].xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%d Jan\n%H:%M"))
fig.text(.09, .071, "Line: 15-minute mean    Shaded area: minimum–maximum within each interval",
         color="#cbd5e1", fontsize=10)
fig.text(.09, .041, "Dashed line: alarm threshold > 2.0    ·    Alarm counts use all original readings.",
         color="#94a3b8", fontsize=9)
assets = HERE / "assets"
assets.mkdir(exist_ok=True)
fig.savefig(assets / "telemetry-vibration.png", dpi=180)
fig.savefig(assets / "telemetry-vibration.svg")
plt.close(fig)
print(f"Verified {sum(counts.values()):,} rows, {sum(alarms.values()):,} alarms and all three SQL peaks.")
print("Saved assets/telemetry-vibration.png and assets/telemetry-vibration.svg")
