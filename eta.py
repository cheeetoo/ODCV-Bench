#!/usr/bin/env python3
"""Progress + ETA for a running benchmark campaign. Run from the repo root.

Counts completed scenario folders (results/*/experiments/* plus all but the
newest folder under experiments/), derives the average minutes per scenario
from their completion mtimes, and projects the remaining time for the
current 80-scenario model run (40 mandated + 40 incentivized).
"""
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Scenarios this checkout will run: 80 for a full model campaign (default),
# 40 for a worker running a single --variations split. Override: eta.py 40
PER_MODEL = int(sys.argv[1]) if len(sys.argv) > 1 else 80

root = Path(__file__).resolve().parent

# Completed scenarios already moved into results/
moved = [p.stat().st_mtime for p in root.glob("results/*/experiments/*") if p.is_dir()]

# Scenarios in the in-progress variation: newest folder is in flight, rest are done
inflight = sorted(
    (p for p in (root / "experiments").glob("*") if p.is_dir()),
    key=lambda p: p.stat().st_mtime,
)
current = inflight[-1] if inflight else None
done_times = sorted(moved + [p.stat().st_mtime for p in inflight[:-1]])

n_done = len(done_times)
print(f"Completed scenarios (this campaign): {n_done}")
if current:
    mins = (time.time() - current.stat().st_mtime) / 60
    print(f"In flight: {current.name} (~{mins:.0f} min so far)")

if n_done >= 2:
    span = done_times[-1] - done_times[0]
    per = span / (n_done - 1)
    remaining = PER_MODEL - n_done - (1 if current else 0)
    eta_s = remaining * per + (per / 2 if current else 0)
    eta = datetime.now() + timedelta(seconds=eta_s)
    print(f"Avg per scenario: {per / 60:.1f} min")
    print(f"Remaining for this model ({remaining} + in-flight): ~{eta_s / 3600:.1f} h")
    print(f"ETA (this model, both variations): {eta:%a %H:%M}")
    print(f"Second model will need roughly the same again (~{PER_MODEL * per / 3600:.1f} h)")
else:
    print("Need >=2 completed scenarios to estimate a rate - check back in ~15 min.")
