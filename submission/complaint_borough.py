#!/usr/bin/env python3
"""Build a python-based command line tool borough_complaints.py that uses argparse to provide a UNIX-style command which outputs the number of each complaint type per borough for a given (creation) date range.
"""
import argparse
import csv
import sys
from collections import Counter
from datetime import datetime, timedelta

ROW_FORMATS = ("%m/%d/%Y %I:%M:%S %p", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S")

def parse_arg_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{s}' is not a valid date, use YYYY-MM-DD")


def parse_row_date(s):
    for fmt in ROW_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def main():
    p = argparse.ArgumentParser(
        description="Count complaints of each type per borough for incidents "
                    "created within a date range (inclusive). Output is CSV.")
    p.add_argument("-i", "--input", required=True, help="input 311 CSV file")
    p.add_argument("-s", "--start", required=True, type=parse_arg_date,
                   help="start date, YYYY-MM-DD (inclusive)")
    p.add_argument("-e", "--end", required=True, type=parse_arg_date,
                   help="end date, YYYY-MM-DD (inclusive)")
    p.add_argument("-o", "--output", help="output file (default: stdout)")
    args = p.parse_args()

    start = args.start
    end = args.end + timedelta(days=1)  # make end date inclusive
    if end <= start:
        p.error("end date must not be before start date")

    counts = Counter()
    with open(args.input, newline="", encoding="utf-8") as f:
        # stream row by row, no pandas, so big files are fine
        for row in csv.DictReader(f):
            created = parse_row_date(row["Created Date"])
            if created is None or not (start <= created < end):
                continue
            counts[(row["Complaint Type"], row["Borough"])] += 1

    out = open(args.output, "w", newline="") if args.output else sys.stdout
    try:
        w = csv.writer(out)
        w.writerow(["complaint type", "borough", "count"])
        for (ctype, boro), n in sorted(counts.items(), key=lambda kv: (kv[0][0], -kv[1])):
            w.writerow([ctype, boro, n])
    finally:
        if args.output:
            out.close()


if __name__ == "__main__":
    main()
