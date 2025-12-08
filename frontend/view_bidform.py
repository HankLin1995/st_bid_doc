import streamlit as st
import requests
from datetime import datetime
from typing import List
import time
from api import get_project,get_projects,update_project,update_project_dates,update_project_date_and_status
import pandas as pd

# API 配置
API_URL = "http://backend:8000"

IsERROR=False

if 'construction_content' not in st.session_state:
    st.session_state.construction_content = ""

def draft_page():

    st.subheader(":star: 初稿送審")

    with st.container(border=True):
        
        #顯示工程清單
        projects=get_projects()

        df=pd.DataFrame(projects)

        df=df[(df["CurrentStatus"]=="核定") | (df["CurrentStatus"]=="提報")]

        df_distinct_workstation=["無"]+df["Workstation"].unique().tolist()

        st.caption("如果看不到自己的工作站或工程編號可以跳過不用填寫初稿送審!")

        workstation=st.selectbox("選擇工作站",df_distinct_workstation,index=0)

        if workstation=="無":
            return

        df=df[df["Workstation"]==workstation]

        #結合ProjectID與ProjectName
        df["ProjectID"] = df["ProjectID"].astype(str)
        df["ProjectName"] = df["ProjectName"].astype(str)
        df["ProjectID_ProjectName"] = df["ProjectID"] + " - " + df["ProjectName"]

        project_name=st.selectbox("選擇工程",df["ProjectID_ProjectName"].tolist()) 
        project_id=df[df["ProjectID_ProjectName"]==project_name]["ProjectID"].values[0]

        # st.badge(project_id, color="green")

    if st.button("送審",use_container_width=True,type="primary"):
        
        current_date=datetime.now().strftime("%Y-%m-%d")
        result=update_project_date_and_status(project_id,"初稿",current_date)
        if result=="更新成功":
            st.success("初稿送審成功",icon="✅")
            st.balloons()
        else:
            st.error(result)


def create_project(project_data: dict):
    response = requests.post(f"{API_URL}/projects/", json=project_data)
    if response.status_code == 200:
        return {"success": True, "data": response.json()}
    elif response.status_code == 400:
        # Handle the case where project already exists
        return {"success": False, "error": response.json().get("detail", "Project already exists")}
    else:
        # Handle other errors
        return {"success": False, "error": "An error occurred"}

def get_project_by_number(project_number: str):
    response = requests.get(f"{API_URL}/projects/{project_number}")
    return response.json() if response.status_code == 200 else None

def load_test_data():
    return {
        "project_name": "測試工程-排水改善工程",
        "project_number": f"TEST-{datetime.now().strftime('%Y%m%d%H%M')}",
        "location": "雲林縣斗六市",
        "duration": 90,
        "construction_content": "排水溝改善及路面修復",
        "funding_source": "固定資產建設改良擴充-土地改良物(國庫撥款)",
        "approved_amount": 1000000,
        "total_budget": 950000,
        "contract_amount": 900000,
        "branch_office": "虎尾分處",
        "supervisor": "王工程師",
        "supervisor_personnel": "李監造",
        "outsourcing_company": "OOO工程顧問公司",
        "outsourcing_items": ["瀝青混凝土鋪面", "控制性低強度回填材料(CLSM)"]
    }

@st.dialog("施工內容")
def get_construction():
    mylen=st.number_input("施工總長度",min_value=0.0)
    myline=st.number_input("施工線數",min_value=0)
    myother=st.text_input("其他內容",placeholder="其他內容")

    if st.button("確認"):

        if myother=="":
            st.session_state.construction_content="施工線數:"+str(myline)+"線、"+"施工總長度:"+str(mylen)+"M"
        else:
            st.session_state.construction_content="施工線數:"+str(myline)+"線、"+"施工總長度:"+str(mylen)+"M、"+myother
        st.rerun()

