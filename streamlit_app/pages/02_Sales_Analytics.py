import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# -----------------------------------------------------------------------------
# Path Resolution
# -----------------------------------------------------------------------------
# Resolve BASE_DIR relative to the location of this script (streamlit_app/pages/02_Sales_Analytics.py)
# __file__ -> pages -> app -> Sales Forecasting Analysis
try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
except NameError:
    # Fallback for interactive environments
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))

# -----------------------------------------------------------------------------
# Custom CSS for Enterprise Dark Theme
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Dark Theme KPI Cards */
    div[data-testid="metric-container"] {
        background-color: #1E1E2F;
        border: 1px solid #32324E;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="metric-container"] > div {
        color: #E2E8F0;
    }
    .main-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
@st.cache_data
def load_dashboard_data():
    """Loads pre-aggregated JSON dashboard data from the original analysis."""
    json_path = os.path.join(BASE_DIR, "data", "dashboard_data.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@st.cache_data
def load_competition_data():
    """Dynamically loads and aggregates competition distance data from CSVs."""
    store_path = os.path.join(BASE_DIR, "data", "store.csv")
    train_path = os.path.join(BASE_DIR, "data", "train_store_cleaned.csv")
    
    # Fallback if the cleaned csv is missing
    if not os.path.exists(train_path):
        train_path = os.path.join(BASE_DIR, "data", "train_dataset.csv")

    if os.path.exists(train_path) and os.path.exists(store_path):
        try:
            # Memory-efficient loading
            df = pd.read_csv(train_path, usecols=['Store', 'Sales'], low_memory=False)
            store_df = pd.read_csv(store_path, usecols=['Store', 'CompetitionDistance'])
            
            df = df.merge(store_df, on='Store', how='inner')
            
            # Create Distance Buckets
            bins = [0, 1000, 5000, 10000, float('inf')]
            labels = ['< 1km', '1-5km', '5-10km', '> 10km']
            df['Comp_Bucket'] = pd.cut(df['CompetitionDistance'], bins=bins, labels=labels)
            
            # Aggregate Average Sales
            comp_dist = df.groupby('Comp_Bucket', observed=False)['Sales'].mean().reset_index()
            return comp_dist
        except Exception:
            return None
    return None

def apply_plotly_dark_theme(fig):
    """Applies a consistent enterprise dark theme to all Plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0"),
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor="#32324E"),
        yaxis=dict(showgrid=True, gridcolor="#32324E")
    )
    return fig

# -----------------------------------------------------------------------------
# Main UI Execution
# -----------------------------------------------------------------------------
st.markdown("<h1 class='main-header'>📊 Sales Analytics</h1>", unsafe_allow_html=True)
st.markdown("Deep dive into the operational metrics and store performance across the Rossmann network.")

# Load Data
data = load_dashboard_data()
comp_data = load_competition_data()

if data is None:
    st.error("⚠️ Dashboard data could not be found. Please ensure `dashboard_data.json` exists.")
    st.stop()

# --- KPI Cards ---
st.subheader("Network Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Raw Records", value="1,017,209")
with col2:
    st.metric(label="Cleaned Target Records", value="844,392")
with col3:
    st.metric(label="Total Stores", value="1,115")
with col4:
    st.metric(label="Verified Promo Lift", value="38.77%", delta="+38.77%", delta_color="normal")

st.markdown("<br>", unsafe_allow_html=True)

# --- Monthly Trend Analysis ---
st.subheader("Historical Sales Trajectory")
monthly_df = pd.DataFrame(data["monthly_trends"])

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=monthly_df["month"], 
    y=monthly_df["avg_sales"],
    mode='lines+markers',
    name='Avg Monthly Sales',
    line=dict(color='#3B82F6', width=3),
    marker=dict(size=8, color='#60A5FA')
))
fig_trend.update_layout(title="Average Daily Sales Volume over Time (Jan 2013 - Jul 2015)")
fig_trend = apply_plotly_dark_theme(fig_trend)
st.plotly_chart(fig_trend, use_container_width=True)

# --- Store Type & Assortment Breakdown ---
col_type, col_assort = st.columns(2)

with col_type:
    st.subheader("Performance by Store Type")
    types_df = pd.DataFrame(data["store_types"]).sort_values("avg_sales", ascending=True)
    fig_types = px.bar(
        types_df, 
        x="avg_sales", 
        y="type", 
        orientation='h',
        color="avg_sales",
        color_continuous_scale="Teal",
        title="Average Daily Sales by Store Type"
    )
    fig_types = apply_plotly_dark_theme(fig_types)
    fig_types.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_types, use_container_width=True)

with col_assort:
    st.subheader("Performance by Assortment")
    assort_df = pd.DataFrame(data["assortment"]).sort_values("avg_sales", ascending=True)
    fig_assort = px.bar(
        assort_df, 
        x="avg_sales", 
        y="name", 
        orientation='h',
        color="avg_sales",
        color_continuous_scale="Purp",
        title="Average Daily Sales by Assortment Level"
    )
    fig_assort = apply_plotly_dark_theme(fig_assort)
    fig_assort.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_assort, use_container_width=True)

# --- Store Rankings & Competition ---
st.markdown("<hr style='border: 1px solid #32324E'>", unsafe_allow_html=True)
st.subheader("Store Geography & Competition")

col_top, col_comp = st.columns(2)

with col_top:
    top_df = pd.DataFrame(data["top_stores"]).sort_values("avg_sales", ascending=True)
    top_df["store_str"] = "Store " + top_df["store"].astype(str)
    
    fig_top = px.bar(
        top_df, 
        x="avg_sales", 
        y="store_str", 
        orientation='h',
        title="Top 10 Stores (Daily Avg Revenue)",
        text_auto=".2s",
        color_discrete_sequence=["#10B981"]
    )
    fig_top = apply_plotly_dark_theme(fig_top)
    st.plotly_chart(fig_top, use_container_width=True)

with col_comp:
    if comp_data is not None:
        fig_comp = px.bar(
            comp_data, 
            x="Comp_Bucket", 
            y="Sales",
            title="Average Sales by Competition Distance Bucket",
            color="Comp_Bucket",
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig_comp = apply_plotly_dark_theme(fig_comp)
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.warning("⚠️ Competition data unavailable (requires CSVs).")

# --- Weekly Seasonality ---
st.markdown("<hr style='border: 1px solid #32324E'>", unsafe_allow_html=True)
st.subheader("Day of Week Traffic Dynamics")

dow_df = pd.DataFrame(data["day_of_week"])
fig_dow = go.Figure()

fig_dow.add_trace(go.Bar(
    x=dow_df["day"],
    y=dow_df["avg_sales"],
    name="Avg Sales (€)",
    marker_color="#8B5CF6",
    yaxis="y"
))

fig_dow.add_trace(go.Scatter(
    x=dow_df["day"],
    y=dow_df["avg_customers"],
    name="Avg Customers",
    mode="lines+markers",
    line=dict(color="#F59E0B", width=3),
    yaxis="y2"
))

fig_dow.update_layout(
    title="Sales Revenue vs Customer Footfall by Day",
    yaxis=dict(title="Average Sales (€)", titlefont=dict(color="#8B5CF6"), tickfont=dict(color="#8B5CF6")),
    yaxis2=dict(title="Average Customers", titlefont=dict(color="#F59E0B"), tickfont=dict(color="#F59E0B"), overlaying="y", side="right")
)
fig_dow = apply_plotly_dark_theme(fig_dow)
st.plotly_chart(fig_dow, use_container_width=True)

# --- Final Key Findings ---
st.markdown("<hr style='border: 1px solid #32324E'>", unsafe_allow_html=True)
st.subheader("Key Findings")
st.info("""
• Promotions increase sales by 38.77%

• December shows strongest seasonality

• Store Type B delivers highest average sales

• Competition proximity correlates with higher sales

• Sales_Lag_14 is the strongest predictor
""")
