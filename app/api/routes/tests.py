
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.api.deps import  SessionDep
from app.models import Test , VLReading, Reading, RealCondition , TestCreate, TestUpdate
from fastapi import status
from typing import List

router = APIRouter(prefix="/test", tags=["Tests"])

@router.post("/", response_model=Test)
def create_test(test: TestCreate, session: SessionDep):
    db_test = Test(**test.model_dump())
    db_test.createdAt = datetime.now(timezone.utc)
    db_test.updatedAt = datetime.now(timezone.utc)
    db_test.is_deleted = False
    session.add(db_test)
    session.commit()
    session.refresh(db_test)
    return db_test
@router.put("/{test_id}", response_model=Test)
def update_test(test_id: UUID, test_update: TestUpdate, session: SessionDep):
    test = session.get(Test, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    for key, value in test_update.model_dump(exclude_unset=True).items():
        setattr(test, key, value)
    test.updatedAt = datetime.now(timezone.utc)
    session.add(test)
    session.commit()
    session.refresh(test)
    return test
@router.get("/{test_id}", response_model=Test)
def get_test(test_id: UUID, session: SessionDep):
    test = session.get(Test, test_id)
    if not test or test.is_deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@router.delete("/{test_id}")
def delete_test(test_id: UUID, session: SessionDep):
    test = session.get(Test, test_id)
    if not test or test.is_deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    test.is_deleted = True
    test.deleted_at= datetime.now(timezone.utc)
    session.add(test)
    session.commit()
    session.refresh(test)
    return {"deleted": True}
@router.get("/", response_model=list[Test])
def get_all_tests(session: SessionDep):
    tests = session.exec(select(Test).where(Test.is_deleted==False)).all()
    return tests
@router.get("/{test_id}/vlreadings", response_model=List[VLReading])
def get_vlreadings(test_id: UUID, session: SessionDep):
    test = session.get(Test, test_id)
    if not test or test.is_deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    return test.vlReadings

@router.get("/{test_id}/readings", response_model=List[Reading])
def get_readings(test_id: UUID, session: SessionDep):
    test = session.get(Test, test_id)
    if not test or test.is_deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    return test.readings

@router.get("/{test_id}/realconditions", response_model=List[RealCondition])
def get_realconditions(test_id: UUID, session: SessionDep):
    test = session.get(Test, test_id)
    if not test or test.is_deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    return test.realConditions
@router.delete("/vlreading/{vlreading_id}")
def delete_vlreading(vlreading_id: UUID, session: SessionDep):
    vlreading = session.get(VLReading, vlreading_id)
    if not vlreading :
        raise HTTPException(status_code=404, detail="VLReading not found")
    session.delete(vlreading)
    session.commit()
    return {"deleted": True}

@router.delete("/reading/{reading_id}")
def delete_reading(reading_id: UUID, session: SessionDep):
    reading = session.get(Reading, reading_id)
    if not reading :
        raise HTTPException(status_code=404, detail="Reading not found")
    session.delete(reading)
    session.commit()
    return {"deleted": True}

@router.delete("/realcondition/{realcondition_id}")
def delete_realcondition(realcondition_id: UUID, session: SessionDep):
    realcondition = session.get(RealCondition, realcondition_id)
    if not realcondition:
        raise HTTPException(status_code=404, detail="RealCondition not found")
    session.delete(realcondition)
    session.commit()
    return {"deleted": True}
@router.post("/{test_id}/vlreading", response_model=VLReading.Create, status_code=status.HTTP_201_CREATED)
def create_vlreading(test_id: UUID, vlreading: VLReading.Create, session: SessionDep):
    test = session.get(Test, test_id)
    if not test or test.is_deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    db_vlreading = VLReading(**vlreading.model_dump(), test_id=test.id)
    session.add(db_vlreading)
    session.commit()
    session.refresh(db_vlreading)
    return db_vlreading

@router.post("/{test_id}/reading", response_model=Reading.Create, status_code=status.HTTP_201_CREATED)
def create_reading(test_id: UUID, reading: Reading.Create, session: SessionDep):
    test = session.get(Test, test_id)
    if not test or test.is_deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    db_reading =Reading(**reading.model_dump(), tes_id=test.id)
    session.add(db_reading)
    session.commit()
    session.refresh(db_reading)
    return db_reading

@router.post("/{test_id}/realcondition", response_model=RealCondition.Create, status_code=status.HTTP_201_CREATED)
def create_realcondition(test_id: UUID, realcondition: RealCondition.Create, session: SessionDep):
    test = session.get(Test, test_id)
    if not test or test.is_deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    db_realcondition = RealCondition(**realcondition.model_dump(), test_id=test.id)
    session.add(db_realcondition)
    session.commit()
    session.refresh(db_realcondition)
    return db_realcondition
