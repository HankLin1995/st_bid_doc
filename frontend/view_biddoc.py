import streamlit as st
import os
from docx_utils import replace_text_within_percent_signs
import requests
# import cn2an
# import opencc
import io
import zipfile
import shutil
from datetime import datetime
import pandas as pd
import time
from dotenv import load_dotenv
from utils import get_contractor, get_cost_range,num_to_chinese

load_dotenv()

# API 配置
API_URL = "http://backend:8000"

def get_projects():
    response = requests.get(f"{API_URL}/projects/")
    return response.json() if response.status_code == 200 else []

def get_project_by_id(project_id):
    response = requests.get(f"{API_URL}/projects/{project_id}")
    return response.json() if response.status_code == 200 else None

# @st.dialog("選擇工程")
def select_project():

    projects = get_projects()

    project_df=pd.DataFrame(projects)
    
    if len(projects) == 0:
        st.error("目前沒有任何專案")
        return

    # 將專案資料轉換為更好的顯示格式
    # display_projects = []
    # for p in projects:
    #     display_projects.append({
    #         "ID": p["id"],
    #         "工程名稱": p["project_name"],
    #         "工程編號": p["project_number"],
    #         "分處": p["branch_office"],
    #         "核定金額": f"{p['approved_amount']:,.0f}",
    #         "工期": p["duration"],
    #         "建立時間": datetime.fromisoformat(p['created_at']).strftime('%Y-%m-%d')
    #     })
    
    # 創建可選擇的資料表
    # project_df = pd.DataFrame(display_projects)
    project_name=st.sidebar.selectbox("請選擇要載入的工程", project_df["project_name"])    
    project_id = projects[project_df[project_df["project_name"] == project_name].index[0]]["id"]

    if st.sidebar.button(":star:載入工程", key="load_project"):
        st.session_state.project_data = get_project_by_id(project_id)
        st.sidebar.success("工程載入成功！")
        time.sleep(1)
        st.rerun()

# def num_to_chinese(amount):

#     if amount==0: return "免收"

#     cc = opencc.OpenCC('s2t')  # 's2t' 表示简体转繁体
#     simplified_text=cn2an.an2cn(str(amount),"up")
#     simplified_text= simplified_text.replace("叁","參")
#     return cc.convert(simplified_text)+'元整'

def convert_data(data):
    for key in data:
        if isinstance(data[key], bool):
            data[key] = deal_bool(data[key])  # 使用 deal_bool 函數進行轉換
        elif data[key] is None:
            data[key] = ''  # 將 None 轉換為空字符串
    return data

# deal true or false black square or blank square
def deal_bool(data):
    if data:
        return '■'  # 黑色方格
    else:
        return '□'  # 白色方格
    
# def get_contractor(contract_money: float) -> str:
#     m = contract_money

#     if m < 6000000:
#         f = "設立於雲林縣或毗鄰縣市之土木包工業，或丙等以上綜合營造業"
#     elif 6000000 <= m < 7200000:
#         f = "設立於雲林縣或毗鄰縣市並依營造業法規定辦理資本額增資之土木包工業，或丙等以上綜合營造業"
#     elif m <= 22500000:
#         f = "丙等(含)綜合營造業以上"
#     elif 22500000 < m <= 27000000:
#         f = "依營造業法規定辦理資本額增資之丙等綜合營造業，或乙等以上綜合營造業"
#     elif m <= 75000000:
#         f = "乙等(含)綜合營造業以上"
#     elif 75000000 < m <= 90000000:
#         f = "依營造業法規定辦理資本額增資之乙等綜合營造業，或甲等以上綜合營造業"
#     else:
#         f = "甲等(含)綜合營造業以上"

#     result = f

#     # Check specific contract money cases and add a special prefix
#     if m in [6000000, 7200000, 22500000, 27000000, 75000000, 90000000]:
#         result = "!!!!!!!!!!" + f

#     return result

# def get_cost_range(contract_money: float) -> str:

#     if contract_money < 150000:
#         return "公告金額十分之一之採購"
#     elif contract_money < 1500000:
#         return "未達公告金額而逾公告金額十分之一之採購"
#     elif contract_money < 50000000:
#         return "公告金額以上未達查核金額之採購"
#     else:
#         return "查核金額以上未達巨額之採購"

