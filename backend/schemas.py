from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import  ProjectStatus

class ProjectBase(BaseModel):
    branch_office: str
    project_name: str
    project_number: str
    funding_source: str
    approved_amount: int
    total_budget: int
    contract_amount: int
    duration: int
    construction_content: str
    location: str
    supervisor: str
    supervisor_personnel: str
    outsourcing_items: str
    # procurement_type: ProcurementType
    year: int
    schedule_type:str
    bid_bond: Optional[int] = None
    performance_bond: Optional[int] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdateBond(BaseModel):
    id: int
    bid_bond: Optional[int] = None
    performance_bond: Optional[int] = None

class ProjectUpdate(ProjectBase):
    status: Optional[ProjectStatus] = None

class Project(ProjectBase):
    id: int
    created_at: datetime
    status: ProjectStatus

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    user_id: str
    user_name: str
    nick_name: str
    pic_url: str
    role: str = "user"

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    nick_name: Optional[str] = None
    pic_url: Optional[str] = None
    role: Optional[str] = None
    reviewed: Optional[int] = None

class User(UserBase):
    id: int
    created_time: datetime
    reviewed: int

    class Config:
        from_attributes = True
