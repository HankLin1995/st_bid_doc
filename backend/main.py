from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud
from database import engine, get_db
import os
import shutil
from pathlib import Path
import zipfile
import io
from urllib.parse import quote

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# PDF 檔案目錄設定
BASE_DIR = Path(__file__).parent
UPLOAD_DIR1 = BASE_DIR / "data" / "pdfs" / "生態檢核"
UPLOAD_DIR2 = BASE_DIR / "data" / "pdfs" / "碳排計算"
UPLOAD_DIR1.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR2.mkdir(parents=True, exist_ok=True)

@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # Check if a project with the same project_number already exists
    existing_project = db.query(models.Project).filter(models.Project.project_number == project.project_number).first()
    if existing_project:
        raise HTTPException(status_code=400, detail="Project with this project number already exists")
    
    # Create new project if it doesn't exist
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

@app.get("/projects/all", response_model=List[schemas.Project])
def read_all_projects(db: Session = Depends(get_db)):
    projects = db.query(models.Project).all()
    return projects

@app.get("/projects/{project_number}", response_model=schemas.Project)
def read_project(project_number: str, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.project_number == project_number).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}/bonds", response_model=schemas.Project)
def update_project_bonds(project_id: int, project: schemas.ProjectUpdateBond, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.model_dump().items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.put("/projects/{project_id}/status", response_model=schemas.Project)
def update_project_bonds(project_id: int, project: schemas.ProjectUpdateStatus, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.model_dump().items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if project_number is being updated and if it already exists
    if project.project_number and project.project_number != db_project.project_number:
        existing_project = db.query(models.Project).filter(
            models.Project.project_number == project.project_number,
            models.Project.id != project_id
        ).first()
        if existing_project:
            raise HTTPException(status_code=400, detail="Project with this project number already exists")
    
    for key, value in project.model_dump().items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 刪除對應的 PDF 檔案
    deleted_files = []
    
    # 1. 刪除生態檢核 PDF (格式: {year}-{project_name}.pdf)
    if project.year and project.project_name:
        ecological_filename = f"{project.year}-{project.project_name}.pdf"
        ecological_path = UPLOAD_DIR1 / ecological_filename
        if ecological_path.exists():
            ecological_path.unlink()
            deleted_files.append(f"生態檢核: {ecological_filename}")
    
    # 2. 刪除碳排計算 PDF (格式: {project_number}_{plan_name}_減碳簡易檢核表_{project_name}.pdf)
    if project.project_number and project.project_name:
        # 判斷計畫名稱
        plan_name = "未定"
        if "擴大灌溉" in project.project_name:
            plan_name = "擴大灌溉"
        elif "更新改善" in project.project_name:
            plan_name = "更新改善"
        
        carbon_filename = f"{project.project_number}_{plan_name}_減碳簡易檢核表_{project.project_name}.pdf"
        carbon_path = UPLOAD_DIR2 / carbon_filename
        if carbon_path.exists():
            carbon_path.unlink()
            deleted_files.append(f"碳排計算: {carbon_filename}")
    
    # 刪除資料庫記錄
    db.delete(project)
    db.commit()
    
    return {
        "message": "Project deleted successfully",
        "deleted_files": deleted_files
    }

# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(models.User).filter(models.User.user_id == user.user_id).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="User ID already registered")
#     db_user = models.User(**user.model_dump())
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# @app.get("/users/", response_model=List[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = db.query(models.User).offset(skip).limit(limit).all()
#     return users

# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: str, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.user_id == user_id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# @app.put("/users/{user_id}", response_model=schemas.User)
# def update_user(user_id: str, user: schemas.UserUpdate, db: Session = Depends(get_db)):
#     db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     update_data = user.model_dump(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_user, key, value)
    
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# @app.delete("/users/{user_id}")
# def delete_user(user_id: str, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.user_id == user_id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     db.delete(user)
#     db.commit()
#     return {"message": "User deleted successfully"}

@app.post("/plans/", response_model=schemas.Plan)
def create_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    return crud.create_plan(db=db, plan=plan)

@app.get("/plans/{plan_id}", response_model=schemas.Plan)
def read_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = crud.get_plan(db, plan_id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="計畫未找到")
    return db_plan

@app.get("/plans/", response_model=List[schemas.Plan])
def read_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    plans = crud.get_plans(db, skip=skip, limit=limit)
    return plans

@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    if not crud.delete_plan(db, plan_id=plan_id):
        raise HTTPException(status_code=404, detail="計畫未找到")
    return {"message": "計畫已刪除"}

# PDF 檔案上傳端點

@app.get("/pdf/list")
def list_all_pdfs():
    """列出所有已上傳的 PDF 檔案"""
    ecological_files = []
    carbon_files = []
    
    # 列出生態檢核檔案
    if UPLOAD_DIR1.exists():
        for file_path in UPLOAD_DIR1.glob("*.pdf"):
            file_stat = file_path.stat()
            ecological_files.append({
                "filename": file_path.name,
                "size": file_stat.st_size,
                "modified_time": file_stat.st_mtime,
                "type": "ecological"
            })
    
    # 列出碳排計算檔案
    if UPLOAD_DIR2.exists():
        for file_path in UPLOAD_DIR2.glob("*.pdf"):
            file_stat = file_path.stat()
            carbon_files.append({
                "filename": file_path.name,
                "size": file_stat.st_size,
                "modified_time": file_stat.st_mtime,
                "type": "carbon"
            })
    
    return {
        "ecological": ecological_files,
        "carbon": carbon_files,
        "total": len(ecological_files) + len(carbon_files)
    }

@app.get("/pdf/ecological/{year}/{project_name}")
def get_ecological_pdf(year: int, project_name: str):
    """取得生態檢核 PDF 檔案"""
    filename = f"{year}-{project_name}.pdf"
    file_path = UPLOAD_DIR1 / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    # 對中文檔名進行 URL 編碼（RFC 5987）
    encoded_filename = quote(filename)

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )

@app.get("/pdf/carbon/{project_number}/{project_name}")
def get_carbon_pdf(
    project_number: str, 
    project_name: str,
    plan_name: str = None
):
    """
    取得碳排計算 PDF 檔案
    project_number: 工程編號
    project_name: 工程名稱
    plan_name: 計畫名稱 (選填，根據工程名稱自動判斷)
    """
    # 根據工程名稱判斷計畫名稱
    if not plan_name:
        if "擴大灌溉" in project_name:
            plan_name = "擴大灌溉"
        elif "更新改善" in project_name:
            plan_name = "更新改善"
        else:
            plan_name = "未定"
    
    filename = f"{project_number}_{plan_name}_減碳簡易檢核表_{project_name}.pdf"
    file_path = UPLOAD_DIR2 / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    # 對中文檔名進行 URL 編碼（RFC 5987）
    encoded_filename = quote(filename)

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )

