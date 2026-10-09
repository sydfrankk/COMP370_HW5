#!/usr/bin/env python3
"""Process data before dashboard calculation."""
import csv
import sys
from collections import defaultdict
from datetime import datetime

FMT = "%m/%d/%Y %I:%M:%S %p"


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: preprocess.py <input.csv> <output.csv>")
    inp, out = sys.argv[1], sys.argv[2]

    sums = defaultdict(float)    
    counts = defaultdict(int)   

    with open(inp, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            zipc = row["Incident Zip"].strip()
            created = row["Created Date"].strip()
            closed = row["Closed Date"].strip()

            # drop: no zipcode, or not yet closed
            if not zipc or not closed:
                continue
            try:
                c = datetime.strptime(created, FMT)
                cl = datetime.strptime(closed, FMT)
            except ValueError:
                continue

            # only incidents opened in 2024
            if c.year != 2024:
                continue

            hours = (cl - c).total_seconds() / 3600
            if hours < 0:               # closed before opened
                continue

            month = cl.strftime("%Y-%m")   # bucket by CLOSED month
            for key in ((zipc, month), ("ALL", month)):
                sums[key] += hours
                counts[key] += 1

    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["zip", "month", "avg_hours"])
        for key in sorted(sums):
            w.writerow([key[0], key[1], round(sums[key] / counts[key], 4)])

    print(f"wrote {out}")


if __name__ == "__main__":
    main()