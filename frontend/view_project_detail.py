import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from docx_utils import read_tender_document
import time

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

def update_project(project_id, project_data):
    response = requests.put(f"{BACKEND_URL}/projects/{project_id}", json=project_data)
    if response.status_code != 200:
        print(f"Error: {response.status_code}", response.json())
    return response.status_code == 200

projects = get_projects()
df = pd.DataFrame(projects)

# my_pass=st.sidebar.text_input("請輸入密碼",type="password")

# if my_pass!=os.getenv("PASSWORD"):
#     st.stop()

st.markdown("### 🔍 專案詳細資訊")

# Project selection
selected_project = st.selectbox(
    "選擇專案",
    options=df['project_number'].tolist(),
    format_func=lambda x: f"{x} - {df[df['project_number']==x]['project_name'].iloc[0]}"
)

tab1,tab2=st.tabs(["詳細資訊","簽呈"])

with tab1:

# with st.expander("詳細資訊"):
    if selected_project:
        project_data = df[df['project_number'] == selected_project].iloc[0]

        # Add edit mode toggle
        edit_mode = st.toggle("編輯模式")

        with st.container():
            st.markdown("#### 📋 基本資訊")
            cols1 = st.columns(3)
            with cols1[0]:
                if edit_mode:
                    year = st.text_input("年度", value=project_data['year'])
                else:
                    st.markdown(" 🔹 **年度**")
                    st.markdown(f"{project_data['year']}")

                st.markdown(" 🔹 **標案案號**")
                st.markdown(f"{project_data['project_number']}")
            
            with cols1[1]:

                if edit_mode:
                    project_name = st.text_input("工程名稱", value=project_data['project_name'])
                else:
                    st.markdown(" 🔹 **工程名稱**")
                    st.markdown(f"{project_data['project_name']}")

                if edit_mode:
                    duration = st.number_input("工期(天)", value=int(project_data['duration']))
                else:
                    st.markdown(" 🔹 **工期**")
                    st.markdown(f"{project_data['duration']} 天")
            
            with cols1[2]:

                if edit_mode:
                    location = st.text_input("工程地點", value=project_data['location'])
                else:
                    st.markdown(" 🔹 **工程地點**"  )
                    st.markdown(f"{project_data['location']}")

            if edit_mode:
                construction_content = st.text_area("工程內容", value=project_data['construction_content'])
            else:
                st.markdown(" 🔹 **工程內容**")
                st.markdown(f"{project_data['construction_content']}")

            st.markdown("---")

            st.markdown("#### 💰 預算資訊")
            cols2 = st.columns(4)
            with cols2[0]:

                if edit_mode:
                    funding_source = st.text_input("經費來源", value=project_data['funding_source'])
                else:
                    st.markdown(" 🔹 **經費來源**")
                    st.markdown(f"{project_data['funding_source']}")

            with cols2[1]:

                if edit_mode:
                    approved_amount = st.number_input("核定金額", value=project_data['approved_amount'] if pd.notna(project_data['approved_amount']) else 0)
                else:
                    st.markdown(" 🔹 **核定金額**")
                    st.markdown(f"{format_currency(project_data['approved_amount'])}")

                if edit_mode:
                    bid_bond = st.number_input("押標金金額", value=project_data['bid_bond'] if pd.notna(project_data['bid_bond']) else 0)
                else:
                    st.markdown(" 🔹 **押標金金額**")
                    st.markdown(f"{format_currency(project_data['bid_bond'])}")

            with cols2[2]:

                if edit_mode:
                    total_budget = st.number_input("預算金額", value=project_data['total_budget'] if pd.notna(project_data['total_budget']) else 0)
                else:
                    st.markdown(" 🔹 **預算金額**")
                    st.markdown(f"{format_currency(project_data['total_budget'])}")

                if edit_mode:
                    performance_bond = st.number_input("履約保證金金額", value=project_data['performance_bond'] if pd.notna(project_data['performance_bond']) else 0)
                else:
                    st.markdown(" 🔹 **履約保證金金額**")   
                    st.markdown(f"{format_currency(project_data['performance_bond'])}")

            with cols2[3]:

                if edit_mode:
                    contract_amount = st.number_input("契約金額", value=project_data['contract_amount'] if pd.notna(project_data['contract_amount']) else 0)
                else:
                    st.markdown(" 🔹 **契約金額**")
                    st.markdown(f"{format_currency(project_data['contract_amount'])}")

            st.markdown("---")

            st.markdown("#### 👥 監造資訊")
            cols3 = st.columns(4)

            with cols3[0]:

                if edit_mode:
                    branch_office = st.text_input("分處", value=project_data['branch_office'])
                else:
                    st.markdown(" 🔹 **分處**")
                    st.markdown(f"{project_data['branch_office']}")

            with cols3[1]:

                if edit_mode:
                    supervisor = st.text_input("主辦監造", value=project_data['supervisor'])
                else:
                    st.markdown(" 🔹 **主辦監造**")
                    st.markdown(f"{project_data['supervisor']}")

            with cols3[2]:

                if edit_mode:
                    supervisor_personnel = st.text_input("監造人員", value=project_data['supervisor_personnel'])
                else:
                    st.markdown(" 🔹 **監造人員**")
                    st.markdown(f"{project_data['supervisor_personnel']}")

            if edit_mode:
                if st.button("儲存", type="primary"):
                    updated_data = {
                        "year": int(year),
                        "project_number": project_data['project_number'],
                        "project_name": project_name,
                        "duration": int(duration),
                        "location": location,
                        "construction_content": construction_content,
                        "funding_source": funding_source,
                        "approved_amount": int(approved_amount),
                        "bid_bond": int(bid_bond),
                        "total_budget": int(total_budget),
                        "performance_bond": int(performance_bond),
                        "contract_amount": int(contract_amount),
                        "branch_office": branch_office,
                        "supervisor": supervisor,
                        "supervisor_personnel": project_data['supervisor_personnel'],
                        "outsourcing_items": project_data['outsourcing_items'],
                        "schedule_type": project_data['schedule_type'],
                        "outsourcing_company": project_data.get('outsourcing_company'),
                        "status": project_data['status']
                    }
                    
                    if update_project(project_data['id'], updated_data):
                        st.success("更新成功！")
                        time.sleep(2)
                    else:
                        st.error("更新失敗，請稍後再試。")
    else:
        st.info("目前沒有工程案件資料")
            # st.markdown("---")

