import streamlit as st
import requests
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = 'http://backend:8000'

# 排序選項常數
SORT_OPTIONS = [
    "檔案名稱 (A-Z)",
    "檔案名稱 (Z-A)",
    "修改時間 (新到舊)",
    "修改時間 (舊到新)",
    "檔案大小 (大到小)",
    "檔案大小 (小到大)"
]

@st.dialog("顯示PDF", width="large")
def show_pdf(content: bytes) -> None:
    """顯示 PDF 內容"""
    st.pdf(content)

@st.dialog("確認刪除", width="small")
def confirm_delete_dialog(filename: str, pdf_type: str) -> bool:
    """刪除確認對話框"""
    st.warning(f"確定要刪除檔案 **{filename}** 嗎？")
    st.caption("此操作無法復原")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 確認刪除", type="primary", use_container_width=True):
            try:
                response = requests.delete(f"{BACKEND_URL}/pdf/delete/{pdf_type}/{filename}")
                if response.status_code == 200:
                    st.success("檔案已刪除")
                    st.session_state.refresh_files = True
                    st.rerun()
                else:
                    st.error(f"刪除失敗: {response.json().get('detail', '未知錯誤')}")
            except Exception as e:
                st.error(f"刪除錯誤: {e}")
    with col2:
        if st.button("❌ 取消", use_container_width=True):
            st.rerun()

@st.dialog("上傳 PDF 檔案", width="medium")
def upload_file_dialog(pdf_type: str) -> None:
    """上傳檔案對話框"""
    st.markdown(f"### 上傳 {'生態檢核' if pdf_type == 'ecological' else '碳排計算'} PDF")
    
    uploaded_file = st.file_uploader(
        "選擇 PDF 檔案",
        type=['pdf'],
        key=f"uploader_{pdf_type}"
    )
    
    if uploaded_file is not None:
        st.info(f"已選擇檔案: {uploaded_file.name}")
        
        st.markdown("---")
        st.markdown("#### 檔案資訊")
        
        year = st.number_input(
            "民國年度",
            min_value=100,
            max_value=200,
            value=113,
            step=1,
            key=f"year_{pdf_type}"
        )
        
        project_name = st.text_input(
            "工程名稱",
            placeholder="例如: XX水路改善工程",
            key=f"project_name_{pdf_type}"
        )
        
        project_number = st.text_input(
            "工程編號 (必填)",
            placeholder="例如: 雲林114T033",
            key=f"project_number_{pdf_type}"
        )
        
        if pdf_type == "carbon":
            plan_name = st.selectbox(
                "計畫名稱",
                options=["擴大灌溉", "更新改善", "未定"],
                key=f"plan_name_{pdf_type}"
            )
        else:
            plan_name = None
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 上傳", type="primary", use_container_width=True):
                if not project_name:
                    st.error("請輸入工程名稱")
                elif not project_number:
                    st.error("請輸入工程編號")
                else:
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        
                        params = {
                            "project_number": project_number,
                            "plan_name": plan_name
                        }
                        
                        params = {k: v for k, v in params.items() if v is not None}
                        
                        response = requests.post(
                            f"{BACKEND_URL}/upload-pdf/{year}/{project_name}/{pdf_type}",
                            files=files,
                            params=params
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result.get('message', '上傳成功')}")
                            st.info(f"檔案名稱: {result.get('filename')}")
                            st.session_state.refresh_files = True
                            st.balloons()
                        else:
                            error_detail = response.json().get('detail', '未知錯誤')
                            st.error(f"❌ 上傳失敗: {error_detail}")
                    except Exception as e:
                        st.error(f"❌ 上傳錯誤: {e}")
        
        with col2:
            if st.button("❌ 取消", use_container_width=True):
                st.rerun()

