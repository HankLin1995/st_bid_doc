import streamlit as st
from models import Project, ProjectType, ProcurementType, ProjectStatus, get_db_session
from datetime import date

st.header("🔷預算書審查")

# 新增/編輯表單
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
        st.markdown("### 👜經費相關")
        funding_source = st.text_input("經費來源")
        approved_amount = st.number_input("核定金額", min_value=0.0)
        total_budget = st.number_input("總工程費", min_value=0.0)
        contract_amount = st.number_input("發包工作費", min_value=0.0)
        outsourcing_items = st.multiselect(
            "移辦單項目",
            ["瀝青混凝土鋪面", "控制性低強度回填材料(CLSM)", "級配粒料基層", "低密度再生透水混凝土"],
            default=[]
        )

# if st.button("儲存"):
#     try:
#         session = get_db_session()
#         project_data = {
#             "branch_office": branch_office,
#             "project_name": project_name,
#             "project_number": project_number,
#             "funding_source": funding_source,
#             "approved_amount": approved_amount,
#             "total_budget": total_budget,
#             "contract_amount": contract_amount,
#             "duration": duration,
#             "construction_content": construction_content,
#             "location": location,
#             "supervisor": supervisor,
#             "supervisor_personnel": supervisor_personnel,
#             "outsourcing_items": ",".join(outsourcing_items),
#             "procurement_type": ProcurementType.ENGINEERING,  # 預設為工程
#             "year": date.today().year  # 預設為當前年度
#         }

#         if hasattr(st.session_state, 'editing_project'):
#             # 更新現有工程
#             project = project_crud.update_project(
#                 session, 
#                 st.session_state.editing_project.id, 
#                 project_data
#             )
#             st.success("工程更新成功！")
#             del st.session_state.editing_project
#         else:
#             # 創建新工程
#             project = project_crud.create_project(session, project_data)
#             st.success("工程創建成功！")

#         # 重新載入工程列表
#         st.session_state.projects = project_crud.get_projects(session)
        
#     except Exception as e:
#         st.error(f"操作失敗：{str(e)}")
#     finally:
#         session.close()

