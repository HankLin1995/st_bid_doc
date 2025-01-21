import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from docx_utils import read_tender_document

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

projects = get_projects()
df = pd.DataFrame(projects)

my_pass=st.sidebar.text_input("請輸入密碼",type="password")

if my_pass!=os.getenv("PASSWORD"):
    st.stop()

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

            st.markdown("---")
            
            st.markdown("#### 📄 文件產生")
            document_templates = {
                "招標簽-已核定-未達兩千萬": "招標簽(新)-工程-已核定-未達兩千萬.txt",
                "招標簽-未核定-未達兩千萬": "招標簽(新)-工程-未核定-未達兩千萬.txt",
                "預算書簽-已核定-委外": "預算書簽(新)-工程-已核定-委外.txt",
                "預算書簽-已核定": "預算書簽(新)-工程-已核定.txt",
                "預算書簽-未核定-委外": "預算書簽(新)-工程-未核定-委外.txt",
                "預算書簽-未核定": "預算書簽(新)-工程-未核定.txt"
            }
            
            selected_template = st.selectbox(
                "選擇文件範本",
                options=list(document_templates.keys())
            )
            
            if st.button("產生文件"):
                template_path = os.path.join("src", "公文DI", document_templates[selected_template])
                output_path = os.path.join("output", f"{selected_project}_{document_templates[selected_template]}")
                
                if project_data.get('total_budget', 0) >= 200000000:
                    project_category = "未達二千萬之第三類工程"
                else:
                    project_category = "二千萬元以上未達查核金額之第二類工程"

                from view_biddoc import get_contractor, get_cost_range

                # 準備替換的資料
                replacements = {
                    "工程名稱": project_data['project_name'],
                    "經費來源": project_data['funding_source'],
                    "民國年": str(project_data.get('year', '113')),
                    "所屬分處": project_data.get('branch_office', '台北分處'),
                    "委外廠商": project_data.get('supervisor', ''),
                    "工程編號": project_data.get('project_number', '').replace("雲林","YL"),
                    "採購標的": "工程",
                    "核定經費": format_currency(project_data.get('approved_budget', 0)).replace("NT$ ", "") + "元整",
                    "預算書總價": format_currency(project_data.get('total_budget', 0)).replace("NT$ ", "") + "元整",
                    "發包工作費總額": format_currency(project_data.get('contract_amount', 0)).replace("NT$ ", "") + "元整",
                    "工程分類": project_category,
                    "押標金額度": format_currency(project_data.get('bid_bond', 0)).replace("NT$ ", "") + "元整",
                    "廠商基本資格": get_contractor(project_data.get('contract_amount', 0)),
                    "採購金額級距": get_cost_range(project_data.get('contract_amount', 0)),
                    "履約保證金": format_currency(project_data.get('performance_bond', 0)).replace("NT$ ", "") + "元整",
                }
                
                st.json(replacements)

                # # 確保output目錄存在
                # os.makedirs("output", exist_ok=True)
                
                # # 產生文件
                # read_tender_document(template_path, replacements, output_path)
                # st.success(f"文件已產生：{output_path}")
    else:
        st.info("目前沒有工程案件資料")