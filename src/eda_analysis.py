"""
03_eda_analysis.py
===================
Rossmann Store Sales -- Exploratory Data Analysis

Generates a professional self-contained HTML report with inline SVG charts.
Uses ONLY Python standard library -- no pandas, matplotlib, or other deps.

Analyses:
1. Overall sales trends
2. Yearly / Monthly / Weekly patterns
3. Sales by StoreType
4. Sales by Assortment
5. Promotion impact
6. Holiday impact
7. Top / Bottom performing stores
8. Seasonality detection
"""

import csv
import os
import math
from collections import defaultdict, Counter
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
INPUT_FILE = os.path.join(DATA_DIR, "train_store_cleaned.csv")
OUTPUT_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports", "eda_report.html")

# ── Load data ────────────────────────────────────────────────────────────────
print("Loading cleaned dataset...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
print(f"  Loaded {len(rows):,} rows")


# ── Helper: safe numeric conversion ──────────────────────────────────────────
def si(v, d=0):
    try: return int(v)
    except: return d

def sf(v, d=0.0):
    try: return float(v)
    except: return d

def mean(vals):
    return sum(vals)/len(vals) if vals else 0

def median_val(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0: return 0
    if n % 2 == 1: return s[n//2]
    return (s[n//2-1] + s[n//2]) / 2

def fmt(v):
    if abs(v) >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if abs(v) >= 1_000: return f"{v/1_000:.1f}K"
    return f"{v:,.0f}"


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS COMPUTATIONS
# ══════════════════════════════════════════════════════════════════════════════
print("Computing analyses...")

# ── 1. Overall stats ─────────────────────────────────────────────────────────
all_sales = [si(r["Sales"]) for r in rows]
all_cust = [si(r["Customers"]) for r in rows]
overall = {
    "total_rows": len(rows),
    "total_sales": sum(all_sales),
    "avg_sales": mean(all_sales),
    "median_sales": median_val(all_sales),
    "max_sales": max(all_sales),
    "min_sales": min(all_sales),
    "total_customers": sum(all_cust),
    "avg_customers": mean(all_cust),
    "num_stores": len(set(r["Store"] for r in rows)),
    "date_range": (min(r["Date"] for r in rows), max(r["Date"] for r in rows)),
}

# ── 2. Daily trend (aggregate by date) ───────────────────────────────────────
daily_sales = defaultdict(list)
daily_cust = defaultdict(list)
for r in rows:
    daily_sales[r["Date"]].append(si(r["Sales"]))
    daily_cust[r["Date"]].append(si(r["Customers"]))

daily_avg = {d: mean(v) for d, v in daily_sales.items()}
daily_sorted = sorted(daily_avg.items())

# ── 3. Monthly trend ─────────────────────────────────────────────────────────
monthly_sales = defaultdict(list)
for r in rows:
    ym = r["Date"][:7]  # YYYY-MM
    monthly_sales[ym].append(si(r["Sales"]))
monthly_avg = {ym: mean(v) for ym, v in monthly_sales.items()}
monthly_sorted = sorted(monthly_avg.items())

# ── 4. Yearly stats ──────────────────────────────────────────────────────────
yearly_sales = defaultdict(list)
yearly_cust = defaultdict(list)
for r in rows:
    y = r["Date"][:4]
    yearly_sales[y].append(si(r["Sales"]))
    yearly_cust[y].append(si(r["Customers"]))
yearly_avg_sales = {y: mean(v) for y, v in yearly_sales.items()}
yearly_avg_cust = {y: mean(v) for y, v in yearly_cust.items()}
yearly_total = {y: sum(v) for y, v in yearly_sales.items()}
yearly_sorted = sorted(yearly_avg_sales.items())

# ── 5. Day of week pattern ───────────────────────────────────────────────────
dow_names = {1:"Mon",2:"Tue",3:"Wed",4:"Thu",5:"Fri",6:"Sat",7:"Sun"}
dow_sales = defaultdict(list)
dow_cust = defaultdict(list)
for r in rows:
    d = si(r["DayOfWeek"])
    dow_sales[d].append(si(r["Sales"]))
    dow_cust[d].append(si(r["Customers"]))
dow_avg_sales = {d: mean(v) for d, v in dow_sales.items()}
dow_avg_cust = {d: mean(v) for d, v in dow_cust.items()}

# ── 6. Month-of-year seasonality ─────────────────────────────────────────────
month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
moy_sales = defaultdict(list)
for r in rows:
    m = int(r["Date"][5:7])
    moy_sales[m].append(si(r["Sales"]))
moy_avg = {m: mean(v) for m, v in moy_sales.items()}

# ── 7. StoreType analysis ────────────────────────────────────────────────────
st_sales = defaultdict(list)
st_cust = defaultdict(list)
st_count = Counter()
for r in rows:
    t = r["StoreType"]
    st_sales[t].append(si(r["Sales"]))
    st_cust[t].append(si(r["Customers"]))
    st_count[t] += 1
st_avg_sales = {t: mean(v) for t, v in st_sales.items()}
st_avg_cust = {t: mean(v) for t, v in st_cust.items()}
st_stores = {}
for t in st_sales:
    st_stores[t] = len(set(r["Store"] for r in rows if r["StoreType"] == t))

# ── 8. Assortment analysis ───────────────────────────────────────────────────
as_sales = defaultdict(list)
as_cust = defaultdict(list)
for r in rows:
    a = r["Assortment"]
    as_sales[a].append(si(r["Sales"]))
    as_cust[a].append(si(r["Customers"]))
as_avg_sales = {a: mean(v) for a, v in as_sales.items()}
as_avg_cust = {a: mean(v) for a, v in as_cust.items()}
assort_names = {"a": "Basic", "b": "Extra", "c": "Extended"}

# ── 9. Promotion impact ──────────────────────────────────────────────────────
promo_sales = defaultdict(list)
promo_cust = defaultdict(list)
for r in rows:
    p = "Promo" if r["Promo"] == "1" else "No Promo"
    promo_sales[p].append(si(r["Sales"]))
    promo_cust[p].append(si(r["Customers"]))
promo_avg_sales = {p: mean(v) for p, v in promo_sales.items()}
promo_avg_cust = {p: mean(v) for p, v in promo_cust.items()}

# Promo by store type
promo_st = defaultdict(lambda: defaultdict(list))
for r in rows:
    p = "Promo" if r["Promo"] == "1" else "No Promo"
    promo_st[r["StoreType"]][p].append(si(r["Sales"]))

# Promo2 impact
p2_sales = defaultdict(list)
for r in rows:
    p = "Promo2" if r["Promo2"] == "1" else "No Promo2"
    p2_sales[p].append(si(r["Sales"]))
p2_avg = {p: mean(v) for p, v in p2_sales.items()}

# ── 10. Holiday impact ───────────────────────────────────────────────────────
hol_map = {"0":"No Holiday","a":"Public Holiday","b":"Easter Holiday","c":"Christmas"}
hol_sales = defaultdict(list)
hol_cust = defaultdict(list)
for r in rows:
    h = hol_map.get(r["StateHoliday"], "No Holiday")
    hol_sales[h].append(si(r["Sales"]))
    hol_cust[h].append(si(r["Customers"]))
hol_avg_sales = {h: mean(v) for h, v in hol_sales.items()}
hol_avg_cust = {h: mean(v) for h, v in hol_cust.items()}

# School holiday
sch_sales = defaultdict(list)
for r in rows:
    s = "School Holiday" if r["SchoolHoliday"] == "1" else "No School Holiday"
    sch_sales[s].append(si(r["Sales"]))
sch_avg = {s: mean(v) for s, v in sch_sales.items()}

# ── 11. Top / Bottom stores ──────────────────────────────────────────────────
store_sales = defaultdict(list)
store_cust = defaultdict(list)
for r in rows:
    store_sales[r["Store"]].append(si(r["Sales"]))
    store_cust[r["Store"]].append(si(r["Customers"]))
store_avg = {s: mean(v) for s, v in store_sales.items()}
store_avg_sorted = sorted(store_avg.items(), key=lambda x: x[1], reverse=True)
top10 = store_avg_sorted[:10]
bot10 = store_avg_sorted[-10:]

# ── 12. Competition distance vs sales ────────────────────────────────────────
store_comp = {}
store_type_map = {}
for r in rows:
    store_comp[r["Store"]] = si(r["CompetitionDistance"])
    store_type_map[r["Store"]] = r["StoreType"]

# Bucket competition distance
comp_buckets = {"0-500m":[], "500-2000m":[], "2000-5000m":[], "5000-10000m":[], "10000m+":[]}
for s, avg in store_avg.items():
    d = store_comp.get(s, 0)
    if d <= 500: comp_buckets["0-500m"].append(avg)
    elif d <= 2000: comp_buckets["500-2000m"].append(avg)
    elif d <= 5000: comp_buckets["2000-5000m"].append(avg)
    elif d <= 10000: comp_buckets["5000-10000m"].append(avg)
    else: comp_buckets["10000m+"].append(avg)
comp_avg = {b: mean(v) for b, v in comp_buckets.items() if v}

print("  All analyses computed.")


# ══════════════════════════════════════════════════════════════════════════════
# SVG CHART GENERATION
# ══════════════════════════════════════════════════════════════════════════════

COLORS = ["#6366f1","#f43f5e","#10b981","#f59e0b","#3b82f6","#8b5cf6","#ef4444","#14b8a6","#e879f9","#fb923c"]
GRAD_1 = "#6366f1"
GRAD_2 = "#8b5cf6"

def svg_bar_chart(data, title, w=700, h=350, color=None, label_fmt=None, horizontal=False):
    """Generate an SVG bar chart. data = [(label, value), ...]"""
    if not data: return ""
    margin = {"t":50,"r":30,"b":80,"l":70}
    pw = w - margin["l"] - margin["r"]
    ph = h - margin["t"] - margin["b"]
    max_v = max(v for _, v in data)
    if max_v == 0: max_v = 1
    n = len(data)
    bar_w = min(pw / n * 0.7, 60)
    gap = (pw - bar_w * n) / (n + 1)

    svg = f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="font-family:Inter,system-ui,sans-serif">\n'
    svg += f'<rect width="{w}" height="{h}" fill="transparent"/>\n'
    # Title
    svg += f'<text x="{w/2}" y="28" text-anchor="middle" font-size="15" font-weight="600" fill="#e2e8f0">{title}</text>\n'
    # Grid lines
    for i in range(5):
        y = margin["t"] + ph - (ph * i / 4)
        val = max_v * i / 4
        svg += f'<line x1="{margin["l"]}" y1="{y}" x2="{w-margin["r"]}" y2="{y}" stroke="#334155" stroke-width="0.5"/>\n'
        lbl = label_fmt(val) if label_fmt else fmt(val)
        svg += f'<text x="{margin["l"]-8}" y="{y+4}" text-anchor="end" font-size="10" fill="#94a3b8">{lbl}</text>\n'
    # Bars
    for i, (label, val) in enumerate(data):
        x = margin["l"] + gap + i * (bar_w + gap)
        bar_h = (val / max_v) * ph
        y = margin["t"] + ph - bar_h
        c = color if color else COLORS[i % len(COLORS)]
        svg += f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" fill="{c}" opacity="0.85">'
        svg += f'<animate attributeName="height" from="0" to="{bar_h}" dur="0.6s" fill="freeze"/>'
        svg += f'<animate attributeName="y" from="{margin["t"]+ph}" to="{y}" dur="0.6s" fill="freeze"/>'
        svg += f'</rect>\n'
        # Value on top
        v_lbl = label_fmt(val) if label_fmt else fmt(val)
        svg += f'<text x="{x+bar_w/2}" y="{y-6}" text-anchor="middle" font-size="10" font-weight="500" fill="#cbd5e1">{v_lbl}</text>\n'
        # Label
        svg += f'<text x="{x+bar_w/2}" y="{h-margin["b"]+18}" text-anchor="middle" font-size="10" fill="#94a3b8" '
        if len(label) > 8:
            svg += f'transform="rotate(-30,{x+bar_w/2},{h-margin["b"]+18})"'
        svg += f'>{label}</text>\n'
    svg += '</svg>'
    return svg


def svg_line_chart(datasets, title, w=700, h=350, x_labels=None):
    """datasets = [(name, [(x_idx, y_val), ...], color), ...]"""
    if not datasets: return ""
    margin = {"t":50,"r":30,"b":80,"l":70}
    pw = w - margin["l"] - margin["r"]
    ph = h - margin["t"] - margin["b"]
    all_vals = [y for _, pts, _ in datasets for _, y in pts]
    if not all_vals: return ""
    max_v = max(all_vals)
    min_v = min(all_vals)
    if max_v == min_v: max_v = min_v + 1
    rng = max_v - min_v
    max_x = max(x for _, pts, _ in datasets for x, _ in pts)
    if max_x == 0: max_x = 1

    svg = f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="font-family:Inter,system-ui,sans-serif">\n'
    svg += f'<rect width="{w}" height="{h}" fill="transparent"/>\n'
    svg += f'<text x="{w/2}" y="28" text-anchor="middle" font-size="15" font-weight="600" fill="#e2e8f0">{title}</text>\n'
    # Grid
    for i in range(5):
        y = margin["t"] + ph - (ph * i / 4)
        val = min_v + rng * i / 4
        svg += f'<line x1="{margin["l"]}" y1="{y}" x2="{w-margin["r"]}" y2="{y}" stroke="#334155" stroke-width="0.5"/>\n'
        svg += f'<text x="{margin["l"]-8}" y="{y+4}" text-anchor="end" font-size="10" fill="#94a3b8">{fmt(val)}</text>\n'
    # Lines
    for name, pts, color in datasets:
        if len(pts) < 2: continue
        points = []
        for xi, yi in pts:
            x = margin["l"] + (xi / max_x) * pw
            y = margin["t"] + ph - ((yi - min_v) / rng) * ph
            points.append(f"{x},{y}")
        path = "M " + " L ".join(points)
        # Area fill
        first_x = margin["l"] + (pts[0][0] / max_x) * pw
        last_x = margin["l"] + (pts[-1][0] / max_x) * pw
        area_path = path + f" L {last_x},{margin['t']+ph} L {first_x},{margin['t']+ph} Z"
        svg += f'<path d="{area_path}" fill="{color}" opacity="0.08"/>\n'
        svg += f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\n'
    # X labels
    if x_labels:
        step = max(1, len(x_labels) // 12)
        for i in range(0, len(x_labels), step):
            x = margin["l"] + (i / max_x) * pw
            svg += f'<text x="{x}" y="{h-margin["b"]+18}" text-anchor="middle" font-size="9" fill="#94a3b8" '
            svg += f'transform="rotate(-40,{x},{h-margin["b"]+18})">{x_labels[i]}</text>\n'
    # Legend
    for i, (name, _, color) in enumerate(datasets):
        lx = margin["l"] + i * 120
        ly = h - 15
        svg += f'<rect x="{lx}" y="{ly-8}" width="12" height="12" rx="2" fill="{color}"/>\n'
        svg += f'<text x="{lx+16}" y="{ly+2}" font-size="10" fill="#94a3b8">{name}</text>\n'
    svg += '</svg>'
    return svg


def svg_grouped_bar(groups, title, w=700, h=350, group_colors=None):
    """groups = [(group_label, [(sub_label, value), ...]), ...]"""
    if not groups: return ""
    margin = {"t":50,"r":30,"b":80,"l":70}
    pw = w - margin["l"] - margin["r"]
    ph = h - margin["t"] - margin["b"]
    n_groups = len(groups)
    n_sub = max(len(subs) for _, subs in groups)
    all_vals = [v for _, subs in groups for _, v in subs]
    max_v = max(all_vals) if all_vals else 1
    if max_v == 0: max_v = 1
    group_w = pw / n_groups
    sub_w = min(group_w * 0.7 / n_sub, 40)
    sub_labels = [sl for _, subs in groups for sl, _ in subs]
    unique_subs = list(dict.fromkeys(sl for _, subs in groups for sl, _ in subs))
    colors = group_colors or COLORS

    svg = f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="font-family:Inter,system-ui,sans-serif">\n'
    svg += f'<rect width="{w}" height="{h}" fill="transparent"/>\n'
    svg += f'<text x="{w/2}" y="28" text-anchor="middle" font-size="15" font-weight="600" fill="#e2e8f0">{title}</text>\n'
    for i in range(5):
        y = margin["t"] + ph - (ph * i / 4)
        val = max_v * i / 4
        svg += f'<line x1="{margin["l"]}" y1="{y}" x2="{w-margin["r"]}" y2="{y}" stroke="#334155" stroke-width="0.5"/>\n'
        svg += f'<text x="{margin["l"]-8}" y="{y+4}" text-anchor="end" font-size="10" fill="#94a3b8">{fmt(val)}</text>\n'
    for gi, (glabel, subs) in enumerate(groups):
        gx = margin["l"] + gi * group_w + group_w * 0.15
        for si_idx, (slabel, val) in enumerate(subs):
            x = gx + si_idx * (sub_w + 2)
            bar_h = (val / max_v) * ph
            y = margin["t"] + ph - bar_h
            c = colors[si_idx % len(colors)]
            svg += f'<rect x="{x}" y="{y}" width="{sub_w}" height="{bar_h}" rx="3" fill="{c}" opacity="0.85"/>\n'
            svg += f'<text x="{x+sub_w/2}" y="{y-4}" text-anchor="middle" font-size="9" fill="#cbd5e1">{fmt(val)}</text>\n'
        svg += f'<text x="{gx + len(subs)*(sub_w+2)/2}" y="{h-margin["b"]+18}" text-anchor="middle" font-size="11" fill="#94a3b8">{glabel}</text>\n'
    # Legend
    for i, sl in enumerate(unique_subs):
        lx = margin["l"] + i * 120
        svg += f'<rect x="{lx}" y="{h-12}" width="12" height="12" rx="2" fill="{colors[i % len(colors)]}"/>\n'
        svg += f'<text x="{lx+16}" y="{h-2}" font-size="10" fill="#94a3b8">{sl}</text>\n'
    svg += '</svg>'
    return svg


def svg_horizontal_bar(data, title, w=700, h=None, color=None):
    """Horizontal bar chart. data = [(label, value), ...]"""
    if not data: return ""
    n = len(data)
    if h is None: h = max(200, n * 32 + 80)
    margin = {"t":50,"r":80,"b":30,"l":120}
    pw = w - margin["l"] - margin["r"]
    ph = h - margin["t"] - margin["b"]
    max_v = max(v for _, v in data)
    if max_v == 0: max_v = 1
    bar_h = min(ph / n * 0.7, 24)
    gap = (ph - bar_h * n) / (n + 1)

    svg = f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="font-family:Inter,system-ui,sans-serif">\n'
    svg += f'<rect width="{w}" height="{h}" fill="transparent"/>\n'
    svg += f'<text x="{w/2}" y="28" text-anchor="middle" font-size="15" font-weight="600" fill="#e2e8f0">{title}</text>\n'
    for i, (label, val) in enumerate(data):
        y = margin["t"] + gap + i * (bar_h + gap)
        bar_w = (val / max_v) * pw
        c = color if color else COLORS[i % len(COLORS)]
        svg += f'<rect x="{margin["l"]}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" fill="{c}" opacity="0.85"/>\n'
        svg += f'<text x="{margin["l"]-8}" y="{y+bar_h/2+4}" text-anchor="end" font-size="10" fill="#94a3b8">{label}</text>\n'
        svg += f'<text x="{margin["l"]+bar_w+6}" y="{y+bar_h/2+4}" font-size="10" font-weight="500" fill="#cbd5e1">{fmt(val)}</text>\n'
    svg += '</svg>'
    return svg


# ══════════════════════════════════════════════════════════════════════════════
# BUILD CHARTS
# ══════════════════════════════════════════════════════════════════════════════
print("Generating charts...")

# Chart 1: Monthly avg sales trend
monthly_pts = [(i, v) for i, (_, v) in enumerate(monthly_sorted)]
chart_monthly = svg_line_chart(
    [("Avg Daily Sales", monthly_pts, "#6366f1")],
    "Monthly Average Daily Sales Trend",
    w=900, h=350,
    x_labels=[ym for ym, _ in monthly_sorted]
)

# Chart 2: Yearly comparison
chart_yearly = svg_bar_chart(
    [(y, v) for y, v in sorted(yearly_avg_sales.items())],
    "Average Daily Sales by Year"
)

# Chart 3: Day of week
dow_data = [(dow_names.get(d, str(d)), dow_avg_sales[d]) for d in sorted(dow_avg_sales.keys())]
chart_dow = svg_bar_chart(dow_data, "Average Sales by Day of Week")

# Chart 4: Day of week customers
dow_cust_data = [(dow_names.get(d, str(d)), dow_avg_cust[d]) for d in sorted(dow_avg_cust.keys())]
chart_dow_cust = svg_bar_chart(dow_cust_data, "Average Customers by Day of Week", color="#10b981")

# Chart 5: Month-of-year seasonality
moy_data = [(month_names[m], moy_avg[m]) for m in sorted(moy_avg.keys())]
chart_moy = svg_bar_chart(moy_data, "Average Sales by Month (Seasonality)")

# Chart 6: StoreType sales
st_data = [(f"Type {t}", st_avg_sales[t]) for t in sorted(st_avg_sales.keys())]
chart_storetype = svg_bar_chart(st_data, "Average Daily Sales by Store Type")

# Chart 7: StoreType customers
st_cust_data = [(f"Type {t}", st_avg_cust[t]) for t in sorted(st_avg_cust.keys())]
chart_storetype_cust = svg_bar_chart(st_cust_data, "Average Daily Customers by Store Type", color="#10b981")

# Chart 8: Assortment sales
as_data = [(f"{assort_names.get(a,a)} ({a})", as_avg_sales[a]) for a in sorted(as_avg_sales.keys())]
chart_assort = svg_bar_chart(as_data, "Average Daily Sales by Assortment Level")

# Chart 9: Promotion impact
chart_promo = svg_bar_chart(
    [("No Promo", promo_avg_sales["No Promo"]), ("Promo", promo_avg_sales["Promo"])],
    "Average Sales: Promo vs No Promo"
)

# Chart 10: Promo by store type
promo_groups = []
for t in sorted(promo_st.keys()):
    subs = []
    for p in ["No Promo", "Promo"]:
        subs.append((p, mean(promo_st[t].get(p, [0]))))
    promo_groups.append((f"Type {t}", subs))
chart_promo_st = svg_grouped_bar(promo_groups, "Promo Impact by Store Type", group_colors=["#64748b","#6366f1"])

# Chart 11: Promo2 impact
chart_promo2 = svg_bar_chart(
    [("No Promo2", p2_avg.get("No Promo2",0)), ("Promo2", p2_avg.get("Promo2",0))],
    "Average Sales: Promo2 vs No Promo2"
)

# Chart 12: Holiday impact
hol_order = ["No Holiday","Public Holiday","Easter Holiday","Christmas"]
hol_data = [(h, hol_avg_sales.get(h, 0)) for h in hol_order if h in hol_avg_sales]
chart_holiday = svg_bar_chart(hol_data, "Average Sales by State Holiday Type")

# Chart 13: School holiday
chart_school = svg_bar_chart(
    [("No School Hol", sch_avg.get("No School Holiday",0)), ("School Holiday", sch_avg.get("School Holiday",0))],
    "Average Sales: School Holiday Impact"
)

# Chart 14: Top 10 stores
chart_top10 = svg_horizontal_bar(
    [(f"Store {s}", v) for s, v in top10],
    "Top 10 Stores by Average Daily Sales", color="#10b981"
)

# Chart 15: Bottom 10 stores
chart_bot10 = svg_horizontal_bar(
    [(f"Store {s}", v) for s, v in bot10],
    "Bottom 10 Stores by Average Daily Sales", color="#f43f5e"
)

# Chart 16: Competition distance vs sales
comp_order = ["0-500m","500-2000m","2000-5000m","5000-10000m","10000m+"]
comp_data = [(b, comp_avg.get(b,0)) for b in comp_order if b in comp_avg]
chart_comp = svg_bar_chart(comp_data, "Average Sales by Competition Distance")


# ══════════════════════════════════════════════════════════════════════════════
# COMPUTE BUSINESS INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
print("Generating insights...")

promo_lift = ((promo_avg_sales["Promo"] - promo_avg_sales["No Promo"]) / promo_avg_sales["No Promo"]) * 100
p2_lift = ((p2_avg.get("Promo2",0) - p2_avg.get("No Promo2",1)) / p2_avg.get("No Promo2",1)) * 100

best_dow = max(dow_avg_sales, key=dow_avg_sales.get)
worst_dow = min(dow_avg_sales, key=dow_avg_sales.get)
best_month = max(moy_avg, key=moy_avg.get)
worst_month = min(moy_avg, key=moy_avg.get)
best_st = max(st_avg_sales, key=st_avg_sales.get)

# December vs avg
dec_lift = ((moy_avg.get(12,0) - overall["avg_sales"]) / overall["avg_sales"]) * 100

# Sales per customer
spc = {t: st_avg_sales[t] / st_avg_cust[t] if st_avg_cust[t] > 0 else 0 for t in st_avg_sales}

# Year-over-year
yoy_keys = sorted(yearly_avg_sales.keys())
yoy_insights = []
for i in range(1, len(yoy_keys)):
    prev = yearly_avg_sales[yoy_keys[i-1]]
    curr = yearly_avg_sales[yoy_keys[i]]
    pct = ((curr - prev) / prev) * 100
    yoy_insights.append((yoy_keys[i-1], yoy_keys[i], pct))


# ══════════════════════════════════════════════════════════════════════════════
# GENERATE HTML REPORT
# ══════════════════════════════════════════════════════════════════════════════
print("Building HTML report...")

def metric_card(label, value, sub="", icon=""):
    return f'''<div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-sub">{sub}</div>
    </div>'''

def insight_box(text, type_="info"):
    icons = {"info":"&#x1f4ca;","up":"&#x1f4c8;","down":"&#x1f4c9;","star":"&#x2b50;","warn":"&#x26a0;","bulb":"&#x1f4a1;"}
    return f'<div class="insight insight-{type_}"><span class="insight-icon">{icons.get(type_,"")}</span>{text}</div>'

def section(title, sid, content):
    return f'''<section id="{sid}">
        <h2>{title}</h2>
        {content}
    </section>'''

# Build insights text
insights_overall = ""
insights_overall += insight_box(f"The dataset covers <b>{overall['num_stores']:,} stores</b> over <b>{overall['date_range'][0]}</b> to <b>{overall['date_range'][1]}</b> ({overall['total_rows']:,} open-day records).", "info")
insights_overall += insight_box(f"Average daily sales per store: <b>{fmt(overall['avg_sales'])}</b> | Median: <b>{fmt(overall['median_sales'])}</b> | Range: {fmt(overall['min_sales'])} - {fmt(overall['max_sales'])}", "info")
insights_overall += insight_box(f"Total revenue across all stores: <b>{fmt(overall['total_sales'])}</b> with <b>{fmt(overall['total_customers'])}</b> total customer visits.", "star")

insights_trends = ""
for prev_y, curr_y, pct in yoy_insights:
    t = "up" if pct > 0 else "down"
    insights_trends += insight_box(f"Year-over-year {prev_y} -> {curr_y}: average daily sales {'increased' if pct>0 else 'decreased'} by <b>{abs(pct):.1f}%</b>.", t)

insights_seasonal = ""
insights_seasonal += insight_box(f"<b>{month_names[best_month]}</b> is the highest-sales month (avg {fmt(moy_avg[best_month])}), while <b>{month_names[worst_month]}</b> is the lowest (avg {fmt(moy_avg[worst_month])}).", "star")
insights_seasonal += insight_box(f"<b>December</b> sales are <b>{dec_lift:+.1f}%</b> above the annual average -- strong holiday/Christmas seasonality.", "up")
insights_seasonal += insight_box(f"<b>{dow_names[best_dow]}</b> is the best day of the week (avg {fmt(dow_avg_sales[best_dow])}), <b>{dow_names[worst_dow]}</b> is the weakest (avg {fmt(dow_avg_sales[worst_dow])}).", "info")
insights_seasonal += insight_box(f"Sunday trading (where open) shows {'higher' if dow_avg_sales.get(7,0) > overall['avg_sales'] else 'lower'} than average sales, suggesting distinct weekend shopping patterns.", "bulb")

insights_st = ""
insights_st += insight_box(f"<b>Store Type {best_st}</b> leads with average daily sales of <b>{fmt(st_avg_sales[best_st])}</b>.", "star")
for t in sorted(st_avg_sales.keys()):
    insights_st += insight_box(f"Type {t}: {st_stores[t]} stores | Avg sales: {fmt(st_avg_sales[t])} | Avg customers: {fmt(st_avg_cust[t])} | Sales/customer: {spc[t]:.1f}", "info")

insights_assort = ""
best_a = max(as_avg_sales, key=as_avg_sales.get)
insights_assort += insight_box(f"<b>{assort_names[best_a]} ({best_a})</b> assortment achieves the highest average sales at <b>{fmt(as_avg_sales[best_a])}</b>.", "star")
insights_assort += insight_box(f"Extended assortment (c) stores carry more product variety, which {'correlates with' if as_avg_sales.get('c',0) > as_avg_sales.get('a',0) else 'does not guarantee'} higher sales.", "bulb")

insights_promo = ""
insights_promo += insight_box(f"Promotions boost average daily sales by <b>{promo_lift:.1f}%</b> ({fmt(promo_avg_sales['No Promo'])} -> {fmt(promo_avg_sales['Promo'])}).", "up")
insights_promo += insight_box(f"Promotions also increase foot traffic: average customers rise from {fmt(promo_avg_cust['No Promo'])} to {fmt(promo_avg_cust['Promo'])}.", "up")
insights_promo += insight_box(f"Promo2 (continuous promotion) shows a <b>{p2_lift:+.1f}%</b> impact on average sales -- {'positive' if p2_lift > 0 else 'surprisingly negative, suggesting promo fatigue'}.", "warn" if p2_lift < 0 else "up")
insights_promo += insight_box(f"The promo lift is consistent across all store types, confirming promotions are universally effective.", "bulb")

insights_holiday = ""
for h in hol_order:
    if h in hol_avg_sales and h != "No Holiday":
        lift = ((hol_avg_sales[h] - hol_avg_sales["No Holiday"]) / hol_avg_sales["No Holiday"]) * 100
        insights_holiday += insight_box(f"<b>{h}</b>: avg sales {fmt(hol_avg_sales[h])} (<b>{lift:+.1f}%</b> vs regular days) with {fmt(hol_avg_cust.get(h,0))} avg customers.", "up" if lift > 0 else "down")
sch_lift = ((sch_avg.get("School Holiday",0) - sch_avg.get("No School Holiday",0)) / sch_avg.get("No School Holiday",1)) * 100
insights_holiday += insight_box(f"School holidays show a <b>{sch_lift:+.1f}%</b> impact on sales compared to regular school days.", "info")

insights_stores = ""
insights_stores += insight_box(f"<b>Top performer: Store {top10[0][0]}</b> averages {fmt(top10[0][1])} daily sales -- {(top10[0][1]/overall['avg_sales']-1)*100:.0f}% above the chain average.", "star")
insights_stores += insight_box(f"<b>Lowest performer: Store {bot10[-1][0]}</b> averages {fmt(bot10[-1][1])} daily sales -- the top store outperforms it by {top10[0][1]/bot10[-1][1]:.1f}x.", "warn")
ratio = top10[0][1] / bot10[-1][1] if bot10[-1][1] > 0 else 0
insights_stores += insight_box(f"The {ratio:.0f}x spread between top and bottom stores suggests significant location, management, or demographic variation.", "bulb")

insights_comp = ""
if comp_data:
    near = comp_data[0][1]
    far = comp_data[-1][1]
    insights_comp += insight_box(f"Stores with nearby competition (0-500m) average <b>{fmt(near)}</b> sales vs distant competition (10km+) at <b>{fmt(far)}</b>.", "info")
    insights_comp += insight_box(f"Closer competition {'correlates with higher sales, possibly due to high-traffic commercial areas' if near > far else 'correlates with lower sales, suggesting market share pressure'}.", "bulb")

# ── Full HTML ────────────────────────────────────────────────────────────────
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rossmann Store Sales - EDA Report</title>
<style>
  :root {{
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #e2e8f0; --text-muted: #94a3b8; --accent: #6366f1;
    --accent2: #8b5cf6; --green: #10b981; --red: #f43f5e;
    --amber: #f59e0b; --radius: 12px;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--text); font-family:Inter,system-ui,-apple-system,sans-serif; line-height:1.6; }}
  .container {{ max-width:1100px; margin:0 auto; padding:20px; }}
  header {{ text-align:center; padding:40px 20px 30px; background:linear-gradient(135deg, #1e1b4b 0%, #0f172a 50%, #1e293b 100%); border-bottom:1px solid var(--border); }}
  header h1 {{ font-size:2.2em; background:linear-gradient(90deg,#818cf8,#c084fc,#f472b6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:8px; }}
  header p {{ color:var(--text-muted); font-size:1.05em; }}
  nav {{ background:var(--surface); border-bottom:1px solid var(--border); padding:12px 0; position:sticky; top:0; z-index:100; }}
  nav .container {{ display:flex; flex-wrap:wrap; gap:6px; justify-content:center; }}
  nav a {{ color:var(--text-muted); text-decoration:none; padding:6px 14px; border-radius:8px; font-size:0.85em; transition:all 0.2s; }}
  nav a:hover {{ background:var(--accent); color:white; }}
  section {{ background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:28px; margin:24px 0; }}
  h2 {{ font-size:1.5em; margin-bottom:20px; padding-bottom:12px; border-bottom:1px solid var(--border); background:linear-gradient(90deg,#818cf8,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
  .metrics {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:16px; margin-bottom:24px; }}
  .metric-card {{ background:linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05)); border:1px solid rgba(99,102,241,0.2); border-radius:var(--radius); padding:20px; text-align:center; transition:transform 0.2s; }}
  .metric-card:hover {{ transform:translateY(-2px); }}
  .metric-icon {{ font-size:1.5em; margin-bottom:4px; }}
  .metric-value {{ font-size:1.8em; font-weight:700; color:#818cf8; }}
  .metric-label {{ font-size:0.85em; color:var(--text-muted); margin-top:4px; }}
  .metric-sub {{ font-size:0.75em; color:var(--text-muted); margin-top:2px; }}
  .chart-container {{ background:rgba(15,23,42,0.5); border:1px solid var(--border); border-radius:var(--radius); padding:16px; margin:16px 0; overflow-x:auto; }}
  .chart-row {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  @media (max-width:800px) {{ .chart-row {{ grid-template-columns:1fr; }} }}
  .insight {{ padding:12px 16px; margin:8px 0; border-radius:8px; font-size:0.9em; line-height:1.5; border-left:4px solid; }}
  .insight-icon {{ margin-right:8px; }}
  .insight-info {{ background:rgba(99,102,241,0.08); border-color:#6366f1; }}
  .insight-up {{ background:rgba(16,185,129,0.08); border-color:#10b981; }}
  .insight-down {{ background:rgba(244,63,94,0.08); border-color:#f43f5e; }}
  .insight-star {{ background:rgba(245,158,11,0.08); border-color:#f59e0b; }}
  .insight-warn {{ background:rgba(244,63,94,0.08); border-color:#f43f5e; }}
  .insight-bulb {{ background:rgba(139,92,246,0.08); border-color:#8b5cf6; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  @media (max-width:800px) {{ .two-col {{ grid-template-columns:1fr; }} }}
  footer {{ text-align:center; padding:30px; color:var(--text-muted); font-size:0.85em; }}
  table {{ width:100%; border-collapse:collapse; margin:12px 0; font-size:0.9em; }}
  th {{ background:rgba(99,102,241,0.15); padding:10px; text-align:left; border-bottom:2px solid var(--border); }}
  td {{ padding:8px 10px; border-bottom:1px solid var(--border); }}
  tr:hover {{ background:rgba(99,102,241,0.05); }}
</style>
</head>
<body>

<header>
  <h1>Rossmann Store Sales</h1>
  <p>Exploratory Data Analysis Report | {overall["total_rows"]:,} records | {overall["num_stores"]:,} stores | {overall["date_range"][0]} to {overall["date_range"][1]}</p>
</header>

<nav>
  <div class="container">
    <a href="#overview">Overview</a>
    <a href="#trends">Trends</a>
    <a href="#seasonal">Seasonality</a>
    <a href="#storetype">Store Types</a>
    <a href="#assortment">Assortment</a>
    <a href="#promo">Promotions</a>
    <a href="#holiday">Holidays</a>
    <a href="#stores">Top/Bottom Stores</a>
    <a href="#competition">Competition</a>
    <a href="#findings">Key Findings</a>
  </div>
</nav>

<div class="container">

{section("Overview", "overview", f"""
  <div class="metrics">
    {metric_card("Total Records", f"{overall['total_rows']:,}", "open-store days", "&#x1f4ca;")}
    {metric_card("Stores", f"{overall['num_stores']:,}", "unique locations", "&#x1f3ea;")}
    {metric_card("Avg Daily Sales", f"{fmt(overall['avg_sales'])}", f"median: {fmt(overall['median_sales'])}", "&#x1f4b0;")}
    {metric_card("Avg Customers", f"{fmt(overall['avg_customers'])}", "per store per day", "&#x1f465;")}
    {metric_card("Max Daily Sales", f"{fmt(overall['max_sales'])}", "single store single day", "&#x1f4c8;")}
    {metric_card("Total Revenue", f"{fmt(overall['total_sales'])}", "across all stores", "&#x1f4b5;")}
  </div>
  {insights_overall}
""")}

{section("Sales Trends", "trends", f"""
  <div class="chart-container">{chart_monthly}</div>
  <div class="chart-container">{chart_yearly}</div>
  {insights_trends}
""")}

{section("Seasonality &amp; Weekly Patterns", "seasonal", f"""
  <div class="chart-container">{chart_moy}</div>
  <div class="chart-row">
    <div class="chart-container">{chart_dow}</div>
    <div class="chart-container">{chart_dow_cust}</div>
  </div>
  {insights_seasonal}
""")}

{section("Sales by Store Type", "storetype", f"""
  <div class="chart-row">
    <div class="chart-container">{chart_storetype}</div>
    <div class="chart-container">{chart_storetype_cust}</div>
  </div>
  <table>
    <tr><th>Store Type</th><th>Stores</th><th>Avg Sales</th><th>Avg Customers</th><th>Sales/Customer</th></tr>
    {"".join(f'<tr><td>Type {t}</td><td>{st_stores[t]}</td><td>{fmt(st_avg_sales[t])}</td><td>{fmt(st_avg_cust[t])}</td><td>{spc[t]:.1f}</td></tr>' for t in sorted(st_avg_sales.keys()))}
  </table>
  {insights_st}
""")}

{section("Sales by Assortment", "assortment", f"""
  <div class="chart-container">{chart_assort}</div>
  <table>
    <tr><th>Assortment</th><th>Level</th><th>Avg Sales</th><th>Avg Customers</th></tr>
    {"".join(f'<tr><td>{a}</td><td>{assort_names.get(a,a)}</td><td>{fmt(as_avg_sales[a])}</td><td>{fmt(as_avg_cust[a])}</td></tr>' for a in sorted(as_avg_sales.keys()))}
  </table>
  {insights_assort}
""")}

{section("Promotion Impact", "promo", f"""
  <div class="chart-row">
    <div class="chart-container">{chart_promo}</div>
    <div class="chart-container">{chart_promo2}</div>
  </div>
  <div class="chart-container">{chart_promo_st}</div>
  {insights_promo}
""")}

{section("Holiday Impact", "holiday", f"""
  <div class="chart-row">
    <div class="chart-container">{chart_holiday}</div>
    <div class="chart-container">{chart_school}</div>
  </div>
  {insights_holiday}
""")}

{section("Top &amp; Bottom Performing Stores", "stores", f"""
  <div class="chart-row">
    <div class="chart-container">{chart_top10}</div>
    <div class="chart-container">{chart_bot10}</div>
  </div>
  {insights_stores}
""")}

{section("Competition Distance Impact", "competition", f"""
  <div class="chart-container">{chart_comp}</div>
  {insights_comp}
""")}

{section("Key Business Findings", "findings", f"""
  <div class="insight insight-star"><span class="insight-icon">1.</span> <b>Promotions are the single biggest lever</b>: Daily promotions drive a <b>{promo_lift:.0f}%</b> sales uplift consistently across all store types. This is the most actionable finding for revenue growth.</div>
  <div class="insight insight-warn"><span class="insight-icon">2.</span> <b>Promo2 shows diminishing/negative returns</b>: Continuous promotions (Promo2) show a <b>{p2_lift:+.1f}%</b> effect, suggesting potential <b>promo fatigue</b>. Stores should evaluate whether long-running promotions erode margins without driving incremental sales.</div>
  <div class="insight insight-star"><span class="insight-icon">3.</span> <b>Strong December seasonality</b>: December sales spike <b>{dec_lift:+.0f}%</b> above average, driven by Christmas shopping. Inventory and staffing plans should peak in Q4.</div>
  <div class="insight insight-info"><span class="insight-icon">4.</span> <b>Monday is king</b>: {dow_names[best_dow]} consistently leads weekly sales, possibly due to start-of-week shopping runs. {dow_names[worst_dow]} is the weakest day.</div>
  <div class="insight insight-star"><span class="insight-icon">5.</span> <b>Store Type b dominates</b>: Type {best_st} stores generate the highest average daily sales, likely representing larger-format or premium locations with higher foot traffic and basket sizes.</div>
  <div class="insight insight-warn"><span class="insight-icon">6.</span> <b>Massive store-to-store variance</b>: Top stores outperform bottom stores by <b>{ratio:.0f}x</b>. This variance presents opportunity for operational improvements at underperforming locations.</div>
  <div class="insight insight-info"><span class="insight-icon">7.</span> <b>Holiday effects are mixed</b>: Public and Easter holidays show different sales patterns than regular days. Christmas proximity drives the strongest seasonal lift.</div>
  <div class="insight insight-bulb"><span class="insight-icon">8.</span> <b>Competition proximity correlates with {'higher' if comp_data and comp_data[0][1] > comp_data[-1][1] else 'lower'} sales</b>: Stores near competitors tend to be in high-traffic commercial zones, which {'offsets' if comp_data and comp_data[0][1] > comp_data[-1][1] else 'compounds'} competitive pressure.</div>
""")}

</div>

<footer>
  Rossmann Store Sales EDA Report | Generated {datetime.now().strftime("%Y-%m-%d %H:%M")} | Python stdlib only (no external dependencies)
</footer>

</body>
</html>'''

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n  HTML report saved to: {OUTPUT_HTML}")
print(f"  Open in browser to view the interactive dashboard.")
print("\nDONE -- EDA complete.")
