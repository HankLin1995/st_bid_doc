from sqlalchemy import Column, Integer, String, Float, Date,DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
import enum

class ProcurementType(str, enum.Enum):
    ENGINEERING = "工程"
    PURCHASE = "購案"
    SERVICE = "勞務"

class ProjectStatus(str, enum.Enum):
    PENDING = "待審查"
    REVIEWING = "審查中"
    APPROVED = "已核定"
    REJECTED = "已退回"

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
    procurement_type = Column(SQLAlchemyEnum(ProcurementType))
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(SQLAlchemyEnum(ProjectStatus), default=ProjectStatus.PENDING)