with tab2: 
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
        
        if project_data.get('total_budget', 0) < 200000000:
            project_category = "未達二千萬之第三類工程"
        else:
            project_category = "二千萬元以上未達查核金額之第二類工程"

        from utils import get_contractor, get_cost_range,num_to_chinese

        if project_data.get('supervisor_personnel'):
            supervisor_text=project_data.get('supervisor') +"主辦監造及" + project_data.get('supervisor_personnel') + "監造人員"
        else:
            supervisor_text=project_data.get('supervisor') +"主辦監造"

        # 準備替換的資料
        replacements = {
            "工程名稱": project_data['project_name'],
            "經費來源": project_data['funding_source'],
            "民國年": str(project_data.get('year', '113')),
            "所屬分處": project_data.get('branch_office'),
            "委外廠商": project_data.get('outsourcing_company'),
            "工程編號": project_data.get('project_number', ''),#.replace("雲林","YL"),
            "採購標的": "工程",
            "核定經費": format_currency(project_data.get('approved_amount')).replace("NT$ ", "") + "元",
            "預算書總價": format_currency(project_data.get('total_budget')).replace("NT$ ", "") + "元",
            "發包工作費總額": format_currency(project_data.get('contract_amount')).replace("NT$ ", "") + "元",
            "工程分類": project_category,
            "押標金額度": num_to_chinese(int(project_data.get('bid_bond'))) ,
            "廠商基本資格": get_contractor(project_data.get('contract_amount')),
            "採購金額級距": get_cost_range(project_data.get('contract_amount')),
            "履約保證金": num_to_chinese(int(project_data.get('performance_bond'))) ,
            "監造人員": supervisor_text,
        }
        
        # st.json(project_data.to_dict())
        st.json(replacements)

        # 確保output目錄存在
        os.makedirs("output", exist_ok=True)
        
        # 產生文件
        read_tender_document(template_path, replacements, output_path)
        st.success(f"文件已產生：{output_path}")
        
        # 提供下載連結
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 下載文件",
                data=file,
                file_name=os.path.basename(output_path),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        # 關閉檔案後刪除
        if os.path.exists(output_path):
            os.remove(output_path)