def budget_year_page():

    approved_amount_value = 0
    project_name_value = ""

    st.markdown("### 🔷 開口契約預算書審查")

    # 新增/編輯表單
    with st.container(border=True):

        st.markdown("#### 🎯任務分配")

        year = st.number_input("民國年",min_value=113,value=datetime.now().year-1911+1)

        branch_office_options = ["斗六分處","虎尾分處","西螺分處","北港分處","林內分處","本處"]
        branch_office = st.selectbox("分處名稱",options=branch_office_options)

    with st.container(border=True):
        st.markdown("#### 🍪基本資料")
        project_number = st.text_input("工程編號",placeholder="115512XXX")
        project_name = st.text_input("工程名稱",value=project_name_value)
        location = st.text_input("工程地點",placeholder="OO縣OO市")
        #施工總長度、線數、其他內容

        if not str(year) in project_name:
            st.warning("民國年與工程名稱不一致!",icon="⚠️") 

    with st.container(border=True):
        st.markdown("#### 👜經費相關")

        FUNDING_SOURCE_OPTIONS = [
            "業務費用-土地改良物修護費及行政規費與強制費",
            "固定資產建設改良擴充-土地改良物(國庫撥款)",
            "土地改良物(營運資金)"]

        funding_source = st.selectbox("經費來源",options=FUNDING_SOURCE_OPTIONS)
        total_budget = st.number_input("總工程費", min_value=0)
        if total_budget==0:
            st.warning("總工程費未調整，請重新輸入!",icon="⚠️")
        contract_amount = st.number_input("發包工作費", min_value=0)
        if contract_amount==0:
            st.warning("發包工作費未調整，請重新輸入!",icon="⚠️")
        outsourcing_items=st.pills("選擇PCCES有編列項目",["瀝青混凝土鋪面", "控制性低強度回填材料(CLSM)", "級配粒料基層", "低密度再生透水混凝土"],selection_mode="multi")
        #schedule_type=st.radio("開工型式",options=["一般流程","指定開工日","逕流廢汙水"])

    # 送出和清除按鈕
    # col_submit1, col_submit2 = st.columns([3, 1])
    # with col_submit1:
    if st.button("送出表單", type="primary",use_container_width=True):
        try:
            # 步驟2: PDF上傳成功後，才創建工程資料
            project_data = {
                "branch_office": branch_office,
                "project_name": project_name,
                "project_number": project_number,
                "funding_source": funding_source,
                "approved_amount": 0,  # 開口契約預設為0
                "total_budget": total_budget,
                "contract_amount": contract_amount,
                "duration": 0,  # 開口契約預設為0
                "construction_content": "依事件陳報內容辦理",
                "location": location,
                "supervisor": "無",  # 開口契約預設為"無"
                "supervisor_personnel": "無",  # 開口契約預設為"無"
                "outsourcing_items": ",".join(outsourcing_items),
                "procurement_type": "工程",  # 預設為工程
                "year": year,  # 預設為當前年度
                "schedule_type": "一般流程",
                "outsourcing_company": None  # 開口契約不使用委外公司
            }
            
            result = create_project(project_data)

            if result["success"]:
                st.success("✅ 工程資料創建成功！")
                
                st.balloons()
                time.sleep(2)
                st.rerun()
            else:
                # Display the specific error message from the backend
                if "already exists" in result["error"].lower():
                    st.warning(f"工程已存在，請勿重複創建! {result['error']}", icon="⚠️")
                else:
                    st.error(f"創建失敗: {result['error']}")
                    
                # Double check if the project exists by project number
                project = get_project_by_number(project_number)
                if project and not "already exists" in result["error"].lower():
                    st.warning("工程已存在，請勿重複創建!", icon="⚠️")

        except Exception as e:
            st.error(f"操作失敗：{str(e)}")




