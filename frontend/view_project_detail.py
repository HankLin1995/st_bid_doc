import streamlit as st
import requests
import pandas as pd
import os
import io
import zipfile
from dotenv import load_dotenv
from docx_utils import read_tender_document,replace_text_within_percent_signs
import time
import shutil
from utils import (
    convert_data,
    get_work_type,
    get_employ_type,
    get_cost_type,
    get_cost_range,
    get_contractor,
    num_to_chinese
)

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

def update_project_status(project_id, project_data):
    response = requests.put(f"{BACKEND_URL}/projects/{project_id}/status", json=project_data)
    if response.status_code != 200:
        print(f"Error: {response.status_code}", response.json())
    return response.status_code == 200

projects = get_projects()
df = pd.DataFrame(projects)

# my_pass=st.sidebar.text_input("請輸入密碼",type="password")

# if my_pass!=os.getenv("PASSWORD"):
#     st.stop()

st.markdown("### 🔍 專案詳細資訊")

if "project_name" not in st.session_state:
    st.session_state.project_name = df.iloc[0]['project_name']

selected_project = st.sidebar.selectbox(
    "選擇專案",
    options=df['project_name'].tolist(),
    index=df['project_name'].tolist().index(st.session_state.project_name),
    # format_func=lambda x: f"{x} - {df[df['project_number']==x]['project_name'].iloc[0]}",
)

st.session_state.project_name = selected_project

tab1,tab2,tab3,tab4=st.tabs(["詳細資訊","投標文件","公文DI","移辦單"])

with tab1:

    if selected_project:

        project_data = df[df['project_name'] == selected_project].iloc[0]

        st.session_state.project_data=project_data.to_dict()

        # st.sidebar.json(st.session_state)

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
                        "supervisor_personnel": supervisor_personnel,
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

with tab3: 
    st.markdown("#### 📄 公文DI")
    document_templates = {
        "招標簽-已核定": "招標簽(新)-工程-已核定.txt",
        "招標簽-未核定": "招標簽(新)-工程-未核定.txt",
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

with tab4:
    st.markdown("#### 📄 移辦單")

    if project_data.get('outsourcing_items')!="":
        selected_template="採購案件移辦單(103.2.18版)-有備註.docx"
    else:
        selected_template="採購案件移辦單(103.2.18版)-無備註.docx"

    st.write("註記內容",project_data.get('outsourcing_items'))

    os.makedirs("output", exist_ok=True)

    if st.button("產生文件",key="generate_doc"):
            
            template_path = os.path.join("src", "移辦單", selected_template)
            output_path = os.path.join("output", f"{selected_project}_{selected_template}")

            shutil.copyfile(template_path, output_path)

            # 準備替換的資料
            replacements = {
                "工程名稱": project_data['project_name'],
                "再生粒料": project_data['outsourcing_items'],
            }
            
            # 產生文件
            replace_text_within_percent_signs(output_path, replacements)
            st.success(f"文件已產生：{output_path}")

            #更新狀態

            response = requests.put(f"{BACKEND_URL}/projects/{project_data['id']}/status", json={
                "id": str(project_data['id']),
                "status": "移辦"
            })

            if response.status_code != 200:
                st.error("無法更新狀態")
            else:
                st.success("狀態已更新")

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

            # 更新狀態
            update_project_data={
                "status" : "上網"
            }

            if update_project_status(project_data['id'], update_project_data)==200:
                st.success("狀態已更新")

with tab2:

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

        bid_bond=st.number_input("押標金金額",value=project_data['bid_bond'] if 'project_data' in st.session_state else 0)
        bid_bond_chinese=num_to_chinese(bid_bond)
        # st.write(f"押標金金額為:{bid_bond_chinese}")

        performance_bond=st.number_input("履約保證金",value=project_data['performance_bond'] if 'project_data' in st.session_state else 0)
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

    # st.json(convert_data(data))

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

            response = requests.put(f"{BACKEND_URL}/projects/{project_data['id']}/bonds", json={
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