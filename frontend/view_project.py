
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
# import plotly.express as px
# import plotly.graph_objects as go

load_dotenv()

BACKEND_URL = 'http://backend:8000'

def format_currency(value):
    if pd.isna(value):
        return "NT$ 0"
    return f"NT$ {value:,.0f}"

def get_projects():
    response = requests.get(f"{BACKEND_URL}/projects/")
    if response.status_code == 200:
        return response.json()
    return []

# def get_status_color(status):
#     colors = {
#         "初稿": "#1f77b4",  # 藍色
#         "預算書": "#ff7f0e",  # 橘色
#         "上網": "#2ca02c",  # 綠色
#         "決標": "#d62728"   # 紅色
#     }
#     return colors.get(status, "#7f7f7f")

# def create_status_chart(df):
#     status_counts = df['status'].value_counts()
#     fig = go.Figure(data=[go.Pie(
#         labels=status_counts.index,
#         values=status_counts.values,
#         hole=.3,
#         marker_colors=[get_status_color(status) for status in status_counts.index]
#     )])
#     fig.update_layout(
#         title="案件狀態分布",
#         showlegend=True,
#         height=300
#     )
#     return fig

# def create_budget_chart(df):
#     budget_by_branch = df.groupby('branch_office')['total_budget'].sum().sort_values(ascending=True)
#     fig = go.Figure(data=[go.Bar(
#         x=budget_by_branch.values,
#         y=budget_by_branch.index,
#         orientation='h'
#     )])
#     fig.update_layout(
#         title="各單位預算分布",
#         xaxis_title="預算金額",
#         height=300,
#         margin=dict(l=200)
#     )
#     fig.update_xaxes(tickformat=",.0f")
#     return fig

# def create_timeline_chart(df):
#     df['month'] = pd.to_datetime(df['created_at']).dt.to_period('M')
#     monthly_counts = df.groupby('month').size()
#     fig = go.Figure(data=[go.Scatter(
#         x=monthly_counts.index.astype(str),
#         y=monthly_counts.values,
#         mode='lines+markers'
#     )])
#     fig.update_layout(
#         title="案件提交時間軸",
#         xaxis_title="月份",
#         yaxis_title="案件數",
#         height=300
#     )
#     return fig

my_pass=st.sidebar.text_input("請輸入密碼",type="password")

if my_pass!=os.getenv("PASSWORD"):
    st.stop()

st.markdown("### 📋 工程案件總覽")

# Get all projects
projects = get_projects()

if projects:
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(projects)
    
    # Add filters in sidebar
    st.sidebar.markdown("### 🔍 篩選條件")

    # Year filter
    if 'year' in df.columns:
        years = sorted(df['year'].unique(), reverse=True)
        selected_year = st.sidebar.selectbox("年度", ["全部"] + list(years))
        if selected_year != "全部":
            df = df[df['year'] == selected_year]

    # Status filter
    if 'status' in df.columns:
        statuses = sorted(df['status'].unique())
        selected_status = st.sidebar.selectbox("案件狀態", ["全部"] + list(statuses))
        if selected_status != "全部":
            df = df[df['status'] == selected_status]

    # Branch office filter
    if 'branch_office' in df.columns:
        offices = sorted(df['branch_office'].unique())
        selected_office = st.sidebar.selectbox("單位", ["全部"] + list(offices))
        if selected_office != "全部":
            df = df[df['branch_office'] == selected_office]

    # Display summary statistics
    # col1, col2, col3, col4 = st.columns(4)
    # with col1:
    #     st.metric("案件總數", f"{len(df):,d} 件")
    # with col2:
    #     total_budget = df['total_budget'].sum()
    #     st.metric("預算總額", format_currency(total_budget))
    # with col3:
    #     avg_duration = df['duration'].mean()
    #     st.metric("平均工期", f"{avg_duration:.1f} 天")
    # with col4:
    #     completed = len(df[df['status'] == "決標"])
    #     st.metric("已決標案件", f"{completed:,d} 件")

    # Create tabs for different views
    # tab1, tab2 = st.tabs(["📊 列表檢視", "📈 統計分析"])

    # with tab1:
        # Add search box
    # search_term = st.text_input("🔍 搜尋案件 (案號或名稱)")
    
    # if search_term:
    #     df = df[
    #         df['project_number'].str.contains(search_term, case=False, na=False) |
    #         df['project_name'].str.contains(search_term, case=False, na=False)
    #     ]
    
    # Display projects in a table with custom formatting
    st.dataframe(
        df[[
            'project_number', 'project_name', 'branch_office', 
            'total_budget', 'status', 'created_at'
        ]].rename(columns={
            'project_number': '標案案號',
            'project_name': '工程名稱',
            'branch_office': '分處',
            'total_budget': '預算金額',
            'status': '狀態',
            'created_at': '建立時間'
        }).style.format({
            '預算金額': format_currency,
            '建立時間': lambda x: pd.to_datetime(x).strftime('%Y-%m-%d')
        }),
        use_container_width=True,
        hide_index=True
    )

    # with tab2:
    #     # Create three columns for charts
    #     chart_col1, chart_col2 = st.columns(2)
        
    #     with chart_col1:
    #         # Status distribution pie chart
    #         st.plotly_chart(create_status_chart(df), use_container_width=True)
            
    #     with chart_col2:
    #         # Budget distribution bar chart
    #         st.plotly_chart(create_budget_chart(df), use_container_width=True)
        
    #     # Timeline chart in full width
    #     st.plotly_chart(create_timeline_chart(df), use_container_width=True)
        
    #     # Additional statistics
    #     st.markdown("### 📊 統計摘要")
    #     stats_col1, stats_col2 = st.columns(2)
        
    #     with stats_col1:
    #         st.markdown("#### 預算統計")
    #         budget_stats = df['total_budget'].describe()
    #         st.write(f"最高預算: {format_currency(budget_stats['max'])}")
    #         st.write(f"最低預算: {format_currency(budget_stats['min'])}")
    #         st.write(f"平均預算: {format_currency(budget_stats['mean'])}")
            
    #     with stats_col2:
    #         st.markdown("#### 工期統計")
    #         duration_stats = df['duration'].describe()
    #         st.write(f"最長工期: {duration_stats['max']:.0f} 天")
    #         st.write(f"最短工期: {duration_stats['min']:.0f} 天")
    #         st.write(f"平均工期: {duration_stats['mean']:.1f} 天")

else:
    st.info("目前沒有工程案件資料")