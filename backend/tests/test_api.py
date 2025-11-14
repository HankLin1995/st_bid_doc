import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import io

from main import app, get_db
from database import Base
from models import Project

# 設定測試資料庫
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建測試資料庫表
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """每個測試前後清理資料庫"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ==================== 專案相關測試 ====================

def test_create_project():
    """測試創建專案"""
    project_data = {
        "project_name": "測試工程",
        "project_number": "TEST-001",
        "approved_amount": 1000000,
        "branch_office": "斗六分處",
        "funding_source": "國庫撥款",
        "total_budget": 950000,
        "contract_amount": 900000,
        "duration": 90,
        "construction_content": "測試內容",
        "location": "雲林縣",
        "supervisor": "測試監造",
        "year": 113
    }
    
    response = client.post("/projects/", json=project_data)
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == "測試工程"
    assert data["project_number"] == "TEST-001"
    assert "id" in data

def test_create_duplicate_project():
    """測試創建重複專案編號"""
    project_data = {
        "project_name": "測試工程",
        "project_number": "TEST-001",
        "approved_amount": 1000000,
        "year": 113
    }
    
    # 第一次創建
    response1 = client.post("/projects/", json=project_data)
    assert response1.status_code == 200
    
    # 第二次創建相同編號
    response2 = client.post("/projects/", json=project_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

def test_read_projects():
    """測試讀取專案列表"""
    # 創建測試專案
    project_data = {
        "project_name": "測試工程1",
        "project_number": "TEST-001",
        "approved_amount": 1000000,
        "year": 113
    }
    client.post("/projects/", json=project_data)
    
    # 讀取列表
    response = client.get("/projects/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["project_name"] == "測試工程1"

def test_read_project_by_number():
    """測試根據專案編號讀取專案"""
    # 創建測試專案
    project_data = {
        "project_name": "測試工程",
        "project_number": "TEST-001",
        "approved_amount": 1000000,
        "year": 113
    }
    client.post("/projects/", json=project_data)
    
    # 讀取專案
    response = client.get("/projects/TEST-001")
    assert response.status_code == 200
    data = response.json()
    assert data["project_number"] == "TEST-001"

def test_read_nonexistent_project():
    """測試讀取不存在的專案"""
    response = client.get("/projects/NONEXISTENT")
    assert response.status_code == 404

def test_update_project_status():
    """測試更新專案狀態"""
    # 創建測試專案
    project_data = {
        "project_name": "測試工程",
        "project_number": "TEST-001",
        "approved_amount": 1000000,
        "year": 113
    }
    create_response = client.post("/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # 更新狀態
    update_data = {"status": "預算書"}
    response = client.put(f"/projects/{project_id}/status", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == "預算書"

def test_delete_project():
    """測試刪除專案"""
    # 創建測試專案
    project_data = {
        "project_name": "測試工程",
        "project_number": "TEST-001",
        "approved_amount": 1000000,
        "year": 113
    }
    create_response = client.post("/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # 刪除專案
    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # 確認已刪除
    get_response = client.get(f"/projects/TEST-001")
    assert get_response.status_code == 404

# ==================== PDF上傳測試 ====================

def test_upload_ecological_pdf():
    """測試上傳生態檢核PDF"""
    # 創建測試PDF檔案
    pdf_content = b"%PDF-1.4 test content"
    pdf_file = io.BytesIO(pdf_content)
    
    files = {"file": ("test.pdf", pdf_file, "application/pdf")}
    response = client.post("/upload-pdf/113/測試工程/ecological", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "檔案上傳成功"
    assert "113-測試工程_生態檢核.pdf" in data["filename"]

def test_upload_carbon_pdf():
    """測試上傳碳排計算PDF"""
    pdf_content = b"%PDF-1.4 test content"
    pdf_file = io.BytesIO(pdf_content)
    
    files = {"file": ("test.pdf", pdf_file, "application/pdf")}
    response = client.post("/upload-pdf/113/測試工程/carbon", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "檔案上傳成功"
    assert "113-測試工程_碳排計算.pdf" in data["filename"]

def test_upload_invalid_file_type():
    """測試上傳非PDF檔案"""
    txt_content = b"This is not a PDF"
    txt_file = io.BytesIO(txt_content)
    
    files = {"file": ("test.txt", txt_file, "text/plain")}
    response = client.post("/upload-pdf/113/測試工程/ecological", files=files)
    
    assert response.status_code == 400
    assert "只接受PDF檔案" in response.json()["detail"]

def test_upload_invalid_pdf_type():
    """測試上傳無效的PDF類型"""
    pdf_content = b"%PDF-1.4 test content"
    pdf_file = io.BytesIO(pdf_content)
    
    files = {"file": ("test.pdf", pdf_file, "application/pdf")}
    response = client.post("/upload-pdf/113/測試工程/invalid_type", files=files)
    
    assert response.status_code == 400
    assert "無效的PDF類型" in response.json()["detail"]

def test_check_pdf_exists():
    """測試檢查PDF檔案是否存在"""
    # 先上傳一個PDF
    pdf_content = b"%PDF-1.4 test content"
    pdf_file = io.BytesIO(pdf_content)
    files = {"file": ("test.pdf", pdf_file, "application/pdf")}
    client.post("/upload-pdf/113/測試工程/ecological", files=files)
    
    # 檢查檔案是否存在
    response = client.get("/check-pdf/113/測試工程/ecological")
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] == True
    assert "113-測試工程_生態檢核.pdf" in data["filename"]

def test_check_nonexistent_pdf():
    """測試檢查不存在的PDF"""
    response = client.get("/check-pdf/999/不存在的工程/ecological")
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] == False
    assert data["filename"] is None

# ==================== 計畫相關測試 ====================

def test_create_plan():
    """測試創建計畫"""
    plan_data = {
        "plan_name": "測試計畫",
        "plan_code": "PLAN-001",
        "description": "測試計畫描述",
        "projects": []
    }
    
    response = client.post("/plans/", json=plan_data)
    assert response.status_code == 200
    data = response.json()
    assert data["plan_name"] == "測試計畫"
    assert data["plan_code"] == "PLAN-001"

def test_read_plans():
    """測試讀取計畫列表"""
    # 創建測試計畫
    plan_data = {
        "plan_name": "測試計畫",
        "plan_code": "PLAN-001",
        "description": "測試",
        "projects": []
    }
    client.post("/plans/", json=plan_data)
    
    # 讀取列表
    response = client.get("/plans/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_delete_plan():
    """測試刪除計畫"""
    # 創建測試計畫
    plan_data = {
        "plan_name": "測試計畫",
        "plan_code": "PLAN-001",
        "description": "測試",
        "projects": []
    }
    create_response = client.post("/plans/", json=plan_data)
    plan_id = create_response.json()["id"]
    
    # 刪除計畫
    response = client.delete(f"/plans/{plan_id}")
    assert response.status_code == 200
    assert "已刪除" in response.json()["message"]
