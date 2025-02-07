from sqlalchemy.orm import Session
import models, schemas

def get_plan(db: Session, plan_id: int):
    return db.query(models.Plan).filter(models.Plan.id == plan_id).first()

def get_plans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Plan).offset(skip).limit(limit).all()

def create_plan(db: Session, plan: schemas.Plan):
    db_plan = models.Plan(
        plan_name=plan.plan_name,
        plan_code=plan.plan_code,
        description=plan.description
    )
    db.add(db_plan)
    db.flush()

    for project in plan.projects:
        db_project = models.Project(
            project_name=project.project_name,
            project_number=project.project_number,
            approved_amount=project.approved_amount,
            plan_id=db_plan.id
        )
        db.add(db_project)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, plan_id: int):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if db_plan:
        db.delete(db_plan)
        db.commit()
        return True
    return False
