import streamlit as st

VERSION_NUMBER = "V2.1.1"

@st.dialog("⭕系統公告")
def msg_content():
    st.subheader("®️作者: HankLin") 
    st.write("這是用於產製招標文件的工具")
    # st.markdown("☕工程招標文件")
    st.markdown("---")
    st.write("版本:"+VERSION_NUMBER )

st.set_page_config(page_title=f"工程審查系統 {VERSION_NUMBER}")
st.logo("LOGO.PNG")

if "show_info" not in st.session_state:
    msg_content()
    st.session_state.show_info = True

if "test_mode" not in st.session_state:
    st.session_state.test_mode = False

try:
    if st.query_params["test_mode"] == "1":
        st.session_state.test_mode =True

except:
    pass

# 執行LINE登入再進入主要畫面

bidform_page=st.Page("view_bidform.py",title="預算書審查",icon=":material/contract:",default=True)
project_page=st.Page("view_project.py",title="案件總覽",icon=":material/dashboard:")
project_detail_page=st.Page("view_project_detail.py",title="案件詳細資訊",icon=":material/dashboard:")
biddoc_page=st.Page("view_biddoc.py",title="投標文件",icon=":material/assignment:")

pg=st.navigation({
    "預算管理":[bidform_page],
    "專案管理":[project_page,project_detail_page],
    "招標管理":[biddoc_page]
})

pg.run()
