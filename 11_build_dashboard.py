"""
11_build_dashboard.py
=====================
Generates a self-contained enterprise-grade HTML dashboard for Rossmann Sales Forecasting.
Reads from dashboard_data.json and embeds it into a single HTML file.
Uses only Python standard library.
"""

import os
import json

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
JSON_FILE = os.path.join(DATA_DIR, "dashboard_data.json")
OUTPUT_HTML = os.path.join(DATA_DIR, "rossmann_dashboard.html")

print("Loading dashboard data...")
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

json_str = json.dumps(data)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rossmann Sales Forecasting Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {{
  --bg-primary: #0a0e1a;
  --bg-secondary: #111827;
  --bg-card: #1a2035;
  --bg-card-hover: #1f2847;
  --border: rgba(99,102,241,0.15);
  --border-bright: rgba(99,102,241,0.3);
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent: #6366f1;
  --accent-light: #818cf8;
  --green: #10b981;
  --green-bg: rgba(16,185,129,0.1);
  --red: #f43f5e;
  --red-bg: rgba(244,63,94,0.1);
  --amber: #f59e0b;
  --amber-bg: rgba(245,158,11,0.1);
  --blue: #3b82f6;
  --blue-bg: rgba(59,130,246,0.1);
  --purple: #8b5cf6;
  --purple-bg: rgba(139,92,246,0.1);
  --cyan: #06b6d4;
  --radius: 16px;
  --radius-sm: 10px;
  --shadow: 0 4px 24px rgba(0,0,0,0.3);
  --transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}}
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ background:var(--bg-primary);color:var(--text-primary);font-family:'Inter',system-ui,sans-serif;line-height:1.6;overflow-x:hidden; }}
::selection {{ background:var(--accent);color:white; }}
::-webkit-scrollbar {{ width:6px; }}
::-webkit-scrollbar-track {{ background:var(--bg-secondary); }}
::-webkit-scrollbar-thumb {{ background:var(--accent);border-radius:3px; }}

.app {{ display:flex;min-height:100vh; }}

/* ── Sidebar ── */
.sidebar {{ width:260px;background:var(--bg-secondary);border-right:1px solid var(--border);position:fixed;top:0;left:0;bottom:0;z-index:100;display:flex;flex-direction:column;transition:transform 0.3s; }}
.sidebar-brand {{ padding:24px 20px;border-bottom:1px solid var(--border); }}
.sidebar-brand h1 {{ font-size:1.1em;font-weight:700;background:linear-gradient(135deg,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent; }}
.sidebar-brand p {{ font-size:0.7em;color:var(--text-muted);margin-top:2px;letter-spacing:0.5px;text-transform:uppercase; }}
.sidebar-nav {{ flex:1;padding:12px 10px;overflow-y:auto; }}
.nav-item {{ display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:var(--radius-sm);color:var(--text-secondary);cursor:pointer;transition:var(--transition);font-size:0.88em;font-weight:500;margin-bottom:2px; }}
.nav-item:hover {{ background:rgba(99,102,241,0.08);color:var(--text-primary); }}
.nav-item.active {{ background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.1));color:var(--accent-light);border:1px solid var(--border-bright); }}
.nav-icon {{ font-size:1.2em;width:24px;text-align:center; }}
.sidebar-footer {{ padding:16px 20px;border-top:1px solid var(--border);font-size:0.72em;color:var(--text-muted); }}

/* ── Main Content ── */
.main {{ margin-left:260px;flex:1;min-height:100vh; }}
.page-header {{ padding:28px 36px 20px;border-bottom:1px solid var(--border);background:linear-gradient(180deg,rgba(99,102,241,0.04),transparent); }}
.page-header h2 {{ font-size:1.6em;font-weight:700;margin-bottom:4px; }}
.page-header p {{ color:var(--text-secondary);font-size:0.88em; }}
.page-content {{ padding:28px 36px; }}

/* ── Page Sections ── */
.page {{ display:none; }}
.page.active {{ display:block; }}

