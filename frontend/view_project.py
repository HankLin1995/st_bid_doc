import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

load_dotenv()

BACKEND_URL = 'http://backend:8000'

def format_currency(value):
    if pd.isna(value):
        return "NT$ 0"
    return f"NT$ {value:,.0f}"

def get_projects():
    response = requests.get(f"{BACKEND_URL}/projects/all")
    if response.status_code == 200:
        return response.json()
    return []

def delete_project(project_id):
    response = requests.delete(f"{BACKEND_URL}/projects/{project_id}")
    return response.status_code == 200

# my_pass=st.sidebar.text_input("請輸入密碼",type="password")

# if my_pass!=os.getenv("PASSWORD"):
#     st.stop()

st.markdown("### 📊 工程案件總覽")

# Get all projects
projects = get_projects()

if projects:
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(projects)
    
    # Add filters in sidebar
    st.sidebar.markdown("### 篩選條件")

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

    # Display project table
    st.dataframe(
        df[[
            'id','project_number', 'project_name', 'branch_office', 
            'total_budget', 'status', 'created_at'
        ]].rename(columns={
            'id':'案件ID',
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

    # Delete button

    with st.container(border=True,expanded=False):

        project_id=st.number_input("案件ID",min_value=0)

        if st.button("刪除"):
            delete_project(project_id)
            st.success("工程案件已刪除")
            st.rerun()

    # Statistical Analysis Section
    st.markdown("---")
    st.markdown("### 📈 統計分析")

    # Create two columns for charts
    col1, col2 = st.columns(2)

    with col1:
        # Project Status Distribution
        status_counts = df['branch_office'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title='工程案件分布'
        )
        st.plotly_chart(fig_status)

    with col2:
        # Budget Distribution by Year
        yearly_budget = df.groupby('year')['total_budget'].sum().reset_index()
        fig_budget = px.bar(
            yearly_budget,
            x='year',
            y='total_budget',
            title='年度預算分布',
            labels={'year': '年度', 'total_budget': '總預算'}
        )
        fig_budget.update_traces(texttemplate='NT$ %{y:,.0f}', textposition='outside')
        st.plotly_chart(fig_budget)

    # # Project Timeline Analysis
    # st.markdown("### 📅 工期分析")
    
    # # Calculate average duration by year
    # avg_duration = df.groupby('year')['duration'].mean().reset_index()
    # fig_duration = go.Figure()
    # fig_duration.add_trace(go.Scatter(
    #     x=avg_duration['year'],
    #     y=avg_duration['duration'],
    #     mode='lines+markers+text',
    #     name='平均工期',
    #     text=avg_duration['duration'].round(1),
    #     textposition='top center'
    # ))
    # fig_duration.update_layout(
    #     title='年度平均工期(天數)',
    #     xaxis_title='年度',
    #     yaxis_title='平均天數'
    # )
    # st.plotly_chart(fig_duration)

    # # Key Metrics
    # st.markdown("### 🎯 重要指標")
    # metric1, metric2, metric3, metric4 = st.columns(4)
    
    # with metric1:
    #     total_projects = len(df)
    #     st.metric("總案件數", total_projects)
    
    # with metric2:
    #     total_budget = df['total_budget'].sum()
    #     st.metric("總預算", format_currency(total_budget))
    
    # with metric3:
    #     avg_duration = df['duration'].mean()
    #     st.metric("平均工期", f"{avg_duration:.1f} 天")
    
    # with metric4:
    #     completed_rate = (df['status'] == '已完工').mean() * 100
    #     st.metric("完工率", f"{completed_rate:.1f}%")

else:
    st.info("目前沒有工程案件資料")