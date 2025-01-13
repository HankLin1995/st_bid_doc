import streamlit as st

VERSION_NUMBER = "V1.2.2"

@st.dialog("⭕系統公告")
def msg_content():
    st.subheader("®️作者: HankLin") 
    st.write("這是用於產製招標文件的工具")
    st.markdown("---")
    st.write("版本:"+VERSION_NUMBER )

st.set_page_config(page_title=f"工程招標文件{VERSION_NUMBER}", page_icon="☕")

# st.sidebar.title("工程招標文件處理工具V1.2")
# st.sidebar.info("作者: HankLin")

bidform_page=st.Page("view_bidform.py",title="預算書審查",icon=":material/contract:")
biddoc_page=st.Page("view_biddoc.py",title="投標文件",icon=":material/assignment:",default=True)

pg=st.navigation([bidform_page,biddoc_page])

if "show_info" not in st.session_state:
    st.session_state.show_info = True

if st.session_state.show_info:
    msg_content()
    st.session_state.show_info = False

pg.run()