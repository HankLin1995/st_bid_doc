import streamlit as st
from models import Project, ProjectType, ProcurementType, ProjectStatus, get_db_session
from datetime import date

st.header("🔷預算書審查")

with st.container(border=True):

    st.markdown("### 🎯任務分配")

    branch_office = st.text_input("所屬分處")
    supervisor = st.text_input("主辦監造")
    supervisor_personnel = st.text_input("監造人員")

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):

        st.markdown("### 🍪基本資料")

        project_name = st.text_input("工程名稱")
        project_number = st.text_input("工程編號")
        location = st.text_input("工程地點")
        duration = st.number_input("工期", min_value=1)
        construction_content = st.text_input("施工內容")


with col2:

    with st.container(border=True):

        st.markdown("### 👜經費項目")

        funding_source = st.text_input("經費來源")
        approved_amount = st.number_input("核定金額", min_value=0.0)
        total_budget = st.number_input("總工程費", min_value=0.0)
        contract_amount = st.number_input("發包工作費", min_value=0.0)
        outsourcing_items = st.multiselect(
            "移辦單項目",
            ["碎石級配", "AC", "CLSM", "低密度再生透水RC"],
            default=[]
        )      

if st.button("儲存"):

# if submitted:
    try:
        session = get_db_session()
        
        new_project = Project(
            year=year,
            # project_type=ProjectType.GENERAL if project_type == "一般" else ProjectType.OPEN,
            branch_office=branch_office,
            project_name=project_name,
            project_number=project_number,
            funding_source=funding_source,
            approved_amount=approved_amount,
            total_budget=total_budget,
            contract_amount=contract_amount,
            duration=duration,
            construction_content=construction_content,
            location=location,
            supervisor=supervisor,
            supervisor_personnel=supervisor_personnel,
            procurement_type=ProcurementType.ENGINEERING if procurement_type == "工程" 
                            else ProcurementType.SERVICE if procurement_type == "勞務"
                            else ProcurementType.GOODS,
            outsourcing_items=",".join(outsourcing_items),
            procurement_tier=procurement_tier,
            bid_bond=bid_bond,
            performance_bond=performance_bond,
            contractor_qualifications=contractor_qualifications,
            status=ProjectStatus[status]
        )
        
        session.add(new_project)
        session.commit()
        st.success("表單提交成功！")
        
    except Exception as e:
        st.error(f"提交失敗：{str(e)}")
        session.rollback()
    finally:
        session.close()