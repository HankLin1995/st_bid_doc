import streamlit as st
import requests
from datetime import datetime
from typing import List

# API 配置
API_URL = "http://backend:8000"

def create_project(project_data: dict):
    response = requests.post(f"{API_URL}/projects/", json=project_data)
    return response.json() if response.status_code == 200 else None

def get_projects() -> List[dict]:
    response = requests.get(f"{API_URL}/projects/")
    return response.json() if response.status_code == 200 else []

def load_test_data():
    return {
        "project_name": "測試工程-排水改善工程",
        "project_number": f"TEST-{datetime.now().strftime('%Y%m%d%H%M')}",
        "location": "雲林縣斗六市",
        "duration": 90,
        "construction_content": "排水溝改善及路面修復",
        "funding_source": "固定資產建設改良擴充-土地改良物(國庫撥款)",
        "approved_amount": 1000000.0,
        "total_budget": 950000.0,
        "contract_amount": 900000.0,
        "branch_office": "斗六分處",
        "supervisor": "王工程師",
        "supervisor_personnel": "李監造",
        "outsourcing_company": "OOO工程顧問公司",
        "outsourcing_items": ["瀝青混凝土鋪面", "控制性低強度回填材料(CLSM)"]
    }

if st.session_state.test_mode==True:

    if st.sidebar.button("載入測試數據"):
        st.session_state.test_data = load_test_data()
        st.rerun()

st.markdown("### 🔷預算書審查")

# 新增/編輯表單
with st.container(border=True):
    st.markdown("#### 🎯任務分配")

    # 是否委外
    outsourcing_company = None
    is_outsourced = st.checkbox("委外設計監造", 
        value=True if 'test_data' in st.session_state else False)
    
    if is_outsourced:
        outsourcing_company = st.text_input("公司名稱", 
            value=st.session_state.test_data.get("outsourcing_company", "") if 'test_data' in st.session_state else "",
            placeholder="OOO工程顧問公司")

    year = st.number_input("民國年",min_value=datetime.now().year-1911)

    branch_office = st.selectbox("分處名稱",
        options=["斗六分處","虎尾分處","西螺分處","北港分處","林內分處","本處"],
        index=0 if 'test_data' not in st.session_state else 
            ["斗六分處","虎尾分處","西螺分處","北港分處","林內分處","本處"].index(st.session_state.test_data["branch_office"]))
    
    supervisor = st.text_input("主辦監造", 
        value=st.session_state.test_data.get("supervisor", "") if 'test_data' in st.session_state else "")
    supervisor_personnel = st.text_input("監造人員", 
        value=st.session_state.test_data.get("supervisor_personnel", "") if 'test_data' in st.session_state else "")

# col1, col2 = st.columns(2)

# with col1:
with st.container(border=True):
    st.markdown("#### 🍪基本資料")
    project_name = st.text_input("工程名稱", 
        value=st.session_state.test_data.get("project_name", "") if 'test_data' in st.session_state else "")
    project_number = st.text_input("工程編號", 
        value=st.session_state.test_data.get("project_number", "") if 'test_data' in st.session_state else "")
    location = st.text_input("工程地點", 
        value=st.session_state.test_data.get("location", "") if 'test_data' in st.session_state else "")
    duration = st.number_input("工期", min_value=1, 
        value=st.session_state.test_data.get("duration", 1) if 'test_data' in st.session_state else 1)
    construction_content = st.text_input("施工內容", 
        value=st.session_state.test_data.get("construction_content", "") if 'test_data' in st.session_state else "")
# with col2:
with st.container(border=True):
    st.markdown("#### 👜經費相關")
    funding_source = st.text_input("經費來源",
        value=st.session_state.test_data.get("funding_source", "固定資產建設改良擴充-土地改良物(國庫撥款)") if 'test_data' in st.session_state else "固定資產建設改良擴充-土地改良物(國庫撥款)")
    approved_amount = st.number_input("核定金額", min_value=0.0,
        value=st.session_state.test_data.get("approved_amount", 0.0) if 'test_data' in st.session_state else 0.0)
    total_budget = st.number_input("總工程費", min_value=0.0,
        value=st.session_state.test_data.get("total_budget", 0.0) if 'test_data' in st.session_state else 0.0)
    contract_amount = st.number_input("發包工作費", min_value=0.0,
        value=st.session_state.test_data.get("contract_amount", 0.0) if 'test_data' in st.session_state else 0.0)
    default_items = st.session_state.test_data.get("outsourcing_items", []) if 'test_data' in st.session_state else []
    outsourcing_items = st.multiselect(
        "應註記之契約項目",
        ["瀝青混凝土鋪面", "控制性低強度回填材料(CLSM)", "級配粒料基層", "低密度再生透水混凝土"],
        default=default_items
    )
    schedule_type=st.radio("開工型式",options=["一般流程","指定開工日","逕流廢汙水"])
    # st.write(schedule_type)

# 送出和清除按鈕
col_submit1, col_submit2 = st.columns([3, 1])
with col_submit1:
    if st.button("送出表單", type="primary"):
        try:
            project_data = {
                "branch_office": branch_office,
                "project_name": project_name,
                "project_number": project_number,
                "funding_source": funding_source,
                "approved_amount": approved_amount,
                "total_budget": total_budget,
                "contract_amount": contract_amount,
                "duration": duration,
                "construction_content": construction_content,
                "location": location,
                "supervisor": supervisor,
                "supervisor_personnel": supervisor_personnel,
                "outsourcing_items": ",".join(outsourcing_items),
                "procurement_type": "工程",  # 預設為工程
                "year": year,  # 預設為當前年度
                "schedule_type": schedule_type
            }
            
            result = create_project(project_data)
            if result:
                st.success("工程創建成功！")
                if 'test_data' in st.session_state:
                    del st.session_state.test_data
                st.rerun()
            else:
                st.error("創建失敗，請檢查資料是否正確")
                
        except Exception as e:
            st.error(f"操作失敗：{str(e)}")

# # 顯示現有工程列表
# if st.button("刷新"):
#     with st.expander("查看所有工程"):
#         projects = get_projects()
#         for project in projects:
#             with st.container(border=True):
#                 col1, col2 = st.columns([2,1])
#                 with col1:
#                     st.write(f"**工程名稱：** {project['project_name']}")
#                     st.write(f"**工程編號：** {project['project_number']}")
#                     st.write(f"**分處：** {project['branch_office']}")
#                 with col2:
#                     st.write(f"**狀態：** {project['status']}")
#                     st.write(f"**建立時間：** {datetime.fromisoformat(project['created_at']).strftime('%Y-%m-%d %H:%M')}")