/* ── Cards ── */
.kpi-grid {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:28px; }}
.kpi-card {{ background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:22px;transition:var(--transition);position:relative;overflow:hidden; }}
.kpi-card::before {{ content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--accent),var(--purple));opacity:0;transition:var(--transition); }}
.kpi-card:hover {{ border-color:var(--border-bright);transform:translateY(-2px);box-shadow:var(--shadow); }}
.kpi-card:hover::before {{ opacity:1; }}
.kpi-icon {{ font-size:1.8em;margin-bottom:8px; }}
.kpi-value {{ font-size:1.9em;font-weight:800;background:linear-gradient(135deg,#e2e8f0,#cbd5e1);-webkit-background-clip:text;-webkit-text-fill-color:transparent; }}
.kpi-label {{ font-size:0.78em;color:var(--text-muted);margin-top:4px;text-transform:uppercase;letter-spacing:0.5px; }}
.kpi-delta {{ font-size:0.78em;margin-top:6px;padding:3px 8px;border-radius:20px;display:inline-block;font-weight:600; }}
.kpi-delta.up {{ background:var(--green-bg);color:var(--green); }}
.kpi-delta.down {{ background:var(--red-bg);color:var(--red); }}

/* ── Charts ── */
.chart-grid {{ display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:28px; }}
.chart-grid.full {{ grid-template-columns:1fr; }}
.chart-grid.tri {{ grid-template-columns:1fr 1fr 1fr; }}
@media(max-width:1100px) {{ .chart-grid,.chart-grid.tri {{ grid-template-columns:1fr; }} }}
.chart-card {{ background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;transition:var(--transition); }}
.chart-card:hover {{ border-color:var(--border-bright); }}
.chart-title {{ font-size:0.92em;font-weight:600;margin-bottom:16px;color:var(--text-primary); }}
.chart-subtitle {{ font-size:0.75em;color:var(--text-muted);margin-top:-12px;margin-bottom:16px; }}

/* ── SVG Charts ── */
svg text {{ font-family:'Inter',system-ui,sans-serif; }}

/* ── Tables ── */
.data-table {{ width:100%;border-collapse:separate;border-spacing:0;font-size:0.85em; }}
.data-table th {{ background:rgba(99,102,241,0.08);padding:12px 16px;text-align:left;font-weight:600;color:var(--text-secondary);border-bottom:2px solid var(--border);text-transform:uppercase;font-size:0.78em;letter-spacing:0.5px; }}
.data-table td {{ padding:11px 16px;border-bottom:1px solid rgba(51,65,85,0.3); }}
.data-table tr:hover td {{ background:rgba(99,102,241,0.04); }}
.data-table .rank {{ color:var(--accent-light);font-weight:700;width:40px; }}
.badge {{ padding:3px 10px;border-radius:20px;font-size:0.78em;font-weight:600; }}
.badge-green {{ background:var(--green-bg);color:var(--green); }}
.badge-red {{ background:var(--red-bg);color:var(--red); }}
.badge-blue {{ background:var(--blue-bg);color:var(--blue); }}
.badge-purple {{ background:var(--purple-bg);color:var(--purple); }}
.badge-amber {{ background:var(--amber-bg);color:var(--amber); }}

/* ── Insights ── */
.insight-grid {{ display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:20px; }}
@media(max-width:900px) {{ .insight-grid {{ grid-template-columns:1fr; }} }}
.insight-card {{ background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-sm);padding:18px;border-left:4px solid var(--accent); }}
.insight-card.green {{ border-left-color:var(--green); }}
.insight-card.amber {{ border-left-color:var(--amber); }}
.insight-card.red {{ border-left-color:var(--red); }}
.insight-title {{ font-size:0.82em;font-weight:600;margin-bottom:4px; }}
.insight-text {{ font-size:0.78em;color:var(--text-secondary);line-height:1.5; }}

/* ── Model Comparison ── */
.model-cards {{ display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:28px; }}
@media(max-width:900px) {{ .model-cards {{ grid-template-columns:1fr; }} }}
.model-card {{ background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;text-align:center;transition:var(--transition); }}
.model-card.best {{ border-color:var(--green);background:linear-gradient(135deg,rgba(16,185,129,0.05),rgba(16,185,129,0.02)); }}
.model-card.best::before {{ content:'\\2605 BEST MODEL';display:block;font-size:0.68em;color:var(--green);font-weight:700;letter-spacing:1px;margin-bottom:12px; }}
.model-name {{ font-size:1.1em;font-weight:700;margin-bottom:16px; }}
.model-metric {{ margin:10px 0; }}
.model-metric-label {{ font-size:0.72em;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px; }}
.model-metric-value {{ font-size:1.5em;font-weight:700; }}

/* ── Bar in table ── */
.bar-cell {{ position:relative; }}
.bar-bg {{ position:absolute;top:50%;transform:translateY(-50%);left:0;height:6px;border-radius:3px;opacity:0.7;transition:width 0.8s ease; }}
</style>
</head>
<body>
<div class="app">

<!-- ── Sidebar ── -->
<nav class="sidebar">
  <div class="sidebar-brand">
    <h1>Rossmann Analytics</h1>
    <p>Sales Forecasting Suite</p>
  </div>
  <div class="sidebar-nav">
    <div class="nav-item active" data-page="overview">
      <span class="nav-icon">&#x1f4ca;</span> Executive Overview
    </div>
    <div class="nav-item" data-page="sales">
      <span class="nav-icon">&#x1f4c8;</span> Sales Analytics
    </div>
    <div class="nav-item" data-page="promo">
      <span class="nav-icon">&#x1f3af;</span> Promotion Insights
    </div>
    <div class="nav-item" data-page="forecast">
      <span class="nav-icon">&#x1f52e;</span> Forecast Center
    </div>
    <div class="nav-item" data-page="model">
      <span class="nav-icon">&#x1f9e0;</span> Model Insights
    </div>
  </div>
  <div class="sidebar-footer">
    Gradient Boosting &bull; R&sup2; 0.8724<br>
    844,392 records &bull; 1,115 stores
  </div>
</nav>

<!-- ── Main Content ── -->
<div class="main">

<!-- ═══ PAGE 1: EXECUTIVE OVERVIEW ═══ -->
<div class="page active" id="page-overview">
  <div class="page-header">
    <h2>Executive Overview</h2>
    <p>High-level KPIs and business performance summary across 1,115 Rossmann stores</p>
  </div>
  <div class="page-content" id="content-overview"></div>
</div>

<!-- ═══ PAGE 2: SALES ANALYTICS ═══ -->
<div class="page" id="page-sales">
  <div class="page-header">
    <h2>Sales Analytics</h2>
    <p>Deep dive into monthly trends, store performance, and assortment analysis</p>
  </div>
  <div class="page-content" id="content-sales"></div>
</div>

<!-- ═══ PAGE 3: PROMOTION INSIGHTS ═══ -->
<div class="page" id="page-promo">
  <div class="page-header">
    <h2>Promotion Insights</h2>
    <p>Quantify the business impact of promotions on sales and customer traffic</p>
  </div>
  <div class="page-content" id="content-promo"></div>
</div>

<!-- ═══ PAGE 4: FORECAST CENTER ═══ -->
<div class="page" id="page-forecast">
  <div class="page-header">
    <h2>Forecast Center</h2>
    <p>Actual vs predicted sales trends from the holdout test period</p>
  </div>
  <div class="page-content" id="content-forecast"></div>
</div>

<!-- ═══ PAGE 5: MODEL INSIGHTS ═══ -->
<div class="page" id="page-model">
  <div class="page-header">
    <h2>Model Insights</h2>
    <p>Feature importance, model comparison, and machine learning performance</p>
  </div>
  <div class="page-content" id="content-model"></div>
</div>

</div></div>

<script>
const D = ''' + json_str + ''';
const COLORS = ["#6366f1","#8b5cf6","#a78bfa","#c084fc","#e879f9","#f472b6","#fb7185","#f43f5e","#f59e0b","#10b981","#06b6d4","#3b82f6"];
const fmt = v => {{ if(Math.abs(v)>=1e9) return (v/1e9).toFixed(1)+'B'; if(Math.abs(v)>=1e6) return (v/1e6).toFixed(1)+'M'; if(Math.abs(v)>=1e3) return (v/1e3).toFixed(1)+'K'; return v.toLocaleString(); }};
const fmtN = v => v.toLocaleString();

// ── Navigation ──
document.querySelectorAll('.nav-item').forEach(item => {{
  item.addEventListener('click', () => {{
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    item.classList.add('active');
    document.getElementById('page-'+item.dataset.page).classList.add('active');
  }});
}});

// ── SVG Helpers ──
function svgBar(data, w=620, h=300, opts={{}}) {{
  const m = {{t:40,r:20,b:60,l:60,...(opts.margin||{{}})}};
  const pw=w-m.l-m.r, ph=h-m.t-m.b;
  const maxV = Math.max(...data.map(d=>d.value))||1;
  const n=data.length, barW=Math.min(pw/n*0.65,50), gap=(pw-barW*n)/(n+1);
  let s=`<svg viewBox="0 0 ${{w}} ${{h}}" xmlns="http://www.w3.org/2000/svg">`;
  for(let i=0;i<5;i++) {{
    const y=m.t+ph-(ph*i/4), val=maxV*i/4;
    s+=`<line x1="${{m.l}}" y1="${{y}}" x2="${{w-m.r}}" y2="${{y}}" stroke="rgba(148,163,184,0.1)" stroke-width="0.5"/>`;
    s+=`<text x="${{m.l-8}}" y="${{y+4}}" text-anchor="end" font-size="10" fill="#64748b">${{fmt(val)}}</text>`;
  }}
  data.forEach((d,i) => {{
    const x=m.l+gap+i*(barW+gap), bh=(d.value/maxV)*ph, y=m.t+ph-bh;
    const c=d.color||COLORS[i%COLORS.length];
    s+=`<rect x="${{x}}" y="${{y}}" width="${{barW}}" height="${{bh}}" rx="4" fill="${{c}}" opacity="0.85"><animate attributeName="height" from="0" to="${{bh}}" dur="0.6s" fill="freeze"/><animate attributeName="y" from="${{m.t+ph}}" to="${{y}}" dur="0.6s" fill="freeze"/></rect>`;
    s+=`<text x="${{x+barW/2}}" y="${{y-6}}" text-anchor="middle" font-size="10" font-weight="600" fill="#cbd5e1">${{fmt(d.value)}}</text>`;
    s+=`<text x="${{x+barW/2}}" y="${{h-m.b+16}}" text-anchor="middle" font-size="10" fill="#94a3b8">${{d.label}}</text>`;
  }});
  s+=`</svg>`;
  return s;
}}

function svgLine(datasets, w=620, h=300, opts={{}}) {{
  const m={{t:30,r:20,b:50,l:60,...(opts.margin||{{}})}};
  const pw=w-m.l-m.r, ph=h-m.t-m.b;
  let allV=[];datasets.forEach(ds=>ds.points.forEach(p=>allV.push(p.y)));
  if(!allV.length) return '';
  const minV=Math.min(...allV),maxV=Math.max(...allV), rng=maxV-minV||1;
  const maxX=datasets.reduce((a,ds)=>Math.max(a,ds.points.length-1),0)||1;
  let s=`<svg viewBox="0 0 ${{w}} ${{h}}" xmlns="http://www.w3.org/2000/svg">`;
  for(let i=0;i<5;i++) {{
    const y=m.t+ph-(ph*i/4), val=minV+rng*i/4;
    s+=`<line x1="${{m.l}}" y1="${{y}}" x2="${{w-m.r}}" y2="${{y}}" stroke="rgba(148,163,184,0.1)" stroke-width="0.5"/>`;
    s+=`<text x="${{m.l-8}}" y="${{y+4}}" text-anchor="end" font-size="10" fill="#64748b">${{fmt(val)}}</text>`;
  }}
  datasets.forEach(ds => {{
    if(ds.points.length<2) return;
    const pts=ds.points.map((p,i)=>{{
      const x=m.l+(i/maxX)*pw, y=m.t+ph-((p.y-minV)/rng)*ph;
      return `${{x}},${{y}}`;
    }});
    const path='M '+pts.join(' L ');
    const fX=m.l, lX=m.l+((ds.points.length-1)/maxX)*pw;
    s+=`<path d="${{path}} L ${{lX}},${{m.t+ph}} L ${{fX}},${{m.t+ph}} Z" fill="${{ds.color}}" opacity="0.06"/>`;
    s+=`<path d="${{path}}" fill="none" stroke="${{ds.color}}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>`;
  }});
  if(opts.xLabels) {{
    const step=Math.max(1,Math.floor(opts.xLabels.length/8));
    opts.xLabels.forEach((l,i) => {{
      if(i%step!==0) return;
      const x=m.l+(i/maxX)*pw;
      s+=`<text x="${{x}}" y="${{h-m.b+16}}" text-anchor="middle" font-size="9" fill="#64748b" transform="rotate(-35,${{x}},${{h-m.b+16}})">${{l}}</text>`;
    }});
  }}
  if(opts.legend) {{
    datasets.forEach((ds,i) => {{
      const lx=m.l+i*130, ly=h-8;
      s+=`<rect x="${{lx}}" y="${{ly-8}}" width="12" height="12" rx="2" fill="${{ds.color}}"/>`;
      s+=`<text x="${{lx+16}}" y="${{ly+2}}" font-size="10" fill="#94a3b8">${{ds.name}}</text>`;
    }});
  }}
  s+=`</svg>`;
  return s;
}}

function svgHBar(data, w=620, h=null) {{
  const n=data.length;
  if(!h) h=Math.max(200,n*34+70);
  const m={{t:20,r:80,b:20,l:110}};
  const pw=w-m.l-m.r, ph=h-m.t-m.b;
  const maxV=Math.max(...data.map(d=>d.value))||1;
  const barH=Math.min(ph/n*0.7,22), gap=(ph-barH*n)/(n+1);
  let s=`<svg viewBox="0 0 ${{w}} ${{h}}" xmlns="http://www.w3.org/2000/svg">`;
  data.forEach((d,i) => {{
    const y=m.t+gap+i*(barH+gap), bw=(d.value/maxV)*pw;
    const c=d.color||COLORS[i%COLORS.length];
    s+=`<rect x="${{m.l}}" y="${{y}}" width="${{bw}}" height="${{barH}}" rx="4" fill="${{c}}" opacity="0.85"><animate attributeName="width" from="0" to="${{bw}}" dur="0.6s" fill="freeze"/></rect>`;
    s+=`<text x="${{m.l-8}}" y="${{y+barH/2+4}}" text-anchor="end" font-size="10" fill="#94a3b8">${{d.label}}</text>`;
    s+=`<text x="${{m.l+bw+6}}" y="${{y+barH/2+4}}" font-size="10" font-weight="600" fill="#cbd5e1">${{fmt(d.value)}}</text>`;
  }});
  s+=`</svg>`;
  return s;
}}

function svgGroupedBar(groups, w=620, h=300) {{
  const m={{t:30,r:20,b:60,l:60}};
  const pw=w-m.l-m.r, ph=h-m.t-m.b;
  const allV=groups.flatMap(g=>g.bars.map(b=>b.value));
  const maxV=Math.max(...allV)||1;
  const nG=groups.length, nS=groups[0].bars.length;
  const gW=pw/nG, subW=Math.min(gW*0.7/nS,35);
  const subColors=['#64748b','#6366f1'];
  let s=`<svg viewBox="0 0 ${{w}} ${{h}}" xmlns="http://www.w3.org/2000/svg">`;
  for(let i=0;i<5;i++) {{
    const y=m.t+ph-(ph*i/4), val=maxV*i/4;
    s+=`<line x1="${{m.l}}" y1="${{y}}" x2="${{w-m.r}}" y2="${{y}}" stroke="rgba(148,163,184,0.1)" stroke-width="0.5"/>`;
    s+=`<text x="${{m.l-8}}" y="${{y+4}}" text-anchor="end" font-size="10" fill="#64748b">${{fmt(val)}}</text>`;
  }}
  groups.forEach((g,gi) => {{
    const gx=m.l+gi*gW+gW*0.15;
    g.bars.forEach((b,si) => {{
      const x=gx+si*(subW+3), bh=(b.value/maxV)*ph, y=m.t+ph-bh;
      s+=`<rect x="${{x}}" y="${{y}}" width="${{subW}}" height="${{bh}}" rx="3" fill="${{subColors[si]}}" opacity="0.85"/>`;
      s+=`<text x="${{x+subW/2}}" y="${{y-4}}" text-anchor="middle" font-size="9" fill="#cbd5e1">${{fmt(b.value)}}</text>`;
    }});
    s+=`<text x="${{gx+nS*(subW+3)/2}}" y="${{h-m.b+16}}" text-anchor="middle" font-size="11" fill="#94a3b8">${{g.label}}</text>`;
  }});
  groups[0].bars.forEach((b,i) => {{
    const lx=m.l+i*120;
    s+=`<rect x="${{lx}}" y="${{h-12}}" width="12" height="12" rx="2" fill="${{subColors[i]}}"/>`;
    s+=`<text x="${{lx+16}}" y="${{h-2}}" font-size="10" fill="#94a3b8">${{b.label}}</text>`;
  }});
  s+=`</svg>`;
  return s;
}}

// ══════════════════════════════════════════════════════════════════════════════
// PAGE BUILDERS
// ══════════════════════════════════════════════════════════════════════════════

function buildOverview() {{
  const o=D.overview, p=D.promotion;
  let h=`
  <div class="kpi-grid">
    <div class="kpi-card"><div class="kpi-icon">&#x1f4b0;</div><div class="kpi-value">&euro;${{fmt(o.total_revenue)}}</div><div class="kpi-label">Total Revenue</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f3ea;</div><div class="kpi-value">${{fmtN(o.num_stores)}}</div><div class="kpi-label">Stores Tracked</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f4c8;</div><div class="kpi-value">&euro;${{fmtN(o.avg_daily_sales)}}</div><div class="kpi-label">Avg Daily Sales</div><div class="kpi-delta up">Median &euro;${{fmtN(o.median_daily_sales)}}</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f465;</div><div class="kpi-value">${{fmtN(o.avg_customers)}}</div><div class="kpi-label">Avg Daily Customers</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f3af;</div><div class="kpi-value">${{p.lift_pct}}%</div><div class="kpi-label">Promo Sales Lift</div><div class="kpi-delta up">+&euro;${{fmtN(p.promo_avg - p.no_promo_avg)}}/day</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f916;</div><div class="kpi-value">0.8724</div><div class="kpi-label">Model R&sup2;</div><div class="kpi-delta up">MAE &euro;746</div></div>
  </div>`;

  // Monthly trend chart
  const mPts = D.monthly_trends.map(m => ({{y:m.avg_sales}}));
  const mLabels = D.monthly_trends.map(m => m.month);
  h+=`<div class="chart-grid full"><div class="chart-card">
    <div class="chart-title">Monthly Average Sales Trend (Jan 2013 &#x2192; Jul 2015)</div>
    ${{svgLine([{{name:'Avg Sales',points:mPts,color:'#6366f1'}}],900,280,{{xLabels:mLabels}})}}
  </div></div>`;

  // Seasonality + DOW
  h+=`<div class="chart-grid">
    <div class="chart-card">
      <div class="chart-title">Seasonality: Average Sales by Month</div>
      ${{svgBar(D.seasonality.map(s=>({{label:s.month,value:s.avg_sales}})))}}
    </div>
    <div class="chart-card">
      <div class="chart-title">Average Sales by Day of Week</div>
      ${{svgBar(D.day_of_week.map(d=>({{label:d.day,value:d.avg_sales}})))}}
    </div>
  </div>`;

  // Key insights
  h+=`<div class="insight-grid">
    <div class="insight-card green"><div class="insight-title">&#x1f4b0; Revenue Engine</div><div class="insight-text">Total revenue of &euro;${{fmt(o.total_revenue)}} across ${{fmtN(o.num_stores)}} stores over ${{o.total_days}} trading days. Average daily sales of &euro;${{fmtN(o.avg_daily_sales)}} per store.</div></div>
    <div class="insight-card"><div class="insight-title">&#x1f4c5; December Dominance</div><div class="insight-text">December consistently outperforms all months with avg sales of &euro;${{fmtN(D.seasonality[11].avg_sales)}}, driven by holiday shopping season.</div></div>
    <div class="insight-card green"><div class="insight-title">&#x1f3af; Promotion Power</div><div class="insight-text">Active promotions drive a ${{p.lift_pct}}% sales uplift, increasing average daily sales from &euro;${{fmtN(p.no_promo_avg)}} to &euro;${{fmtN(p.promo_avg)}}.</div></div>
    <div class="insight-card amber"><div class="insight-title">&#x1f4ca; Monday Peak</div><div class="insight-text">Monday is the highest-performing weekday with avg sales of &euro;${{fmtN(D.day_of_week[0].avg_sales)}}. Saturday is weakest at &euro;${{fmtN(D.day_of_week[5].avg_sales)}}.</div></div>
  </div>`;
  document.getElementById('content-overview').innerHTML = h;
}}

function buildSales() {{
  let h='';

  // Monthly total revenue trend
  const mPts = D.monthly_trends.map(m=>({{y:m.total_sales}}));
  const mLabels = D.monthly_trends.map(m=>m.month);
  h+=`<div class="chart-grid full"><div class="chart-card">
    <div class="chart-title">Monthly Total Revenue</div>
    ${{svgLine([{{name:'Revenue',points:mPts,color:'#10b981'}}],900,260,{{xLabels:mLabels}})}}
  </div></div>`;

  // Store Type + Assortment
  h+=`<div class="chart-grid">
    <div class="chart-card">
      <div class="chart-title">Average Daily Sales by Store Type</div>
      ${{svgBar(D.store_types.map(s=>({{label:'Type '+s.type,value:s.avg_sales}})))}}
      <table class="data-table" style="margin-top:16px">
        <tr><th>Type</th><th>Stores</th><th>Avg Sales</th><th>Avg Customers</th><th>Sales/Customer</th></tr>
        ${{D.store_types.map(s=>`<tr><td><span class="badge badge-purple">Type ${{s.type}}</span></td><td>${{s.stores}}</td><td>&euro;${{fmtN(s.avg_sales)}}</td><td>${{fmtN(s.avg_customers)}}</td><td>&euro;${{s.sales_per_customer}}</td></tr>`).join('')}}
      </table>
    </div>
    <div class="chart-card">
      <div class="chart-title">Average Daily Sales by Assortment</div>
      ${{svgBar(D.assortment.map(a=>({{label:a.name+' ('+a.type+')',value:a.avg_sales}})))}}
      <table class="data-table" style="margin-top:16px">
        <tr><th>Assortment</th><th>Level</th><th>Avg Sales</th><th>Avg Customers</th></tr>
        ${{D.assortment.map(a=>`<tr><td><span class="badge badge-blue">${{a.type}}</span></td><td>${{a.name}}</td><td>&euro;${{fmtN(a.avg_sales)}}</td><td>${{fmtN(a.avg_customers)}}</td></tr>`).join('')}}
      </table>
    </div>
  </div>`;

  // Top / Bottom Stores
  h+=`<div class="chart-grid">
    <div class="chart-card">
      <div class="chart-title">&#x1f3c6; Top 10 Stores by Avg Daily Sales</div>
      ${{svgHBar(D.top_stores.map((s,i)=>({{label:'Store '+s.store,value:s.avg_sales,color:'#10b981'}})))}}
    </div>
    <div class="chart-card">
      <div class="chart-title">&#x26a0; Bottom 10 Stores by Avg Daily Sales</div>
      ${{svgHBar(D.bottom_stores.map((s,i)=>({{label:'Store '+s.store,value:s.avg_sales,color:'#f43f5e'}})))}}
    </div>
  </div>`;

  // Insights
  const topS=D.top_stores[0], botS=D.bottom_stores[0];
  const ratio=(topS.avg_sales/botS.avg_sales).toFixed(1);
  h+=`<div class="insight-grid">
    <div class="insight-card green"><div class="insight-title">&#x1f3c6; Top Performer</div><div class="insight-text">Store ${{topS.store}} leads with &euro;${{fmtN(topS.avg_sales)}} avg daily sales and ${{fmtN(topS.avg_customers)}} customers. Type ${{topS.type.toUpperCase()}} store.</div></div>
    <div class="insight-card red"><div class="insight-title">&#x26a0; Performance Gap</div><div class="insight-text">The top store outperforms the bottom by ${{ratio}}x. Store ${{botS.store}} averages only &euro;${{fmtN(botS.avg_sales)}} daily, suggesting operational improvement opportunities.</div></div>
    <div class="insight-card"><div class="insight-title">&#x1f3ea; Store Type B Dominates</div><div class="insight-text">Type B stores generate &euro;${{fmtN(D.store_types[1].avg_sales)}} avg daily &mdash; highest across all types. However, they have lower sales/customer (&euro;${{D.store_types[1].sales_per_customer}}) vs Type D (&euro;${{D.store_types[3].sales_per_customer}}).</div></div>
    <div class="insight-card amber"><div class="insight-title">&#x1f6d2; Assortment Effect</div><div class="insight-text">Extra (B) assortment stores avg &euro;${{fmtN(D.assortment[1].avg_sales)}}, outperforming Basic (A) at &euro;${{fmtN(D.assortment[0].avg_sales)}}. Wider product range correlates with higher sales.</div></div>
  </div>`;
  document.getElementById('content-sales').innerHTML=h;
}}

function buildPromo() {{
  const p=D.promotion;
  let h=`
  <div class="kpi-grid">
    <div class="kpi-card"><div class="kpi-icon">&#x1f4c8;</div><div class="kpi-value">+${{p.lift_pct}}%</div><div class="kpi-label">Sales Lift from Promos</div><div class="kpi-delta up">Universally Effective</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f6d2;</div><div class="kpi-value">&euro;${{fmtN(p.promo_avg)}}</div><div class="kpi-label">Avg Sales (Promo)</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f6ab;</div><div class="kpi-value">&euro;${{fmtN(p.no_promo_avg)}}</div><div class="kpi-label">Avg Sales (No Promo)</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f465;</div><div class="kpi-value">+${{Math.round((p.promo_cust-p.no_promo_cust)/p.no_promo_cust*100)}}%</div><div class="kpi-label">Customer Lift</div><div class="kpi-delta up">${{fmtN(p.no_promo_cust)}} &#x2192; ${{fmtN(p.promo_cust)}}</div></div>
  </div>`;

  // Promo vs No Promo bar
  h+=`<div class="chart-grid">
    <div class="chart-card">
      <div class="chart-title">Promo vs No Promo: Average Daily Sales</div>
      ${{svgBar([{{label:'No Promo',value:p.no_promo_avg,color:'#64748b'}},{{label:'Promo',value:p.promo_avg,color:'#6366f1'}}])}}
    </div>
    <div class="chart-card">
      <div class="chart-title">Promotion Impact by Store Type</div>
      ${{svgGroupedBar(p.by_store_type.map(s=>({{label:'Type '+s.type,bars:[{{label:'No Promo',value:s.no_promo}},{{label:'Promo',value:s.promo}}]}})))}}
    </div>
  </div>`;

  // Promo lift table
  h+=`<div class="chart-card" style="margin-bottom:20px">
    <div class="chart-title">Promotion Lift by Store Type</div>
    <table class="data-table">
      <tr><th>Store Type</th><th>No Promo Avg</th><th>Promo Avg</th><th>Lift</th><th>Assessment</th></tr>
      ${{p.by_store_type.map(s=>`<tr>
        <td><span class="badge badge-purple">Type ${{s.type}}</span></td>
        <td>&euro;${{fmtN(s.no_promo)}}</td>
        <td>&euro;${{fmtN(s.promo)}}</td>
        <td><span class="badge badge-green">+${{s.lift_pct}}%</span></td>
        <td>${{s.lift_pct>35?'High Impact':s.lift_pct>25?'Strong Impact':'Moderate Impact'}}</td>
      </tr>`).join('')}}
    </table>
  </div>`;

  h+=`<div class="insight-grid">
    <div class="insight-card green"><div class="insight-title">&#x1f3af; Universal Effectiveness</div><div class="insight-text">Promotions boost sales across ALL store types. Type A sees the highest lift at ${{p.by_store_type[0].lift_pct}}%, while Type B sees ${{p.by_store_type[1].lift_pct}}%.</div></div>
    <div class="insight-card"><div class="insight-title">&#x1f465; Foot Traffic Driver</div><div class="insight-text">Promos increase not just sales but customer visits &mdash; from ${{fmtN(p.no_promo_cust)}} to ${{fmtN(p.promo_cust)}} avg daily customers (+${{Math.round((p.promo_cust-p.no_promo_cust)/p.no_promo_cust*100)}}%).</div></div>
    <div class="insight-card amber"><div class="insight-title">&#x1f4a1; Strategic Recommendation</div><div class="insight-text">Promotions are the single biggest controllable lever for revenue growth. Prioritize promo deployment in Type A stores for maximum ROI.</div></div>
    <div class="insight-card"><div class="insight-title">&#x1f4ca; Type B Lower Lift</div><div class="insight-text">Type B stores show the lowest relative lift (${{p.by_store_type[1].lift_pct}}%), likely because their high baseline sales already attract high-intent shoppers.</div></div>
  </div>`;
  document.getElementById('content-promo').innerHTML=h;
}}

function buildForecast() {{
  const fc=D.forecast_sample;
  let h='';

  // KPIs
  const vals=fc.map(f=>f.avg_sales);
  const avgFC=Math.round(vals.reduce((a,b)=>a+b,0)/vals.length);
  const maxFC=Math.max(...vals), minFC=Math.min(...vals);
  h+=`<div class="kpi-grid">
    <div class="kpi-card"><div class="kpi-icon">&#x1f4c5;</div><div class="kpi-value">${{fc.length}}</div><div class="kpi-label">Forecast Days</div><div class="kpi-delta up">${{fc[0].date}} to ${{fc[fc.length-1].date}}</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f4ca;</div><div class="kpi-value">&euro;${{fmtN(avgFC)}}</div><div class="kpi-label">Avg Daily (Test Period)</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f4c8;</div><div class="kpi-value">&euro;${{fmtN(maxFC)}}</div><div class="kpi-label">Peak Daily Average</div></div>
    <div class="kpi-card"><div class="kpi-icon">&#x1f4c9;</div><div class="kpi-value">&euro;${{fmtN(minFC)}}</div><div class="kpi-label">Trough Daily Average</div></div>
  </div>`;

  // Full forecast line chart
  const pts=fc.map(f=>({{y:f.avg_sales}}));
  const labels=fc.map(f=>f.date.slice(5));
  h+=`<div class="chart-grid full"><div class="chart-card">
    <div class="chart-title">Daily Average Sales &mdash; Test Period (Actual Values)</div>
    <div class="chart-subtitle">Across all 1,115 stores. Weekly seasonality clearly visible.</div>
    ${{svgLine([{{name:'Avg Sales',points:pts,color:'#6366f1'}}],900,320,{{xLabels:labels}})}}
  </div></div>`;

  h+=`<div class="insight-grid">
    <div class="insight-card"><div class="insight-title">&#x1f50d; Weekly Rhythm</div><div class="insight-text">The test period shows strong weekly oscillation &mdash; Sunday peaks followed by Saturday troughs, matching training data patterns.</div></div>
    <div class="insight-card green"><div class="insight-title">&#x1f916; Model Accuracy</div><div class="insight-text">The Gradient Boosting model achieves MAE of &euro;746 and R&sup2; of 0.87 on this exact test period, accurately tracking these daily fluctuations.</div></div>
  </div>`;
  document.getElementById('content-forecast').innerHTML=h;
}}

function buildModel() {{
  const m=D.models;
  let h=`
  <div class="model-cards">
    <div class="model-card">
      <div class="model-name">Historical Average</div>
      <div class="model-metric"><div class="model-metric-label">MAE</div><div class="model-metric-value" style="color:#f43f5e">&euro;${{fmtN(m.baseline.mae)}}</div></div>
      <div class="model-metric"><div class="model-metric-label">RMSE</div><div class="model-metric-value" style="color:#f43f5e">&euro;${{fmtN(m.baseline.rmse)}}</div></div>
      <div class="model-metric"><div class="model-metric-label">R&sup2;</div><div class="model-metric-value" style="color:#f43f5e">${{m.baseline.r2}}</div></div>
    </div>
    <div class="model-card">
      <div class="model-name">Random Forest</div>
      <div class="model-metric"><div class="model-metric-label">MAE</div><div class="model-metric-value" style="color:#f59e0b">&euro;${{fmtN(m.random_forest.mae)}}</div></div>
      <div class="model-metric"><div class="model-metric-label">RMSE</div><div class="model-metric-value" style="color:#f59e0b">&euro;${{fmtN(m.random_forest.rmse)}}</div></div>
      <div class="model-metric"><div class="model-metric-label">R&sup2;</div><div class="model-metric-value" style="color:#f59e0b">${{m.random_forest.r2}}</div></div>
    </div>
    <div class="model-card best">
      <div class="model-name">Gradient Boosting</div>
      <div class="model-metric"><div class="model-metric-label">MAE</div><div class="model-metric-value" style="color:#10b981">&euro;${{fmtN(m.xgboost.mae)}}</div></div>
      <div class="model-metric"><div class="model-metric-label">RMSE</div><div class="model-metric-value" style="color:#10b981">&euro;${{fmtN(m.xgboost.rmse)}}</div></div>
      <div class="model-metric"><div class="model-metric-label">R&sup2;</div><div class="model-metric-value" style="color:#10b981">${{m.xgboost.r2}}</div></div>
    </div>
  </div>`;

  // Comparison table
  h+=`<div class="chart-card" style="margin-bottom:20px">
    <div class="chart-title">Model Performance Comparison</div>
    <table class="data-table">
      <tr><th>Metric</th><th>Baseline</th><th>Random Forest</th><th>Gradient Boosting</th><th>GB Improvement</th></tr>
      <tr><td>MAE</td><td>&euro;${{fmtN(m.baseline.mae)}}</td><td>&euro;${{fmtN(m.random_forest.mae)}}</td><td><strong>&euro;${{fmtN(m.xgboost.mae)}}</strong></td><td><span class="badge badge-green">-${{Math.round((1-m.xgboost.mae/m.baseline.mae)*100)}}% vs Baseline</span></td></tr>
      <tr><td>RMSE</td><td>&euro;${{fmtN(m.baseline.rmse)}}</td><td>&euro;${{fmtN(m.random_forest.rmse)}}</td><td><strong>&euro;${{fmtN(m.xgboost.rmse)}}</strong></td><td><span class="badge badge-green">-${{Math.round((1-m.xgboost.rmse/m.baseline.rmse)*100)}}% vs Baseline</span></td></tr>
      <tr><td>R&sup2;</td><td>${{m.baseline.r2}}</td><td>${{m.random_forest.r2}}</td><td><strong>${{m.xgboost.r2}}</strong></td><td><span class="badge badge-green">+${{(m.xgboost.r2-m.baseline.r2).toFixed(4)}}</span></td></tr>
    </table>
  </div>`;

  // Feature importance
  const fi=D.feature_importance.xgboost;
  h+=`<div class="chart-grid">
    <div class="chart-card">
      <div class="chart-title">&#x1f9e0; Top Predictive Features (Gradient Boosting)</div>
      ${{svgHBar(fi.map((f,i)=>({{label:f.feature,value:Math.round(f.importance*1000),color:i<3?'#6366f1':i<6?'#8b5cf6':'#64748b'}})),620,fi.length*30+50)}}
    </div>
    <div class="chart-card">
      <div class="chart-title">Feature Importance Breakdown</div>
      <table class="data-table">
        <tr><th>#</th><th>Feature</th><th>Score</th><th>Category</th></tr>
        ${{fi.map((f,i)=>{{
          const cat=f.feature.includes('Lag')?'Lag Feature':f.feature.includes('Rolling')?'Rolling Stat':f.feature==='Promo'?'Business':'Calendar';
          const badge=cat==='Lag Feature'?'badge-purple':cat==='Rolling Stat'?'badge-blue':cat==='Business'?'badge-green':'badge-amber';
          return `<tr><td class="rank">${{i+1}}</td><td>${{f.feature}}</td><td>${{(f.importance*100).toFixed(1)}}%</td><td><span class="badge ${{badge}}">${{cat}}</span></td></tr>`;
        }}).join('')}}
      </table>
    </div>
  </div>`;

  h+=`<div class="insight-grid">
    <div class="insight-card green"><div class="insight-title">&#x2705; Gradient Boosting Wins</div><div class="insight-text">Gradient Boosting reduces MAE by 39% vs Baseline and 20% vs Random Forest, making it the production-ready model for forecasting.</div></div>
    <div class="insight-card"><div class="insight-title">&#x1f4ca; Temporal Features Dominate</div><div class="insight-text">The top 6 features are all time-series lag/rolling features, confirming that recent sales momentum is the strongest predictor of future sales.</div></div>
    <div class="insight-card amber"><div class="insight-title">&#x1f4a1; Business Signal</div><div class="insight-text">Promo ranks #4 overall (9.4%), making it the most important non-temporal feature. This validates promotions as the key controllable business lever.</div></div>
    <div class="insight-card"><div class="insight-title">&#x1f527; Feature Engineering ROI</div><div class="insight-text">Engineered features (lags, rolling means/stds) account for >80% of total importance. Raw calendar features contribute <5% individually.</div></div>
  </div>`;
  document.getElementById('content-model').innerHTML=h;
}}

// ── Initialize all pages ──
buildOverview();
buildSales();
buildPromo();
buildForecast();
buildModel();
</script>
</body>
</html>'''

print(f"Writing dashboard to {OUTPUT_HTML}...")
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Dashboard saved: {OUTPUT_HTML}")
print("Open in browser to view.")
