from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ProjectBase(BaseModel):
    project_name: str
    project_number: str
    approved_amount: int
    branch_office: Optional[str] = None
    funding_source: Optional[str] = None
    total_budget: Optional[int] = None
    contract_amount: Optional[int] = None
    duration: Optional[int] = None
    construction_content: Optional[str] = None
    location: Optional[str] = None
    supervisor: Optional[str] = None
    supervisor_personnel: Optional[str] = None
    outsourcing_items: Optional[str] = None
    year: Optional[int] = None
    schedule_type: Optional[str] = None
    bid_bond: Optional[int] = None
    performance_bond: Optional[int] = None
    outsourcing_company: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdateStatus(BaseModel):
    status: str

class ProjectUpdateBond(BaseModel):
    id: int
    bid_bond: Optional[int] = None
    performance_bond: Optional[int] = None

class ProjectUpdate(ProjectBase):
    status: str

class Project(ProjectBase):
    id: int
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

# ----------------------------------------

# class UserBase(BaseModel):
#     user_id: str
#     user_name: str
#     nick_name: str
#     pic_url: str
#     role: str = "user"

# class UserCreate(UserBase):
#     pass

# class UserUpdate(UserBase):
#     user_id: Optional[str] = None
#     user_name: Optional[str] = None
#     nick_name: Optional[str] = None
#     pic_url: Optional[str] = None
#     role: Optional[str] = None
#     reviewed: Optional[int] = None

# class User(UserBase):
#     id: int
#     created_time: datetime
#     reviewed: int

#     class Config:
#         from_attributes = True

# ----------------------------------------
        
class Plan(BaseModel):
    plan_name: str
    plan_code: Optional[str]= None
    description: Optional[str] = None
    projects: List[ProjectBase] #= []

# class PlanCreate(Plan):
#     projects: List[ProjectBase] = []