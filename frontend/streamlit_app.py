import streamlit as st
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

VERSION_NUMBER = "V1.3.0"
load_dotenv()

# LINE Login configuration
LINE_CHANNEL_ID = os.getenv('LINE_CHANNEL_ID')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8501')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

@st.dialog("⭕系統公告")
def msg_content():
    st.subheader("®️作者: HankLin") 
    st.write("這是用於產製招標文件的工具")
    st.markdown("---")
    st.write("版本:"+VERSION_NUMBER )

st.set_page_config(page_title=f"工程招標文件{VERSION_NUMBER}", page_icon="☕")

def line_login():
    if 'user_info' not in st.session_state:
        auth_url = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={LINE_CHANNEL_ID}&redirect_uri={REDIRECT_URI}&state=12345&scope=profile%20openid%20email"
        
        if "code" not in st.experimental_get_query_params():
            st.write("請先登入LINE帳號")
            st.link_button("LINE登入", auth_url)
            st.stop()
        else:
            code = st.experimental_get_query_params()["code"][0]
            
            # Exchange code for access token
            token_url = "https://api.line.me/oauth2/v2.1/token"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'client_id': LINE_CHANNEL_ID,
                'client_secret': LINE_CHANNEL_SECRET
            }
            
            response = requests.post(token_url, headers=headers, data=data)
            if response.status_code == 200:
                token_data = response.json()
                
                # Get user profile
                profile_url = "https://api.line.me/v2/profile"
                headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
                profile_response = requests.get(profile_url, headers=headers)
                
                if profile_response.status_code == 200:
                    user_profile = profile_response.json()
                    
                    # Save user info to backend
                    user_data = {
                        "user_id": user_profile["userId"],
                        "user_name": user_profile["displayName"],
                        "nick_name": user_profile.get("displayName", ""),
                        "pic_url": user_profile.get("pictureUrl", "")
                    }
                    
                    backend_response = requests.post(f"{BACKEND_URL}/users/", json=user_data)
                    if backend_response.status_code in [200, 400]:  # 400 means user already exists
                        st.session_state.user_info = user_profile
                        st.rerun()
                    else:
                        st.error("無法儲存使用者資訊")
                        st.stop()
                else:
                    st.error("無法取得使用者資訊")
                    st.stop()
            else:
                st.error("LINE登入失敗")
                st.stop()

# 執行LINE登入再進入主要畫面
line_login()

# Only show main content after successful login
if 'user_info' in st.session_state:
    bidform_page=st.Page("view_bidform.py",title="預算書審查",icon=":material/contract:")
    biddoc_page=st.Page("view_biddoc.py",title="投標文件",icon=":material/assignment:",default=True)

    pg=st.navigation([bidform_page,biddoc_page])

    if "show_info" not in st.session_state:
        st.session_state.show_info = True

    if st.session_state.show_info:
        msg_content()
        st.session_state.show_info = False

    # Add logout button
    if st.sidebar.button("登出"):
        del st.session_state.user_info
        st.rerun()

    pg.run()