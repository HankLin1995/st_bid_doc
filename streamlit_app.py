import streamlit as st
import os
from main import replace_text_within_percent_signs
from data_storage import convert_data, deal_bool

import cn2an
import opencc
import io
import zipfile
import shutil

st.set_page_config(page_title="工程招標文件處理工具")

st.sidebar.title("工程招標文件處理工具V1.1")
st.sidebar.info("作者: HankLin")

def num_to_chinese(amount):

    if amount=="": return ""

    cc = opencc.OpenCC('s2t')  # 's2t' 表示简体转繁体
    simplified_text=cn2an.an2cn(str(amount),"up")
    simplified_text= simplified_text.replace("叁","參")
    return cc.convert(simplified_text)+'元整'

def get_contractor(contract_money: float) -> str:
    m = contract_money

    if m < 6000000:
        f = "設立於雲林縣或毗鄰縣市之土木包工業，或丙等以上綜合營造業"
    elif 6000000 <= m < 7200000:
        f = "設立於雲林縣或毗鄰縣市並依營造業法規定辦理資本額增資之土木包工業，或丙等以上綜合營造業"
    elif m <= 22500000:
        f = "丙等(含)綜合營造業以上"
    elif 22500000 < m <= 27000000:
        f = "依營造業法規定辦理資本額增資之丙等綜合營造業，或乙等以上綜合營造業"
    elif m <= 75000000:
        f = "乙等(含)綜合營造業以上"
    elif 75000000 < m <= 90000000:
        f = "依營造業法規定辦理資本額增資之乙等綜合營造業，或甲等以上綜合營造業"
    else:
        f = "甲等(含)綜合營造業以上"

    result = f

    # Check specific contract money cases and add a special prefix
    if m in [6000000, 7200000, 22500000, 27000000, 75000000, 90000000]:
        result = "!!!!!!!!!!" + f

    return result

def get_cost_range(contract_money: float) -> str:

    if contract_money < 150000:
        return "公告金額十分之一之採購"
    elif contract_money < 1500000:
        return "未達公告金額而逾公告金額十分之一之採購"
    elif contract_money < 50000000:
        return "公告金額以上未達查核金額之採購"
    else:
        return "查核金額以上未達巨額之採購"

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
        st.error("小額採購或巨額採購請另外處理!!")
    
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
        
    elif qualification == "丙等(含)綜合營造業以上":
        contractor_a = True
        contractor_a3 = True  # 丙等 or higher
    
    elif qualification == "依營造業法規定辦理資本額增資之丙等綜合營造業，或乙等以上綜合營造業":
        contractor_a = True
        contractor_a2 = True
        contractor_a3 = True  # 乙等 or higher
        
    elif qualification == "乙等(含)綜合營造業以上":
        contractor_a = True
        contractor_a2 = True  # 乙等 or higher

    elif qualification == "依營造業法規定辦理資本額增資之乙等綜合營造業，或甲等以上綜合營造業":
        contractor_a = True
        contractor_a1 = True
        contractor_a2 = True
    
    elif qualification == "甲等(含)綜合營造業以上":
        contractor_a = True
        contractor_a1 = True

    else:
        st.error("小額採購或巨額採購請另外處理!!")

    return contractor_a, contractor_a1, contractor_a2, contractor_a3, contractor_b



### 主要介面

mode=st.radio("選擇模式",["一般工程","開口契約"])

# st.write(mode)

st.markdown("---")

# 基本資訊部分

st.subheader("基本資訊")

year=st.text_input("年度")
project_name=st.text_input("標案名稱",placeholder="例：114年度舊庄農地重劃區小排20等緊急農水路改善工程")
project_number=st.text_input("標案案號",placeholder="例：雲林113J206")
location=st.text_input("工程地點",placeholder="例：雲林縣大埤鄉")

st.markdown("---")
st.subheader("經費相關")

funding_source=st.text_input("經費來源",value="固定資產建設改良擴充-土地改良物(國庫撥款)")
budget=st.text_input("預算金額",value="0")