def get_work_type(work_type, work_days):
    general_box = False
    specified_box = False
    runoff_box = False
    general_date= None
    specified_date= None
    runoff_date= None

    if work_type == "一般流程":
        general_box = True
        general_date = work_days
    elif work_type == "指定開工日":
        specified_box = True
        specified_date = work_days
        # start_date = st.date_input("指定開工日")
    elif work_type == "逕流廢汙水":
        runoff_box = True
        runoff_date = work_days

    return general_box, specified_box, runoff_box, general_date, specified_date, runoff_date

def get_cost_type(cost_type: str):

    purchase_a = False
    purchase_b = False
    purchase_c = False

    if cost_type == "未達公告金額而逾公告金額十分之一之採購":
        purchase_a = True
    elif cost_type == "公告金額以上未達查核金額之採購":
        purchase_b = True
    elif cost_type == "查核金額以上未達巨額之採購":
        purchase_c = True
    else:
        st.toast("小額採購或巨額採購請另外處理!!!",icon="🚫")
    
    return purchase_a, purchase_b, purchase_c

def get_employ_type(qualification: str):
    # Initially set all checkboxes to False
    contractor_a = False
    contractor_a1 = False
    contractor_a2 =False
    contractor_a3 = False
    contractor_b = False

    # Classifying based on qualification type and selecting appropriate checkboxes
    if qualification == "設立於雲林縣或毗鄰縣市之土木包工業，或丙等以上綜合營造業":
        contractor_a = True
        contractor_a3 = True  # 丙等 or higher, so select "廠商A丙-BOX"
        contractor_b = True  # 土包 as well
        
    elif qualification == "設立於雲林縣或毗鄰縣市並依營造業法規定辦理資本額增資之土木包工業，或丙等以上綜合營造業":
        contractor_a = True
        contractor_a3 = True  # 丙等 or higher
        contractor_b = True  # 土包
        
    elif qualification == "丙等以上綜合營造業":
        contractor_a = True
        contractor_a3 = True  # 丙等 or higher
    
    elif qualification == "依營造業法規定辦理資本額增資之丙等綜合營造業，或乙等以上綜合營造業":
        contractor_a = True
        contractor_a2 = True
        contractor_a3 = True  # 乙等 or higher
        
    elif qualification == "乙等以上綜合營造業":
        contractor_a = True
        contractor_a2 = True  # 乙等 or higher

    elif qualification == "依營造業法規定辦理資本額增資之乙等綜合營造業，或甲等以上綜合營造業":
        contractor_a = True
        contractor_a1 = True
        contractor_a2 = True
    
    elif qualification == "甲等綜合營造業":
        contractor_a = True
        contractor_a1 = True

    else:
        st.toast("小額採購或巨額採購請另外處理!!!",icon="🚫")

    return contractor_a, contractor_a1, contractor_a2, contractor_a3, contractor_b


### 主要介面

# msg_content()

my_pass=st.sidebar.text_input("請輸入密碼",type="password",key="view_biddoc_password")

if my_pass!=os.getenv("PASSWORD"):
    st.stop()

select_project()

# 基本資訊部分

st.markdown("### 🔷投標文件")

with st.container(border=True):
    st.markdown("#### 🍪基本資料")
    
    mode=st.radio("選擇模式",["一般工程","開口契約"])

    # 如果有選擇現有工程，使用其資料
    if 'project_data' in st.session_state:
        project_data = st.session_state.project_data
        year = st.text_input("民國年", value=str(project_data.get('year', '114')))
        project_name = st.text_input("標案名稱", value=project_data['project_name'])
        project_number = st.text_input("標案編號", value=project_data['project_number'].replace("雲林", "YL"))
        location = st.text_input("工程地點", value=project_data['location'])
    else:
        year = st.text_input("年度", value="114")
        project_name = st.text_input("標案名稱", value="OOOO改善工程")
        project_number = st.text_input("標案編號",placeholder="YL114OOO")

        if '雲林' in project_number:
            st.error("請將標案編號中的「雲林」改為「YL」")

        location = st.text_input("工程地點")

