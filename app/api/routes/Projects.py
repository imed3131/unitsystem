
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.api.deps import  SessionDep
from app.models import Project, ProjectAttachment, ProjectMetaData, ProjectRule, ProjectObjective, ProjectDeliverable, ProjectConstraint , ProjectBase ,UpdateProject



router = APIRouter(prefix="/projects", tags=["Projects"])   

@router.post("/", response_model=Project)
def create_project(project: ProjectBase, session: SessionDep):
    db_project = Project(**project.model_dump())
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

@router.get("/", response_model=list[Project])
def read_projects(session: SessionDep):
    projects = session.exec(select(Project).where(Project.is_deleted == False)).all()
    return projects

@router.get("/{project_id}", response_model=Project)
def read_project(project_id: UUID, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=Project)
def update_project(project_id: UUID, project_update: UpdateProject, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project_data = project_update.dict(exclude_unset=True)
    for key, value in project_data.items():
        setattr(project, key, value)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: UUID, session: SessionDep):
    project = session.get(Project, project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    project.is_deleted = True
    project.deleted_at = datetime.now(timezone.utc)
    session.add(project)
    session.commit()
    return {"deleted": True}

@router.get("/{project_id}/metadata/", response_model=list[ProjectMetaData])
def get_project_metadata(project_id: UUID, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not hasattr(project, "project_metadata") or project.project_metadata is None:
        raise HTTPException(status_code=404, detail="Project metadata not found")
    return project.project_metadata

@router.get("/{project_id}/rules/", response_model=list[ProjectRule])
def get_project_rules(project_id: UUID, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not hasattr(project, "project_rules") or project.project_rules is None:
        raise HTTPException(status_code=404, detail="Project rules not found")
    return project.project_rules

@router.get("/{project_id}/objectives/", response_model=list[ProjectObjective])
def get_project_objectives(project_id: UUID, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not hasattr(project, "project_objectives") or project.project_objectives is None:
        raise HTTPException(status_code=404, detail="Project objectives not found")
    return project.project_objectives

@router.get("/{project_id}/deliverables/", response_model=list[ProjectDeliverable])
def get_project_deliverables(project_id: UUID, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not hasattr(project, "project_deliverables") or project.project_deliverables is None:
        raise HTTPException(status_code=404, detail="Project deliverables not found")
    return project.project_deliverables

@router.get("/{project_id}/constraints/", response_model=list[ProjectConstraint])
def get_project_constraints(project_id: UUID, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not hasattr(project, "project_constraints") or project.project_constraints is None:
        raise HTTPException(status_code=404, detail="Project constraints not found")
    return project.project_constraints

@router.get("/{project_id}/attachments/", response_model=list[ProjectAttachment])
def get_project_attachments(project_id: UUID, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not hasattr(project, "project_attachments") or project.project_attachments is None:
        raise HTTPException(status_code=404, detail="Project attachments not found")
    return project.project_attachments

@router.post("/{project_id}/metadata/", response_model=ProjectMetaData)
def create_project_metadata(project_id: UUID, metadata: ProjectMetaData.Create, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_metadata = ProjectMetaData(**metadata.model_dump(), project_id=project_id)
    session.add(db_metadata)
    session.commit()
    session.refresh(db_metadata)
    return db_metadata

@router.post("/{project_id}/rules/", response_model=ProjectRule)
def create_project_rule(project_id: UUID, rule: ProjectRule.Create, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_rule = ProjectRule(**rule.model_dump(), project_id=project_id)
    session.add(db_rule)
    session.commit()
    session.refresh(db_rule)
    return db_rule

@router.post("/{project_id}/objectives/", response_model=ProjectObjective)
def create_project_objective(project_id: UUID, objective: ProjectObjective.Create, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_objective = ProjectObjective(**objective.model_dump(), project_id=project_id)
    session.add(db_objective)
    session.commit()
    session.refresh(db_objective)
    return db_objective

@router.post("/{project_id}/deliverables/", response_model=ProjectDeliverable)
def create_project_deliverable(project_id: UUID, deliverable: ProjectDeliverable.Create, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_deliverable = ProjectDeliverable(**deliverable.model_dump(), project_id=project_id)
    session.add(db_deliverable)
    session.commit()
    session.refresh(db_deliverable)
    return db_deliverable

@router.post("/{project_id}/constraints/", response_model=ProjectConstraint)
def create_project_constraint(project_id: UUID, constraint: ProjectConstraint.Create, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_constraint = ProjectConstraint(**constraint.model_dump(), project_id=project_id)
    session.add(db_constraint)
    session.commit()
    session.refresh(db_constraint)
    return db_constraint

@router.post("/{project_id}/attachments/", response_model=ProjectAttachment)
def create_project_attachment(project_id: UUID, attachment: ProjectAttachment.Create, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_attachment = ProjectAttachment(**attachment.model_dump(), project_id=project_id)
    session.add(db_attachment)
    session.commit()
    session.refresh(db_attachment)
    return db_attachment
@router.delete("/metadata/{metadata_id}", response_model=dict)
def delete_project_metadata( metadata_id: UUID, session: SessionDep):
    metadata = session.get(ProjectMetaData, metadata_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Project metadata not found")
    session.delete(metadata)
    session.commit()
    return {"deleted": True}

@router.delete("/rules/{rule_id}", response_model=dict)
def delete_project_rule(rule_id: UUID, session: SessionDep):
    rule = session.get(ProjectRule, rule_id)
    if not rule :
        raise HTTPException(status_code=404, detail="Rule not found")
    session.delete(rule)
    session.commit()
    return {"deleted": True}

@router.delete("/objectives/{objective_id}", response_model=dict)
def delete_project_objective(objective_id: UUID, session: SessionDep):
    objective = session.get(ProjectObjective, objective_id)
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    session.delete(objective)
    session.commit()
    return {"deleted": True}

@router.delete("deliverables/{deliverable_id}", response_model=dict)
def delete_project_deliverable(deliverable_id: UUID, session: SessionDep):
    deliverable = session.get(ProjectDeliverable, deliverable_id)
    if not deliverable :
        raise HTTPException(status_code=404, detail="Deliverable not found")
    session.delete(deliverable)
    session.commit()
    return {"deleted": True}

@router.delete("/constraints/{constraint_id}", response_model=dict)
def delete_project_constraint(constraint_id: UUID, session: SessionDep):
    constraint = session.get(ProjectConstraint, constraint_id)
    if not constraint:
        raise HTTPException(status_code=404, detail="Constraint not found")
    session.delete(constraint)
    session.commit()
    return {"deleted": True}

@router.delete("/attachments/{attachment_id}", response_model=dict)
def delete_project_attachment( attachment_id: UUID, session: SessionDep):
    attachment = session.get(ProjectAttachment, attachment_id)
    if not attachment :
        raise HTTPException(status_code=404, detail="Attachment not found")
    session.delete(attachment)
    session.commit()
    return {"deleted": True}