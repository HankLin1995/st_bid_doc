from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import ProcurementType, ProjectStatus

class ProjectBase(BaseModel):
    branch_office: str
    project_name: str
    project_number: str
    funding_source: str
    approved_amount: float
    total_budget: float
    contract_amount: float
    duration: int
    construction_content: str
    location: str
    supervisor: str
    supervisor_personnel: str
    outsourcing_items: str
    procurement_type: ProcurementType
    year: int

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    status: Optional[ProjectStatus] = None

class Project(ProjectBase):
    id: int
    created_at: datetime
    status: ProjectStatus

    class Config:
        from_attributes = True