bid_bond=st.number_input("押標金金額",value=0)
bid_bond_chinese=num_to_chinese(bid_bond)# st.text_input("押標金金額中文") #自動轉換
if bid_bond_chinese!="":
    st.toast(f"押標金金額:{bid_bond_chinese}")

performance_bond=st.number_input("履約保證金",value=0)
performance_bond_chinese=num_to_chinese(performance_bond)# st.text_input("履約保證金中文") #自動轉換
if performance_bond_chinese!="":
    st.toast(f"履約保證金:{performance_bond_chinese}")

if mode=="開口契約":
    purchase_limit=st.text_input("採購金額上限",value="0")
    purchase_level = get_cost_range(float(purchase_limit))
else:
    purchase_level = get_cost_range(float(budget))

purchase_level = st.selectbox("採購級距",options=["公告金額十分之一之採購","未達公告金額而逾公告金額十分之一之採購","公告金額以上未達查核金額之採購","查核金額以上未達巨額之採購"],index=["公告金額十分之一之採購","未達公告金額而逾公告金額十分之一之採購","公告金額以上未達查核金額之採購","查核金額以上未達巨額之採購"].index(purchase_level))

st.markdown("---")
st.subheader("資格及進度")

# 保留決標

bid_award=st.checkbox("保留決標")

contractor_qual=get_contractor(float(budget))
contractor_qual=st.selectbox("廠商資格",options=["設立於雲林縣或毗鄰縣市之土木包工業，或丙等以上綜合營造業","設立於雲林縣或毗鄰縣市並依營造業法規定辦理資本額增資之土木包工業，或丙等以上綜合營造業","丙等(含)綜合營造業以上","依營造業法規定辦理資本額增資之丙等綜合營造業，或乙等以上綜合營造業","乙等(含)綜合營造業以上","依營造業法規定辦理資本額增資之乙等綜合營造業，或甲等以上綜合營造業","甲等(含)綜合營造業以上"],index=["設立於雲林縣或毗鄰縣市之土木包工業，或丙等以上綜合營造業","設立於雲林縣或毗鄰縣市並依營造業法規定辦理資本額增資之土木包工業，或丙等以上綜合營造業","丙等(含)綜合營造業以上","依營造業法規定辦理資本額增資之丙等綜合營造業，或乙等以上綜合營造業","乙等(含)綜合營造業以上","依營造業法規定辦理資本額增資之乙等綜合營造業，或甲等以上綜合營造業","甲等(含)綜合營造業以上"].index(contractor_qual))

work_days=st.text_input("工期")

mode2=st.radio("開工型式",["一般流程","指定開工日","逕流廢汙水"])

start_date=None

if mode2=="指定開工日":
    start_date=st.date_input("指定開工日").strftime("%Y-%m-%d")

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
    '預算金額': budget,
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
    '保留決標': bid_award
    
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

st.toast(doc_folder)

output_dir=os.path.join(".", data['標案名稱'])
# output_dir=r".\output2"

submitted = st.button("產製招標文件",type="primary")

if submitted:

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
            st.toast(file)
            file_path = os.path.join(root, file) # 取得文件的完整路徑
            relative_path = os.path.relpath(file_path, doc_folder) # 取得相對路徑
            output_file_path=os.path.join(output_dir,relative_path) # 取得輸出文件的完整路徑
            output_folder = os.path.dirname(output_file_path)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            shutil.copy(file_path,output_file_path) # 將文件複製到輸出目錄

            if file.endswith(".docx"):
                replace_text_within_percent_signs(output_file_path, data)
                files_processed += 1
                progress_bar.progress(files_processed / total_files)
                status_text.text(f"正在處理文件: {file}")
                    
        # Clear progress indicators
        status_text.empty()
        progress_bar.empty()
            
    if files_processed > 0:
        st.success(f"完成處理 {files_processed} 個文件！")
        st.info(f"處理後的文件已保存在: {output_dir}")
            
        # Create ZIP file for download
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # print(file_path)
                    # 使用相對路徑來保存文件
                    # rel_path = os.path.basename(file_path)
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