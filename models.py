from sqlalchemy import create_engine, Column, Integer, String, Float, Enum, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

Base = declarative_base()

class ProjectType(enum.Enum):
    GENERAL = "一般"
    OPEN = "開口"

class ProcurementType(enum.Enum):
    ENGINEERING = "工程"
    SERVICE = "勞務"
    GOODS = "財務"

class ProjectStatus(enum.Enum):
    SURVEY = "測設"
    DRAFT = "初稿"
    BUDGET = "預算書"
    ANNOUNCEMENT = "公告"
    BID_RESULT = "決標"
    FAILED_BID = "流標"
    START = "開工"

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    project_type = Column(Enum(ProjectType), nullable=False)
    branch_office = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    project_number = Column(String, nullable=False, unique=True)
    funding_source = Column(String, nullable=False)
    approved_amount = Column(Float)
    total_budget = Column(Float)
    contract_amount = Column(Float)
    duration = Column(Integer)  # 工期(天數)
    construction_content = Column(String)
    location = Column(String)
    supervisor = Column(String)
    supervisor_personnel = Column(String)
    procurement_type = Column(Enum(ProcurementType))
    outsourcing_items = Column(String)  # 可能有多個項目，用逗號分隔
    procurement_tier = Column(String)
    bid_bond = Column(Float)
    performance_bond = Column(Float)
    contractor_qualifications = Column(String)
    status = Column(Enum(ProjectStatus))

# 資料庫連接
engine = create_engine('sqlite:///projects.db')
Base.metadata.create_all(engine)

# 建立Session類別
Session = sessionmaker(bind=engine)

def get_db_session():
    return Session()