def format_file_size(size_bytes: int) -> str:
    """將檔案大小轉換為可讀格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def format_timestamp(timestamp: float) -> str:
    """將時間戳轉換為可讀格式"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def filter_files(files: List[Dict], search_term: str) -> List[Dict]:
    """根據搜尋關鍵字過濾檔案（支援檔案名稱和工程編號）"""
    if not search_term:
        return files
    
    search_lower = search_term.lower()
    filtered = []
    for f in files:
        # 搜尋檔案名稱
        if search_lower in f['filename'].lower():
            filtered.append(f)
            continue
        # 搜尋工程編號
        project_number = f.get('project_number')
        if project_number:
            # 確保工程編號是字串
            project_number_str = str(project_number).lower()
            if search_lower in project_number_str:
                filtered.append(f)
    
    return filtered

def sort_files(files: List[Dict], sort_option: str) -> List[Dict]:
    """根據排序選項排序檔案"""
    sort_mapping = {
        "檔案名稱 (A-Z)": (lambda x: x['filename'], False),
        "檔案名稱 (Z-A)": (lambda x: x['filename'], True),
        "修改時間 (新到舊)": (lambda x: x['modified_time'], True),
        "修改時間 (舊到新)": (lambda x: x['modified_time'], False),
        "檔案大小 (大到小)": (lambda x: x['size'], True),
        "檔案大小 (小到大)": (lambda x: x['size'], False)
    }
    
    key_func, reverse = sort_mapping.get(sort_option, (lambda x: x['filename'], False))
    return sorted(files, key=key_func, reverse=reverse)

def preview_pdf(pdf_url: str) -> None:
    """預覽 PDF 檔案"""
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            show_pdf(response.content)
        else:
            st.error("無法載入 PDF")
    except Exception as e:
        st.error(f"預覽失敗: {e}")

def download_single_pdf(pdf_url: str, filename: str) -> None:
    """下載單個 PDF 檔案"""
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            st.download_button(
                label="⬇️ 下載",
                data=response.content,
                file_name=filename,
                mime="application/pdf",
                key=f"download_{filename}"
            )
        else:
            st.error("無法下載檔案")
    except Exception as e:
        st.error(f"下載失敗: {e}")

def render_file_item(file: Dict, pdf_type: str, idx: int, selected_files: List[Dict]) -> None:
    """渲染單個檔案項目"""
    with st.container(border=True):
        col0, col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1, 1])
        
        with col0:
            # 勾選框
            is_selected = st.checkbox(
                "選擇",
                key=f"select_{pdf_type}_{idx}",
                label_visibility="collapsed"
            )
            if is_selected:
                file_info = {"pdf_type": pdf_type, "filename": file['filename']}
                if file_info not in selected_files:
                    selected_files.append(file_info)
        
        with col1:
            st.markdown(f"**📄 {file['filename']}**")
            project_number_text = f"工程編號: {file.get('project_number', '未知')}" if file.get('project_number') else "工程編號: 未知"
            st.caption(
                f"{project_number_text} | "
                f"大小: {format_file_size(file['size'])} | "
                f"修改時間: {format_timestamp(file['modified_time'])}"
            )
        
        with col2:
            if st.button("👁️ 預覽", key=f"view_{pdf_type}_{idx}"):
                pdf_url = f"{BACKEND_URL}/pdf/download/{pdf_type}/{file['filename']}"
                preview_pdf(pdf_url)
        
        with col3:
            pdf_url = f"{BACKEND_URL}/pdf/download/{pdf_type}/{file['filename']}"
            response = requests.get(pdf_url)
            if response.status_code == 200:
                st.download_button(
                    label="⬇️ 下載",
                    data=response.content,
                    file_name=file['filename'],
                    mime="application/pdf",
                    key=f"dl_{pdf_type}_{idx}"
                )
        
        with col4:
            if st.button("🗑️ 刪除", key=f"delete_{pdf_type}_{idx}", type="secondary"):
                confirm_delete_dialog(file['filename'], pdf_type)

