
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.api.deps import  SessionDep
from app.models import UnitSystemCreate, UnitSystemRead, UnitSystemUpdate ,PhysicalQuantity  , UnitSystem , Unit ,  LinearUnit , FunctionalUnit

router = APIRouter(prefix="/unitsystems", tags=["UnitSystems"])
# ==================================================


# Create a new unit system
@router.post("/", response_model=UnitSystemRead)
def create_unit_system(data: UnitSystemCreate, session: SessionDep):
    # Get all linear units and functional units

    unit_system = UnitSystem(
        name=data.name,
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
        is_deleted=False
    )

    # Create PhysicalQuantities from input and attach all units
    unit_system.physical_quantities = [
        PhysicalQuantity(
            quantity=pq.quantity,
            value=pq.value,
            unit_system_id=unit_system.id,  # This will be set after commit
        )
        for pq in data.physical_quantities
    ]
    session.add(unit_system)
    session.commit()
    session.refresh(unit_system)
    return unit_system


# ==================================================


# Read all unit systems or a specific one by ID
@router.get("/", response_model=list[UnitSystemRead])
def read_all_unit_systems(session: SessionDep):
    statement = select(UnitSystem).where(UnitSystem.is_deleted == False)
    return session.exec(statement).all()


# ==================================================

# Reading a specific unit system by ID, updating it, and soft deleting it
@router.get("/{unitsystem_id}", response_model=UnitSystemRead)
def read_unit_system(unitsystem_id: UUID, session: SessionDep):
    unit = session.get(UnitSystem, unitsystem_id)
    if not unit or unit.is_deleted:
        raise HTTPException(status_code=404, detail="UnitSystem not found")
    return unit

@router.patch("/{unitsystem_id}", response_model=UnitSystemRead)
def update_unit_system(unitsystem_id: UUID, data: UnitSystemUpdate, session: SessionDep):
    unit = session.get(UnitSystem, unitsystem_id)
    if not unit or unit.is_deleted:
        raise HTTPException(status_code=404, detail="UnitSystem not found")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(unit, key, value)
    
    unit.updatedAt = datetime.now(timezone.utc)
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return unit

@router.delete("/{unitsystem_id}")
def soft_delete_unit_system(unitsystem_id: UUID, session: SessionDep):
    unit = session.get(UnitSystem, unitsystem_id)
    if not unit or unit.is_deleted:
        raise HTTPException(status_code=404, detail="UnitSystem not found")

    unit.is_deleted = True
    unit.deleted_at = datetime.now(timezone.utc)
    session.add(unit)
    session.commit()
    return {"message": "UnitSystem soft deleted"}


@router.delete("/{unitsystem_id}")
def soft_delete_unit_system(unitsystem_id: UUID, session: SessionDep):
    unit = session.get(UnitSystem, unitsystem_id)
    if not unit or unit.is_deleted:
        raise HTTPException(status_code=404, detail="UnitSystem not found")

    unit.is_deleted = True
    unit.deleted_at = datetime.now(timezone.utc)
    session.add(unit)
    session.commit()
    return {"message": "UnitSystem soft deleted"}


@router.post("/{unitsystem_id}/physical_quantities", response_model=UnitSystemRead)
def add_physical_quantity(unitsystem_id: UUID, pq: PhysicalQuantity.Create, session: SessionDep):
    unit_system = session.get(UnitSystem, unitsystem_id)
    if not unit_system or unit_system.is_deleted:
        raise HTTPException(status_code=404, detail="UnitSystem not found")
        # Create a new PhysicalQuantity and associate it with the UnitSystem
    new_pq = PhysicalQuantity(
        quantity=pq.quantity,
        value=pq.value,
        unit_system_id=unit_system.id,
    )
    session.add(new_pq)
    unit_system.physical_quantities.append(new_pq)
    session.commit()
    session.refresh(unit_system)
    return unit_system

@router.delete("/{unitsystem_id}/physical_quantities/{pq_id}", response_model=UnitSystemRead)
def remove_physical_quantity(unitsystem_id: UUID, pq_id: int, session: SessionDep):
    unit_system = session.get(UnitSystem, unitsystem_id)
    if not unit_system or unit_system.is_deleted:
        raise HTTPException(status_code=404, detail="UnitSystem not found")
    pq = session.get(PhysicalQuantity, pq_id)
    if not pq or pq.unit_system_id != unitsystem_id:
        raise HTTPException(status_code=404, detail="PhysicalQuantity not found in this UnitSystem")
    session.delete(pq)
    session.commit()
    session.refresh(unit_system)
    return unit_system