@app.get("/pdf/download/{pdf_type}/{filename}")
def download_pdf_by_filename(pdf_type: str, filename: str):
    """
    根據檔案名稱下載 PDF
    pdf_type: 'ecological' 或 'carbon'
    filename: 檔案名稱
    """
    if pdf_type not in ['ecological', 'carbon']:
        raise HTTPException(status_code=400, detail="無效的PDF類型")
    
    if pdf_type == "ecological":
        file_path = UPLOAD_DIR1 / filename
    else:
        file_path = UPLOAD_DIR2 / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # 對中文檔名進行 URL 編碼（RFC 5987）
    encoded_filename = quote(filename)
    
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )

@app.post("/pdf/download-batch")
async def download_batch_pdfs(files: List[dict]):
    """
    批次下載 PDF 檔案，打包成 ZIP
    files: [{"pdf_type": "ecological", "filename": "xxx.pdf"}, ...]
    """
    if not files:
        raise HTTPException(status_code=400, detail="沒有選擇檔案")
    
    # 創建記憶體中的 ZIP 檔案
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_info in files:
            pdf_type = file_info.get('pdf_type')
            filename = file_info.get('filename')
            
            if pdf_type not in ['ecological', 'carbon']:
                continue
            
            # 確定檔案路徑
            if pdf_type == "ecological":
                file_path = UPLOAD_DIR1 / filename
            else:
                file_path = UPLOAD_DIR2 / filename
            
            # 如果檔案存在，添加到 ZIP
            if file_path.exists():
                # 在 ZIP 中使用子資料夾區分類型
                folder_name = "生態檢核" if pdf_type == "ecological" else "碳排計算"
                zip_file.write(file_path, f"{folder_name}/{filename}")
    
    # 將指針移到開頭
    zip_buffer.seek(0)
    
    # 返回 ZIP 檔案
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=pdfs.zip"}
    )

@app.post("/upload-pdf/{year}/{project_name}/{pdf_type}")
async def upload_pdf(
    year: int,
    project_name: str,
    pdf_type: str,
    file: UploadFile = File(...),
    project_number: str = None,
    plan_name: str = None
):
    """
    上傳PDF檔案
    year: 民國年度
    project_name: 工程名稱
    pdf_type: 'ecological' (生態檢核) 或 'carbon' (碳排計算)
    project_number: 工程編號 (碳排計算必填)
    plan_name: 計畫名稱 (碳排計算選填，預設為"雲林農田水利署")
    """
    # 驗證檔案類型
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只接受PDF檔案")
    
    # 驗證 pdf_type
    if pdf_type not in ['ecological', 'carbon']:
        raise HTTPException(status_code=400, detail="無效的PDF類型")

    # 建立檔案名稱
    if pdf_type == "ecological":
        # 生態檢核檔案名稱：年度-工程名稱.pdf
        filename = f"{year}-{project_name}.pdf"
        file_path = UPLOAD_DIR1 / filename
    else:
        # 碳排計算檔案名稱：工程編號_計畫名稱_減碳簡易檢核表_工程名稱.pdf
        if not project_number:
            raise HTTPException(status_code=400, detail="碳排計算PDF需提供工程編號")
        
        # 根據工程名稱判斷計畫名稱
        if not plan_name:
            if "擴大灌溉" in project_name:
                plan_name = "擴大灌溉"
            elif "更新改善" in project_name:
                plan_name = "更新改善"
            else:
                plan_name = "未定"
        
        filename = f"{project_number}_{plan_name}_減碳簡易檢核表_{project_name}.pdf"
        file_path = UPLOAD_DIR2 / filename

    # 儲存檔案
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {
            "message": "檔案上傳成功",
            "filename": filename,
            "path": str(file_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"檔案上傳失敗: {str(e)}")