def render_file_list(files: List[Dict], pdf_type: str, search_key: str, sort_key: str) -> None:
    """渲染檔案列表"""
    col_title, col_upload = st.columns([4, 1])
    with col_upload:
        if st.button("➕ 上傳檔案", key=f"upload_btn_{pdf_type}", type="primary"):
            upload_file_dialog(pdf_type)
    
    if not files:
        st.info(f"目前沒有{pdf_type}檔案")
        return
    
    # 搜尋功能
    search_term = st.text_input(
        "🔍 搜尋檔案名稱或工程編號",
        key=search_key,
        placeholder="輸入工程編號或關鍵字搜尋..."
    )
    
    # 過濾檔案
    filtered_files = filter_files(files, search_term)
    
    if not filtered_files:
        st.info("沒有符合搜尋條件的檔案")
        return
    
    # 排序選項
    # col_sort, col_batch = st.columns([3, 1])
    # with col_sort:
        # sort_option = st.selectbox("排序方式", SORT_OPTIONS, key=sort_key)
    
    # 排序檔案
    sorted_files = sort_files(filtered_files, "檔案名稱 (A-Z)")  # 將 filtered_files 傳入 sort_files
    
    # 顯示檔案數量
    st.caption(f"顯示 {len(sorted_files)} 個檔案")
    
    # 用於儲存選中的檔案
    selected_files = []
    
    # 顯示檔案列表
    for idx, file in enumerate(sorted_files):
        render_file_item(file, pdf_type, idx, selected_files)
    
    # 批次操作按鈕
    if selected_files:
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.info(f"已選擇 {len(selected_files)} 個檔案")
        with col2:
            if st.button(f"📦 批次下載", key=f"batch_download_{pdf_type}", type="primary"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/pdf/download-batch",
                        json=selected_files
                    )
                    if response.status_code == 200:
                        st.download_button(
                            label="💾 下載 ZIP 檔案",
                            data=response.content,
                            file_name=f"pdfs_{pdf_type}.zip",
                            mime="application/zip",
                            key=f"zip_{pdf_type}"
                        )
                    else:
                        st.error("批次下載失敗")
                except Exception as e:
                    st.error(f"批次下載錯誤: {e}")
        with col3:
            if st.button(f"🗑️ 批次刪除", key=f"batch_delete_{pdf_type}", type="secondary"):
                if st.session_state.get(f"confirm_batch_delete_{pdf_type}", False):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/pdf/delete-batch",
                            json=selected_files
                        )
                        if response.status_code == 200:
                            result = response.json()
                            st.success(result.get('message', '刪除成功'))
                            if result.get('failed_files'):
                                st.warning(f"部分檔案刪除失敗: {result['failed_files']}")
                            st.session_state.refresh_files = True
                            st.session_state[f"confirm_batch_delete_{pdf_type}"] = False
                            st.rerun()
                        else:
                            st.error("批次刪除失敗")
                    except Exception as e:
                        st.error(f"批次刪除錯誤: {e}")
                else:
                    st.session_state[f"confirm_batch_delete_{pdf_type}"] = True
                    st.warning("⚠️ 再次點擊確認批次刪除")
                    st.rerun()

def fetch_pdf_files() -> tuple:
    """從後端獲取 PDF 檔案列表"""
    response = requests.get(f"{BACKEND_URL}/pdf/list")
    if response.status_code != 200:
        raise Exception(f"無法獲取檔案列表: {response.status_code}")
    
    data = response.json()
    return (
        data.get('ecological', []),
        data.get('carbon', []),
        data.get('total', 0)
    )

def files_page() -> None:
    """PDF 檔案管理主頁面"""
    st.markdown("### PDF 檔案管理")
    
    try:
        # 獲取所有檔案列表
        ecological_files, carbon_files, total_files = fetch_pdf_files()
        
        # 建立標籤頁
        tab1, tab2 = st.tabs(["🌱 生態檢核 PDF", "♻️ 碳排計算 PDF"])
        
        # 生態檢核 PDF 標籤頁
        with tab1:
            st.markdown("#### 生態檢核 PDF 檔案")
            render_file_list(
                files=ecological_files,
                pdf_type="ecological",
                search_key="search_eco",
                sort_key="sort_eco"
            )
        
        # 碳排計算 PDF 標籤頁
        with tab2:
            st.markdown("#### 碳排計算 PDF 檔案")
            render_file_list(
                files=carbon_files,
                pdf_type="carbon",
                search_key="search_carbon",
                sort_key="sort_carbon"
            )
    
    except Exception as e:
        st.error(f"發生錯誤: {e}")

# 執行主頁面
files_page()