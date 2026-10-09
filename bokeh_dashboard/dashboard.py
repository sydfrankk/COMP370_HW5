"""Bokeh dashboard"""

import csv
import os

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Select
from bokeh.plotting import figure

PATH = os.environ.get("MONTHLY_AVG", "data/monthly_avg.csv")

# Load the small precomputed file (zip, month, avg_hours)
lookup = {}          
month_set = set()

with open(PATH, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        z = row["zip"].strip()
        m = row["month"].strip()
        if not z or not m:
            continue
        try:
            hours = float(row["avg_hours"])
        except ValueError:
            continue
        lookup.setdefault(z, {})[m] = hours
        month_set.add(m)

months = sorted(month_set)
xs = list(range(len(months)))
zips = sorted(z for z in lookup if z != "ALL")


def series(z):
    """Average hours for zipcode z in each month (NaN where there is no data)."""
    d = lookup.get(z, {})
    return [d.get(m, float("nan")) for m in months]


# Data sources for the three curves
src_all = ColumnDataSource(dict(x=xs, y=series("ALL")))
src_1 = ColumnDataSource(dict(x=xs, y=series(zips[0])))
src_2 = ColumnDataSource(dict(x=xs, y=series(zips[1] if len(zips) > 1 else zips[0])))

# Dropdowns
sel1 = Select(title="Zipcode 1", value=zips[0], options=zips)
sel2 = Select(title="Zipcode 2", value=zips[1] if len(zips) > 1 else zips[0], options=zips)

# Plot
p = figure(
    width=900,
    height=450,
    title="Monthly average incident create-to-closed time",
    x_axis_label="Month (incident closed)",
    y_axis_label="Average response time (hours)",
)
p.xaxis.ticker = xs
p.xaxis.major_label_overrides = {i: m for i, m in enumerate(months)}
p.xaxis.major_label_orientation = 0.8

p.line("x", "y", source=src_all, color="black", line_width=2, legend_label="All zipcodes")
p.line("x", "y", source=src_1, color="blue", line_width=2, legend_label="Zipcode 1")
p.line("x", "y", source=src_2, color="red", line_width=2, legend_label="Zipcode 2")
p.legend.location = "top_left"


# Update when either dropdown changes
def update(attr, old, new):
    src_1.data = dict(x=xs, y=series(sel1.value))
    src_2.data = dict(x=xs, y=series(sel2.value))


sel1.on_change("value", update)
sel2.on_change("value", update)

# Single-column layout
curdoc().title = "311 Response Times"
curdoc().add_root(column(sel1, sel2, p))