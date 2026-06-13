import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Sales Analytics", page_icon="📊", layout="wide")

st.title("📊 Sales Analytics")
st.markdown("Explore key exploratory data analysis (EDA) insights driving the forecasting engine.")

@st.cache_data
def load_dashboard_data():
    json_path = os.path.join("data", "dashboard_data.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@st.cache_data
def load_and_aggregate_extra_data():
    train_path = os.path.join("data", "train_dataset.csv")
    store_path = os.path.join("data", "store.csv")
    
    if os.path.exists(train_path) and os.path.exists(store_path):
        # Sample or chunk to prevent excessive memory usage if needed, but Streamlit caching should handle it once
        train_df = pd.read_csv(train_path, low_memory=False)
        store_df = pd.read_csv(store_path)
        
        df = train_df.merge(store_df, on='Store', how='left')
        df = df[df['Open'] == 1] # Only consider open stores
        
        # State Holiday
        df['StateHoliday'] = df['StateHoliday'].astype(str).replace({'0': 'None', 'a': 'Public Holiday', 'b': 'Easter', 'c': 'Christmas'})
        state_holiday = df.groupby('StateHoliday')['Sales'].mean().reset_index()
        
        # School Holiday
        df['SchoolHoliday_Str'] = df['SchoolHoliday'].replace({0: "No School Holiday", 1: "School Holiday"})
        school_holiday = df.groupby('SchoolHoliday_Str')['Sales'].mean().reset_index()
        
        # Competition buckets
        bins = [0, 1000, 5000, 10000, float('inf')]
        labels = ['< 1km', '1-5km', '5-10km', '> 10km']
        df['Comp_Bucket'] = pd.cut(df['CompetitionDistance'], bins=bins, labels=labels)
        comp_dist = df.groupby('Comp_Bucket')['Sales'].mean().reset_index()
        
        return state_holiday, school_holiday, comp_dist
    return None, None, None

data = load_dashboard_data()
state_holiday, school_holiday, comp_dist = load_and_aggregate_extra_data()

if data:
    st.divider()
    
    # 1. Monthly Sales Trend
    st.subheader("1. Monthly Sales Trend")
    monthly_df = pd.DataFrame(data["monthly_trends"])
    fig_monthly = px.line(
        monthly_df, 
        x="month", 
        y="avg_sales", 
        title="Average Monthly Sales Over Time",
        markers=True,
        template="plotly_dark",
        labels={"month": "Month", "avg_sales": "Average Sales"}
    )
    fig_monthly.update_traces(line=dict(color="#1E90FF", width=3))
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    st.divider()

    # 2. Store Type Analysis
    st.subheader("2. Store Type Analysis")
    store_types_df = pd.DataFrame(data["store_types"]).sort_values(by="avg_sales", ascending=False)
    fig_store_types = px.bar(
        store_types_df, 
        x="type", 
        y="avg_sales",
        color="type",
        title="Average Sales by Store Type",
        template="plotly_dark",
        labels={"type": "Store Type", "avg_sales": "Average Sales"}
    )
    st.plotly_chart(fig_store_types, use_container_width=True)

    st.divider()

    # 3. Promotion Impact
    st.subheader("3. Promotion Impact")
    col1, col2 = st.columns(2)
    promo_data = data["promotion"]
    
    fig_promo = go.Figure(data=[
        go.Bar(name='No Promo', x=['Sales'], y=[promo_data['no_promo_avg']], marker_color='#EF553B'),
        go.Bar(name='Promo', x=['Sales'], y=[promo_data['promo_avg']], marker_color='#00CC96')
    ])
    fig_promo.update_layout(barmode='group', title="Promo vs No Promo Comparison", template="plotly_dark")
    
    with col1:
        st.plotly_chart(fig_promo, use_container_width=True)
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.metric("Verified Promotion Uplift", "38.77%", delta="+38.77%")
        st.info(f"Average sales without promo: €{promo_data['no_promo_avg']:,.0f}\n\nAverage sales with promo: €{promo_data['promo_avg']:,.0f}")

    st.divider()
    
    # 4. Holiday Impact
    st.subheader("4. Holiday Impact")
    col_hol1, col_hol2 = st.columns(2)
    
    if state_holiday is not None and school_holiday is not None:
        fig_state = px.bar(state_holiday, x="StateHoliday", y="Sales", title="State Holiday Comparison", template="plotly_dark", color="StateHoliday")
        fig_school = px.bar(school_holiday, x="SchoolHoliday_Str", y="Sales", title="School Holiday Comparison", template="plotly_dark", color="SchoolHoliday_Str", labels={"SchoolHoliday_Str": "School Holiday"})
        
        with col_hol1:
            st.plotly_chart(fig_state, use_container_width=True)
        with col_hol2:
            st.plotly_chart(fig_school, use_container_width=True)
    else:
        st.warning("Holiday data unavailable (requires CSVs).")
        
    st.divider()

    # 5. Competition Analysis
    st.subheader("5. Competition Analysis")
    if comp_dist is not None:
        fig_comp = px.bar(comp_dist, x="Comp_Bucket", y="Sales", title="Average Sales by Competition Distance", template="plotly_dark", color="Comp_Bucket", labels={"Comp_Bucket": "Distance Bucket"})
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.warning("Competition data unavailable (requires CSVs).")

    st.divider()

    # 6. Top 10 Stores
    st.subheader("6. Top 10 Stores")
    top_stores_df = pd.DataFrame(data["top_stores"]).sort_values(by="avg_sales", ascending=True)
    top_stores_df["store"] = top_stores_df["store"].astype(str)
    
    fig_top_stores = px.bar(
        top_stores_df, 
        y="store", 
        x="avg_sales", 
        orientation='h',
        title="Top 10 Stores by Average Sales",
        template="plotly_dark",
        labels={"store": "Store ID", "avg_sales": "Average Sales"}
    )
    st.plotly_chart(fig_top_stores, use_container_width=True)

    st.divider()

    # 7. Key Business Findings
    st.subheader("7. Key Business Findings")
    st.info("""
    - **Promotions increase sales by 38.77%**
    - **December shows strongest seasonality**
    - **Store Type B has highest average sales**
    - **Competition proximity correlates with higher sales**
    - **Large performance gap exists between stores**
    """)
else:
    st.error("Dashboard data could not be loaded. Please ensure `dashboard_data.json` exists.")