with st.container(border=True):
    st.markdown("#### 💰經費相關")
    
    bid_award = st.checkbox("保留決標")

    if 'project_data' in st.session_state:
        funding_source = st.text_input("經費來源", value=project_data['funding_source'])
        budget = st.text_input("預算金額", value=str(project_data['contract_amount']))
    else:
        funding_source = st.text_input("經費來源", value="固定資產建設改良擴充-土地改良物(國庫撥款)")
        budget = st.text_input("預算金額", value="0")

    try:
        budget_value = float(budget)
        formatted_budget = "{:,.0f}".format(budget_value)  # Format as a string with commas
    except ValueError:
        formatted_budget = "0"  # If the input is not a valid number, display 0

    bid_bond=st.number_input("押標金金額",value=0)
    bid_bond_chinese=num_to_chinese(bid_bond)
    # st.write(f"押標金金額為:{bid_bond_chinese}")

    performance_bond=st.number_input("履約保證金",value=0)
    performance_bond_chinese=num_to_chinese(performance_bond)
    # st.write(f"履約保證金為:{performance_bond_chinese}")

    if mode=="開口契約":
        purchase_limit=st.text_input("採購金額上限",value="0")
        purchase_level = get_cost_range(float(purchase_limit))
    else:
        purchase_level = get_cost_range(float(budget))

    purchase_level = st.selectbox("採購級距",options=["公告金額十分之一之採購","未達公告金額而逾公告金額十分之一之採購","公告金額以上未達查核金額之採購","查核金額以上未達巨額之採購"],index=["公告金額十分之一之採購","未達公告金額而逾公告金額十分之一之採購","公告金額以上未達查核金額之採購","查核金額以上未達巨額之採購"].index(purchase_level))

with st.container(border=True):

    st.markdown("#### 🍰資格及進度")
    contractor_qual=get_contractor(float(budget))
    contractor_qual=st.selectbox("廠商資格",options=["設立於雲林縣或毗鄰縣市之土木包工業，或丙等以上綜合營造業","設立於雲林縣或毗鄰縣市並依營造業法規定辦理資本額增資之土木包工業，或丙等以上綜合營造業","丙等以上綜合營造業","依營造業法規定辦理資本額增資之丙等綜合營造業，或乙等以上綜合營造業","乙等以上綜合營造業","依營造業法規定辦理資本額增資之乙等綜合營造業，或甲等以上綜合營造業","甲等綜合營造業"],index=["設立於雲林縣或毗鄰縣市之土木包工業，或丙等以上綜合營造業","設立於雲林縣或毗鄰縣市並依營造業法規定辦理資本額增資之土木包工業，或丙等以上綜合營造業","丙等以上綜合營造業","依營造業法規定辦理資本額增資之丙等綜合營造業，或乙等以上綜合營造業","乙等以上綜合營造業","依營造業法規定辦理資本額增資之乙等綜合營造業，或甲等以上綜合營造業","甲等綜合營造業"].index(contractor_qual))

    if mode=="開口契約":
        work_days=0
    else:
        if 'project_data' in st.session_state:
            work_days=st.text_input("工期", value=str(project_data['duration']))
        else:
            work_days=st.number_input("工期", min_value=1, value=1)

    if 'project_data' in st.session_state:
        mode2=st.radio("開工型式",["一般流程","指定開工日","逕流廢汙水"],index=["一般流程","指定開工日","逕流廢汙水"].index(project_data['schedule_type']))
    else:
        mode2=st.radio("開工型式",["一般流程","指定開工日","逕流廢汙水"])

    start_date=None
    general_days=None

    if mode2=="指定開工日":
        start_date=st.date_input("指定開工日").strftime("%Y-%m-%d")
    elif mode2=="一般流程":
        general_days="14"

general_box, specified_box, runoff_box, general_date, specified_date, runoff_date = get_work_type(mode2,work_days)
contractor_a, contractor_a1, contractor_a2, contractor_a3, contractor_b = get_employ_type(contractor_qual)
purchase_a, purchase_b, purchase_c = get_cost_type(purchase_level)

