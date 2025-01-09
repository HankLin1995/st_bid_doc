import streamlit as st

VERSION_NUMBER = "V1.2"

st.set_page_config(page_title=f"工程招標文件{VERSION_NUMBER}", page_icon="🌌", layout="wide")

# st.sidebar.title("工程招標文件處理工具V1.2")
# st.sidebar.info("作者: HankLin")

bidform_page=st.Page("view_bidform.py",title="預算書審查",icon=":material/contract:")
biddoc_page=st.Page("view_biddoc.py",title="投標文件",icon=":material/assignment:")

pg=st.navigation({"招標文件": [bidform_page,biddoc_page]})

pg.run()