def budget_page():
    global IsERROR
    
    # if st.session_state.test_mode==True:

    #     if st.sidebar.button("載入測試數據"):
    #         st.session_state.test_data = load_test_data()
    #         st.rerun()

    approved_amount_value = 0
    project_name_value = ""

    st.markdown("### 🔷預算書審查")

    # 新增/編輯表單
    with st.container(border=True):

        st.markdown("#### 🎯任務分配")

        # 是否委外
        outsourcing_company = None
        is_outsourced = st.checkbox("委外設計監造", 
            value=True if 'test_data' in st.session_state else False)
        
        if is_outsourced:
            outsourcing_company = st.text_input("公司名稱",placeholder="OOO工程顧問公司")

        year = st.number_input("民國年",min_value=113,value=datetime.now().year-1911)

        branch_office_options = ["斗六分處","虎尾分處","西螺分處","北港分處","林內分處","本處"]
        branch_office = st.selectbox("分處名稱",options=branch_office_options)
        supervisor = st.text_input("主辦監造",placeholder="(必填)姓名")
        supervisor_personnel = st.text_input("監造人員",placeholder="(選填)姓名")

    with st.container(border=True):
        st.markdown("#### 🍪基本資料")
        project_number = st.text_input("工程編號",placeholder="雲林114TXX")

        try:

            if project_number:
                project = get_project(project_number)
                approved_amount_value = project["ApprovalBudget"]
                project_name_value = project["ProjectName"]

                if "ProjectName" in project:
                    project_id = project["ProjectID"]
                    st.success(f"工程載入成功！")
                    IsERROR = False
                else:
                    st.error("無法載入工程，請通知審查人員!")
                    IsERROR = True
            else:
                IsERROR = False
        except Exception as e:
            IsERROR = True
            st.error(f"請自行輸入核定金額：{str(e)}")

        project_name = st.text_input("工程名稱",value=project_name_value)

        if "開口契約" in project_name:
            st.warning("請移動至開口契約審查進行!",icon="⚠️")
            st.stop()

        location = st.text_input("工程地點",placeholder="OO縣OO市")
        duration = st.number_input("工期(天數)", min_value=0)
        #施工總長度、線數、其他內容

        construction_content = st.session_state.construction_content

        if st.button("填寫施工內容"):
            construction_content = get_construction()

        if construction_content=="":
            st.warning("請填寫施工內容!")
        else:
            st.write("施工內容:",construction_content)

    with st.container(border=True):
        st.markdown("#### 👜經費相關")

        FUNDING_SOURCE_OPTIONS = [
            "固定資產建設改良擴充-土地改良物(國庫撥款)",
            "業務費用-土地改良物修護費",
            "土地改良物(營運資金)",
            "其他機關"]

        funding_source = st.selectbox("經費來源",options=FUNDING_SOURCE_OPTIONS)
        approved_amount=st.number_input("核定金額",value=approved_amount_value,disabled=not IsERROR)
        total_budget = st.number_input("總工程費", min_value=0)
        if total_budget==0:
            st.warning("總工程費未調整，請重新輸入!",icon="⚠️")
        contract_amount = st.number_input("發包工作費", min_value=0)
        if contract_amount==0:
            st.warning("發包工作費未調整，請重新輸入!",icon="⚠️")
        outsourcing_items=st.pills("選擇PCCES有編列項目",["瀝青混凝土鋪面", "控制性低強度回填材料(CLSM)", "級配粒料基層", "低密度再生透水混凝土"],selection_mode="multi")
        schedule_type=st.radio("開工型式",options=["一般流程","指定開工日","逕流廢汙水"])

    with st.container(border=True):
        st.markdown("#### 📄PDF文件上傳")
        st.caption("2026/1/1起，請上傳生態檢核用印PDF和碳排計算PDF")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # st.markdown("**生態檢核用印PDF**")
            ecological_pdf = st.file_uploader(
                "上傳生態檢核PDF",
                type=['pdf'],
                key="ecological_pdf"
            )
            if ecological_pdf:
                st.success(f"✅ 已選擇: {ecological_pdf.name}")
        
        with col2:
            # st.markdown("**碳排計算PDF**")
            carbon_pdf = st.file_uploader(
                "上傳碳排計算PDF",
                type=['pdf'],
                key="carbon_pdf"
            )
            if carbon_pdf:
                st.success(f"✅ 已選擇: {carbon_pdf.name}")

    # 送出和清除按鈕
    # col_submit1, col_submit2 = st.columns([3, 1])
    # with col_submit1:
    if st.button("送出表單", type="primary",use_container_width=True):
        try:
            # 驗證PDF檔案是否都已上傳
            # if not ecological_pdf:
            #     st.error("❌ 請上傳生態檢核用印PDF")
                # st.stop()
            
            # if not carbon_pdf:
            #     st.error("❌ 請上傳碳排計算PDF")
                # st.stop()
            
            # 步驟1: 先上傳PDF檔案
            pdf_upload_success = True
            with st.spinner("正在上傳PDF檔案..."):
                # 上傳生態檢核PDF
                if ecological_pdf:
                    try:
                        files = {"file": (ecological_pdf.name, ecological_pdf, "application/pdf")}
                        response = requests.post(
                            f"{API_URL}/upload-pdf/{year}/{project_name}/ecological",
                            files=files
                        )
                        if response.status_code == 200:
                            st.success("✅ 生態檢核PDF上傳成功")
                        else:
                            st.error(f"❌ 生態檢核PDF上傳失敗: {response.json().get('detail', '未知錯誤')}")
                            pdf_upload_success = False
                    except Exception as e:
                        st.error(f"❌ 生態檢核PDF上傳失敗: {str(e)}")
                        pdf_upload_success = False
                
                # 上傳碳排計算PDF
                if carbon_pdf and pdf_upload_success:
                    try:
                        files = {"file": (carbon_pdf.name, carbon_pdf, "application/pdf")}
                        # 碳排計算需要傳遞工程編號
                        params = {"project_number": project_number}
                        response = requests.post(
                            f"{API_URL}/upload-pdf/{year}/{project_name}/carbon",
                            files=files,
                            params=params
                        )
                        if response.status_code == 200:
                            st.success("✅ 碳排計算PDF上傳成功")
                        else:
                            st.error(f"❌ 碳排計算PDF上傳失敗: {response.json().get('detail', '未知錯誤')}")
                            pdf_upload_success = False
                    except Exception as e:
                        st.error(f"❌ 碳排計算PDF上傳失敗: {str(e)}")
                        pdf_upload_success = False
            
            # 如果PDF上傳失敗，停止後續流程
            if not pdf_upload_success:
                st.error("⚠️ PDF檔案上傳失敗，工程資料未建立，請重新上傳")
                st.stop()
            
            # 步驟2: PDF上傳成功後，才創建工程資料
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
                "schedule_type": schedule_type,
                "outsourcing_company": outsourcing_company
            }
            
            # st.write(project_data)
            result = create_project(project_data)

            if result["success"]:
                st.success("✅ 工程資料創建成功！")
                
                # 步驟3: 更新專案狀態
                if not IsERROR:
                    update_result = update_project_date_and_status(project_number, "預算書", datetime.now().strftime("%Y-%m-%d"))
                    if update_result == "更新成功":
                        st.success("✅ 狀態更新成功!")
                    else:
                        st.error("❌ 狀態更新失敗!")
                
                st.balloons()
                time.sleep(2)
                if 'test_data' in st.session_state:
                    del st.session_state.test_data
                st.rerun()
            else:
                # Display the specific error message from the backend
                if "already exists" in result["error"].lower():
                    st.warning(f"工程已存在，請勿重複創建! {result['error']}", icon="⚠️")
                else:
                    st.error(f"創建失敗: {result['error']}")
                    
                # Double check if the project exists by project number
                project = get_project_by_number(project_number)
                if project and not "already exists" in result["error"].lower():
                    st.warning("工程已存在，請勿重複創建!", icon="⚠️")

        except Exception as e:
            st.error(f"操作失敗：{str(e)}")


##### MAIN UI #####

# mypage=st.selectbox("選擇功能",["初稿送審","預算書審查"])
mypage=st.radio("選擇功能",["初稿送審","預算書審查","開口契約審查"],horizontal=True)

if mypage=="預算書審查":
    budget_page()

if mypage=="初稿送審":
    draft_page()

if mypage=="開口契約審查":
    budget_year_page()
    