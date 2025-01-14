import streamlit as st
import dotenv
import os

dotenv.load_dotenv()

VERSION_NUMBER = "V1.3.0"

@st.dialog("⭕系統公告")
def msg_content():
    st.subheader("®️作者: HankLin") 
    st.write("這是用於產製招標文件的工具")
    st.markdown("---")
    st.write("版本:"+VERSION_NUMBER )

st.set_page_config(page_title=f"工程招標文件{VERSION_NUMBER}", page_icon="☕")

if "show_info" not in st.session_state:
    st.session_state.show_info = True

if st.session_state.show_info:
    msg_content()
    st.session_state.show_info = False

if "password" not in st.session_state:
    st.session_state.password = ""

bidform_page=st.Page("view_bidform.py",title="預算書審查",icon=":material/contract:",default=True)
biddoc_page=st.Page("view_biddoc.py",title="投標文件",icon=":material/assignment:")

pg=st.navigation([bidform_page,biddoc_page])
pg.run()