
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.api.deps import  SessionDep
from app.models import TestTemplateGeneralInfo , TestTemplateCondition , TestTemplateReading , TestTemplate
from fastapi import status
from typing import List

router = APIRouter(prefix="/template_tests", tags=["Template Tests"])




@router.get("/", response_model=List[TestTemplate.Read])
def get_all_template_tests(session: SessionDep):
    templates = session.exec(
        select(TestTemplate).where(TestTemplate.is_deleted == False)
    ).all()
    return templates





@router.post("/")
def create_template_test(
    data: TestTemplate.Create,
    session: SessionDep):
    template = TestTemplate(
        name=data.name,
        tags=data.tags,
        isVLCompatible=data.isVLCompatible,
        version=data.version,
        isLastVersion=data.isLastVersion, 
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
        is_deleted=False
    )

    session.add(template)
    session.commit()
    session.refresh(template)
    return template
@router.put("/{template_id}", response_model=TestTemplate.Update)
def update_template_test(
    template_id: UUID,
    template_in: TestTemplate.Update,
    session: SessionDep,
):
    template = session.get(TestTemplate, template_id)
    if not template or template.is_deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    for field, value in template_in.dict(exclude_unset=True).items():
        setattr(template, field, value)
    session.add(template)
    session.commit()
    session.refresh(template)
    return template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template_test(
    template_id: UUID,
    session: SessionDep,
):
    template = session.get(TestTemplate, template_id)
    if not template or template.is_deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    template.is_deleted = True
    template.deleted_at = datetime.now(timezone.utc)
    session.add(template)
    session.commit()

@router.post("/{template_id}/general_info", response_model=TestTemplateGeneralInfo)
def add_general_info(
    template_id: UUID,
    general_info_in: TestTemplateGeneralInfo.Create,
    session: SessionDep,
):
    template = session.get(TestTemplate, template_id)
    if not template or template.is_deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    general_info = TestTemplateGeneralInfo(**general_info_in.model_dump(), template_id=template_id)
    template.generalInfo = general_info
    session.add(general_info)
    session.commit()
    session.refresh(general_info)
    return general_info

@router.get("/{template_id}/general_info", response_model=TestTemplateGeneralInfo)
def get_general_info(
    template_id: UUID,
    session: SessionDep,
):
    general_info = session.exec(
        select(TestTemplateGeneralInfo).where(TestTemplateGeneralInfo.test_template_id == template_id)
    ).first()
    if not general_info:
        raise HTTPException(status_code=404, detail="General info not found")
    return general_info

@router.put("/{template_id}/general_info", response_model=TestTemplateGeneralInfo)
def update_general_info(
    template_id: UUID,
    general_info_in: TestTemplateGeneralInfo.Create,
    session: SessionDep,
):
    template = session.get(TestTemplate, template_id)
    if not template or template.is_deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    general_info = session.exec(
        select(TestTemplateGeneralInfo).where(TestTemplateGeneralInfo.template_id == template_id)
    ).first()
    if not general_info:
        raise HTTPException(status_code=404, detail="General info not found")
    for field, value in general_info_in.dict(exclude_unset=True).items():
        setattr(general_info, field, value)
    session.add(general_info)
    session.commit()
    session.refresh(general_info)
    return general_info

# --- Real Condition Endpoints ---

@router.post("/{template_id}/conditions", response_model=TestTemplateCondition)
def add_condition(
    template_id: UUID,
    condition_in: TestTemplateCondition.Create,
    session: SessionDep,
):
    template = session.get(TestTemplate, template_id)
    if not template or template.is_deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    condition = TestTemplateCondition(**condition_in.model_dump(), template_id=template_id)
    template.conditions.append(condition)
    session.add(condition)
    session.commit()
    session.refresh(condition)
    return condition

@router.get("/{template_id}/conditions", response_model=List[TestTemplateCondition])
def get_conditions(
    template_id: UUID,
    session: SessionDep,
):
    conditions = session.exec(
        select(TestTemplateCondition).where(TestTemplateCondition.test_template_id == template_id)
    ).all()
    return conditions

@router.put("/{template_id}/conditions/{condition_id}", response_model=TestTemplateCondition)
def update_condition(
    template_id: UUID ,
    condition_id: UUID,
    condition_in: TestTemplateCondition.Create,
    session: SessionDep,
):
    template = session.get(TestTemplate, template_id)
    if not template or template.is_deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    condition = session.get(TestTemplateCondition, condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Condition not found")
    for field, value in condition_in.dict(exclude_unset=True).items():
        setattr(condition, field, value)
    session.add(condition)
    session.commit()
    session.refresh(condition)
    return condition

@router.delete("/conditions/{condition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_condition(
    condition_id: UUID,
    session: SessionDep,
):
    condition = session.get(TestTemplateCondition, condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Condition not found")
    session.delete(condition)
    session.commit()

# --- Reading Endpoints ---

@router.post("/{template_id}/readings", response_model=TestTemplateReading)
def add_reading(
    template_id: UUID,
    reading_in: TestTemplateReading.Create,
    session: SessionDep,
):
    template = session.get(TestTemplate, template_id)
    if not template or template.is_deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    reading = TestTemplateReading(**reading_in.model_dump(), template_id=template_id)
    template.readings.append(reading)
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading

@router.get("/{template_id}/readings", response_model=List[TestTemplateReading])
def get_readings(
    template_id: UUID,
    session: SessionDep,
):
    readings = session.exec(
        select(TestTemplateReading).where(TestTemplateReading.test_template_id == template_id)
    ).all()
    return readings

@router.put("/{template_id}/readings/{reading_id}", response_model=TestTemplateReading)
def update_reading(
    template_id: UUID ,
    reading_id: UUID,
    reading_in: TestTemplateReading.Create,
    session: SessionDep,
):
    template = session.get(TestTemplate, template_id)
    if not template or template.is_deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    reading = session.get(TestTemplateReading, reading_id)
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    for field, value in reading_in.dict(exclude_unset=True).items():
        setattr(reading, field, value)
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading

@router.delete("/readings/{reading_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reading(
    reading_id: UUID,
    session: SessionDep,
):
    reading = session.get(TestTemplateReading, reading_id)
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    session.delete(reading)
    session.commit()
