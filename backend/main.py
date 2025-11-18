from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud
from database import engine, get_db
import os
import shutil
from pathlib import Path

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

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
UPLOAD_DIR1 = Path("../data/pdfs/生態檢核")
UPLOAD_DIR2 = Path("../data/pdfs/碳排計算")
UPLOAD_DIR1.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR2.mkdir(parents=True, exist_ok=True)

@app.post("/upload-pdf/{year}/{project_name}/{pdf_type}")
async def upload_pdf(
    year: int,
    project_name: str,
    pdf_type: str,
    file: UploadFile = File(...)
):
    """
    上傳PDF檔案
    year: 民國年度
    project_name: 工程名稱
    pdf_type: 'ecological' (生態檢核) 或 'carbon' (碳排計算)
    """
    # 驗證檔案類型
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只接受PDF檔案")
    
    # 驗證 pdf_type
    if pdf_type not in ['ecological', 'carbon']:
        raise HTTPException(status_code=400, detail="無效的PDF類型")

    # 建立檔案名稱：年度-工程名稱_PDF類型.pdf
    pdf_type_name = "生態檢核" if pdf_type == "ecological" else "碳排計算"
    filename = f"{year}-{project_name}.pdf"

    if pdf_type == "ecological":
        file_path = UPLOAD_DIR1 / filename
    else:
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

@app.get("/check-pdf/{year}/{project_name}/{pdf_type}")
def check_pdf_exists(year: int, project_name: str, pdf_type: str):
    """
    檢查PDF檔案是否存在
    """
    if pdf_type not in ['ecological', 'carbon']:
        raise HTTPException(status_code=400, detail="無效的PDF類型")
    
    pdf_type_name = "生態檢核" if pdf_type == "ecological" else "碳排計算"
    filename = f"{year}-{project_name}_{pdf_type_name}.pdf"
    file_path = UPLOAD_DIR / filename
    
    return {
        "exists": file_path.exists(),
        "filename": filename if file_path.exists() else None
    }
