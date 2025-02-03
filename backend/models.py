from sqlalchemy import Column, Integer, String, Float,DateTime
from sqlalchemy.sql import func
from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    branch_office = Column(String(50))
    project_name = Column(String(50))
    project_number = Column(String(20), unique=True, index=True)
    funding_source = Column(String(50))
    approved_amount = Column(Integer)
    total_budget = Column(Integer)
    contract_amount = Column(Integer)
    duration = Column(Integer)
    construction_content = Column(String(255))
    location = Column(String(20))
    supervisor = Column(String(10))
    supervisor_personnel = Column(String(10))
    outsourcing_items = Column(String(100))
    # procurement_type = Column(SQLAlchemyEnum(ProcurementType))
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(10),default="初稿") # Column(SQLAlchemyEnum(ProjectStatus), default=ProjectStatus.PENDING)
    schedule_type = Column(String(10), default="一般流程")
    bid_bond= Column(Integer, default=0)
    performance_bond= Column(Integer, default=0)
    outsourcing_company= Column(String(50), default="無")

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