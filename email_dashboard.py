
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# ============================================
# Placeholder Data Generation
# ============================================
np.random.seed(42)
dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq="D")
sample_size = 500
random_dates = np.random.choice(dates, sample_size)
categories = ["ABAC", "COI", "Data Protection", "IPT", "Sanctions"]
sub_categories = ["ISO 37001", "Gifts & Entertainment", "COI Declaration", "Data Breach", "IPT Policies"]
chatbot_flags = np.random.choice(["Yes", "No"], sample_size, p=[0.4, 0.6])

df = pd.DataFrame({
    "DateTimeReceived": random_dates,
    "Category": np.random.choice(categories, sample_size),
    "Sub-Category": np.random.choice(sub_categories, sample_size),
    "Chatbot_Addressable": chatbot_flags
})

# ============================================
# Sidebar Filters
# ============================================
st.sidebar.header("Filters")
selected_categories = st.sidebar.multiselect("Select Categories", categories)
date_range = st.sidebar.date_input("Select Date Range", [df["DateTimeReceived"].min(), df["DateTimeReceived"].max()])

filtered_df = df[
    (df["DateTimeReceived"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))) &
    (df["Category"].isin(selected_categories) if selected_categories else True)
]

# ============================================
# KPI Calculations
# ============================================
today = pd.Timestamp.today()
total_ytd = len(filtered_df)
total_mtd = filtered_df[filtered_df['DateTimeReceived'].dt.month == today.month].shape[0]
total_wtd = filtered_df[filtered_df['DateTimeReceived'].dt.isocalendar().week == today.isocalendar().week].shape[0]
total_today = filtered_df[filtered_df['DateTimeReceived'].dt.date == today.date()].shape[0]
pct_chatbot = (filtered_df[filtered_df['Chatbot_Addressable'] == 'Yes'].shape[0] / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
manual_time_min = len(filtered_df) * 4
chatbot_time_min = filtered_df[filtered_df['Chatbot_Addressable'] == 'Yes'].shape[0] * 0.1
time_saved_hours = (manual_time_min - chatbot_time_min) / 60
fte_saved = time_saved_hours / 160

# ============================================
# Dashboard Layout
# ============================================
st.title("📊 Email Operations Dashboard")

# KPI Cards
st.subheader("Key Metrics")
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
col1.metric("Total YTD", total_ytd)
col2.metric("Total MTD", total_mtd)
col3.metric("Total WTD", total_wtd)
col4.metric("Today", total_today)
col5.metric("Chatbot %", f"{pct_chatbot:.1f}%")
col6.metric("Hours Saved", f"{time_saved_hours:.2f}")
col7.metric("FTE Saved", f"{fte_saved:.2f}")

# ============================================
# Charts
# ============================================
st.subheader("Volume Trends")

# Monthly Trend
df_monthly = filtered_df.groupby(filtered_df['DateTimeReceived'].dt.to_period('M')).size().reset_index(name='Email Count')
df_monthly['Month'] = df_monthly['DateTimeReceived'].astype(str)
fig_monthly = px.line(df_monthly, x='Month', y='Email Count', title='Emails per Month', markers=True)
st.plotly_chart(fig_monthly, use_container_width=True)

# Daily Trend
df_daily = filtered_df.groupby(filtered_df['DateTimeReceived'].dt.date).size().reset_index(name='Email Count')
fig_daily = px.line(df_daily, x='DateTimeReceived', y='Email Count', title='Daily Email Volume', markers=True)
st.plotly_chart(fig_daily, use_container_width=True)

# Hourly Distribution
df_hourly = filtered_df.groupby(filtered_df['DateTimeReceived'].dt.hour).size().reset_index(name='Email Count')
fig_hourly = px.bar(df_hourly, x='DateTimeReceived', y='Email Count', title='Hourly Email Distribution')
st.plotly_chart(fig_hourly, use_container_width=True)

# Category Breakdown
st.subheader("Category Insights")
df_category = filtered_df['Category'].value_counts().reset_index()
df_category.columns = ['Category', 'Email Count']
fig_category = px.bar(df_category, x='Email Count', y='Category', orientation='h', title='Email Distribution by Category')
st.plotly_chart(fig_category, use_container_width=True)

# Chatbot Automation Pie
st.subheader("Automation Opportunity")
df_chatbot = filtered_df['Chatbot_Addressable'].value_counts().reset_index()
df_chatbot.columns = ['Chatbot', 'Count']
fig_chatbot = px.pie(df_chatbot, names='Chatbot', values='Count', title='Chatbot vs Human Required')
st.plotly_chart(fig_chatbot, use_container_width=True)

# Drill-down
st.subheader("Drill-down by Sub-Category")
if selected_categories:
    df_subcat = filtered_df.groupby('Sub-Category').size().reset_index(name='Email Count')
    fig_subcat = px.bar(df_subcat, x='Email Count', y='Sub-Category', orientation='h', title='Sub-Category Breakdown')
    st.plotly_chart(fig_subcat, use_container_width=True)

# ============================================
# Alerts
# ============================================
st.subheader("Actionable Alerts")
if len(filtered_df) > 0:
    peak_day = df_daily.loc[df_daily['Email Count'].idxmax()]
    st.warning(f"⚠ Peak Day: {peak_day['DateTimeReceived']} with {peak_day['Email Count']} emails.")
    if 'Data Protection' in filtered_df['Category'].values:
        st.error("🚨 Data Protection emails detected! Review for potential breaches.")
else:
    st.info("No data available for selected filters.")
