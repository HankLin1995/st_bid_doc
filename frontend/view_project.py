import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

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

my_pass=st.sidebar.text_input("請輸入密碼",type="password")

if my_pass!=os.getenv("PASSWORD"):
    st.stop()

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

    # select project

    st.markdown("---")

    st.markdown("### 🔍 專案詳細資訊")

    # Project selection
    selected_project = st.selectbox(
        "選擇專案",
        options=df['project_number'].tolist(),
        format_func=lambda x: f"{x} - {df[df['project_number']==x]['project_name'].iloc[0]}"
        )

    with st.expander("詳細資訊"):

        if selected_project:
            project_data = df[df['project_number'] == selected_project].iloc[0]

            with st.container():
                st.markdown("#### 📋 基本資訊")
                cols1 = st.columns(3)
                with cols1[0]:
                    st.markdown(" 🔹 **年度**")
                    st.markdown(f"{project_data['year']}")
                    st.markdown(" 🔹 **標案案號**")
                    st.markdown(f"{project_data['project_number']}")
                
                with cols1[1]:
                    st.markdown(" 🔹 **工程名稱**")
                    st.markdown(f"{project_data['project_name']}")
                    st.markdown(" 🔹 **工期**")
                    st.markdown(f"{project_data['duration']} 天")
                
                with cols1[2]:
                    st.markdown(" 🔹 **工程地點**")
                    st.markdown(f"{project_data['location']}")
                
                st.markdown(" 🔹 **工程內容**")
                st.markdown(f"{project_data['construction_content']}")

                st.markdown("---")

                st.markdown("#### 💰 預算資訊")
                cols2 = st.columns(4)
                with cols2[0]:
                    st.markdown(" 🔹 **經費來源**")
                    st.markdown(f"{project_data['funding_source']}")
                with cols2[1]:
                    st.markdown(" 🔹 **核定金額**")
                    st.markdown(f"{format_currency(project_data['approved_amount'])}")
                with cols2[2]:
                    st.markdown(" 🔹 **預算金額**")
                    st.markdown(f"{format_currency(project_data['total_budget'])}")
                with cols2[3]:
                    st.markdown(" 🔹 **契約金額**")
                    st.markdown(f"{format_currency(project_data['contract_amount'])}")

                st.markdown("---")

                st.markdown("#### 👥 監造資訊")
                cols3 = st.columns(4)
                with cols3[0]:
                    st.markdown(" 🔹 **分處**")
                    st.markdown(f"{project_data['branch_office']}")
                with cols3[1]:
                    st.markdown(" 🔹 **主辦監造**")
                    st.markdown(f"{project_data['supervisor']}")
                with cols3[2]:
                    st.markdown(" 🔹 **監造人員**")
                    st.markdown(f"{project_data['supervisor_personnel']}")
                with cols3[3]:
                    st.markdown(" 🔹 **狀態**")
                    st.markdown(f"{project_data['status']}")
else:
    st.info("目前沒有工程案件資料")