data = {
    '標案名稱': project_name,
    '標案案號': project_number,
    '年度': year,
    '經費來源': funding_source,
    '押標金金額': bid_bond,
    '押標金金額中文': bid_bond_chinese,
    '廠商資格': contractor_qual,
    '工程地點': location,
    '預算金額': formatted_budget,
    '採購金額上限': purchase_limit if mode =="開口契約" else None,
    '採購級距': purchase_level,
    '履約保證金': performance_bond,
    '履約保證金中文': performance_bond_chinese,
    '工期': work_days,
    '指定開工日': start_date if start_date else None,
    '一般BOX': general_box,
    '指定BOX': specified_box,
    '逕流BOX': runoff_box,
    '一般工期': general_date,
    '一般日期範圍':general_days,
    '指定工期': specified_date,
    '逕流工期': runoff_date,
    '採購A-BOX': purchase_a,
    '採購B-BOX': purchase_b,
    '採購C-BOX': purchase_c,
    '廠商A-BOX': contractor_a,
    '廠商A甲-BOX': contractor_a1,
    '廠商A乙-BOX': contractor_a2,
    '廠商A丙-BOX': contractor_a3,
    '廠商B土包-BOX': contractor_b,
    '保留-BOX': bid_award
    
}

data = convert_data(data)

def create_output_folder(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        os.makedirs(os.path.join(output_dir, "投標文件"))
    else:
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)
        os.makedirs(os.path.join(output_dir, "投標文件"))

# 處理文件

if mode=="一般工程":
    doc_folder=os.path.join("src", "廠商投標表單")
else:
    doc_folder=os.path.join("src", "廠商投標表單(開口)")

output_dir=os.path.join(".", data['標案名稱'])

submitted = st.button("產製招標文件",type="primary")

if submitted:

    # call API to store bid_bond and performance_bond

    if 'project_data' in st.session_state:

        response = requests.put(f"{API_URL}/projects/{project_data['id']}/bonds", json={
            "id": project_data['id'],
            "bid_bond": bid_bond,
            "performance_bond": performance_bond
        })

        if response.status_code != 200:
            st.error("無法儲存押標金及履約保證金")

    if not os.path.exists("src"):
        os.makedirs("src")
    if not os.path.exists(doc_folder):
        os.makedirs(doc_folder)
    
    # Create output directory
    create_output_folder(output_dir)
    
    # Process files
    progress_bar = st.progress(0)
    status_text = st.empty()
        
    files_processed = 0
    total_files = sum(1 for _, _, files in os.walk(doc_folder) 
                     for file in files if file.endswith(".docx"))

    for root, dirs, files in os.walk(doc_folder):

        for file in files:

            file_path = os.path.join(root, file) # 取得文件的完整路徑
            relative_path = os.path.relpath(file_path, doc_folder) # 取得相對路徑
            output_file_path=os.path.join(output_dir,relative_path) # 取得輸出文件的完整路徑
            output_folder = os.path.dirname(output_file_path)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            shutil.copy(file_path,output_file_path) # 將文件複製到輸出目錄

            if file.endswith(".docx"):

                status=replace_text_within_percent_signs(output_file_path, data)

                if status:
                    st.error(status)
                else:
                    files_processed += 1
                    progress_bar.progress(files_processed / total_files)
                    status_text.text(f"正在處理文件: {file}")
                    
        # Clear progress indicators
        status_text.empty()
        progress_bar.empty()
            
    if files_processed > 0:
        st.success(f"完成處理 {files_processed} 個文件！")
        # st.info(f"處理後的文件已保存在: {output_dir}")
            
        # Create ZIP file for download
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)

                    zf.write(file_path,os.path.relpath(file_path, output_dir))
        
        memory_file.seek(0)

        shutil.rmtree(output_dir)
            
        # Add download button
        st.download_button(
            key="download_processed_files",
            label="下載處理後的文件 (ZIP)",
            data=memory_file,
            file_name=f"{data['標案名稱']}.zip",
            mime="application/zip"
        )
    else:
        st.warning("沒有文件被成功處理！")