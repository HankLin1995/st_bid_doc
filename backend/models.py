from sqlalchemy import Column, Integer, String, Float,DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
import enum

# class ProcurementType(str, enum.Enum):
#     ENGINEERING = "工程"
#     PURCHASE = "購案"
#     SERVICE = "勞務"

class ProjectStatus(str, enum.Enum):
    # 初稿、預算書
    PENDING = "初稿"
    REVIEWING = "預算書"
    APPROVED = "上網"
    REJECTED = "決標"

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    branch_office = Column(String(50))
    project_name = Column(String(50))
    project_number = Column(String(20), unique=True, index=True)
    funding_source = Column(String(50))
    approved_amount = Column(Float)
    total_budget = Column(Float)
    contract_amount = Column(Float)
    duration = Column(Integer)
    construction_content = Column(String(255))
    location = Column(String(20))
    supervisor = Column(String(10))
    supervisor_personnel = Column(String(10))
    outsourcing_items = Column(String(100))
    # procurement_type = Column(SQLAlchemyEnum(ProcurementType))
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(SQLAlchemyEnum(ProjectStatus), default=ProjectStatus.PENDING)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True)  
    user_name= Column(String(100))
    nick_name= Column(String(100))
    pic_url= Column(String(255))
    created_time = Column(DateTime(timezone=True), server_default=func.now())
    reviewed = Column(Integer, default=0)
    role = Column(String(20), default="user")