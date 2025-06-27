
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.api.deps import  SessionDep
from app.models import UnitSystemCreate, UnitSystemRead, UnitSystemUpdate ,PhysicalQuantity  , UnitSystem , Unit ,  LinearUnit , FunctionalUnit
import os 
import yaml
router = APIRouter(prefix="/unitsystems", tags=["UnitSystems"])
# ==================================================


# Create a new unit system
@router.post("/")
def create_unit_system(data: UnitSystemCreate, session: SessionDep):
    # Get all linear units and functional units

    unit_system = UnitSystem(
        name=data.name,
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
        is_deleted=False
    )
    unit_system.physical_quantities = []

    for pq in data.physical_quantities:
        # Search for the unit by type and unit_id
        if pq.type == "linear":
            unit = session.get(LinearUnit, pq.unit_id)
        elif pq.type == "functional":
            unit = session.get(FunctionalUnit, pq.unit_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown unit type: {pq.type}")

        if not unit:
            raise HTTPException(status_code=404, detail=f"Unit not found for id {pq.unit_id} and type {pq.type}")
            # Create the PhysicalQuantity with the correct unit reference
        if pq.type == "linear":
            physical_quantity = PhysicalQuantity(
            quantity=pq.quantity,
            value=pq.value,
            type=pq.type,
            linear_unit_id=pq.unit_id
            )
        elif pq.type == "functional":
            physical_quantity = PhysicalQuantity(
            quantity=pq.quantity,
            value=pq.value,
            type=pq.type,
            functional_unit_id=pq.unit_id
            )
        unit_system.physical_quantities.append(physical_quantity)
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

@router.get("/units/")
def get_all_units(session: SessionDep):
    linear_units = session.exec(select(LinearUnit).where(LinearUnit.is_deleted == False)).all()
    functional_units = session.exec(select(FunctionalUnit).where(FunctionalUnit.is_deleted == False)).all()
    return {
        "linear_units": [{"id": u.id, "name": u.name, "type": "linear"} for u in linear_units],
        "functional_units": [{"id": u.id, "name": u.name, "type": "functional"} for u in functional_units]
    }
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


@router.post("/{unitsystem_id}/physical_quantities")
def add_physical_quantity(unitsystem_id: UUID, pq: PhysicalQuantity.Create, session: SessionDep):
    unit_system = session.get(UnitSystem, unitsystem_id)

    if pq.type == "linear":
        unit = session.get(LinearUnit, pq.unit_id)
    elif pq.type == "functional":
        unit = session.get(FunctionalUnit, pq.unit_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown unit type: {pq.type}")

    if not unit:
        raise HTTPException(status_code=404, detail=f"Unit not found for id {pq.unit_id} and type {pq.type}")


    if not unit_system or unit_system.is_deleted:
        raise HTTPException(status_code=404, detail="UnitSystem not found")
        # Create a new PhysicalQuantity and associate it with the UnitSystem
    if not pq.type or pq.type not in ["linear", "functional"]:
        raise HTTPException(status_code=400, detail="Type is required for PhysicalQuantity")
    if pq.type == "linear":
        new_pq = PhysicalQuantity(
            quantity=pq.quantity,
            value=pq.value,
            unit_system_id=unit_system.id,
            type=pq.type,
            linear_unit_id=pq.unit_id
        )
    elif pq.type == "functional":
        new_pq = PhysicalQuantity(
            quantity=pq.quantity,
            value=pq.value,
            unit_system_id=unit_system.id,
            type=pq.type,
            functional_unit_id=pq.unit_id
        )
    else:
        raise HTTPException(status_code=400, detail="Unknown unit type")
    session.add(new_pq)
    unit_system.physical_quantities.append(new_pq)
    session.commit()
    session.refresh(unit_system)
    return unit_system

@router.delete("/{unitsystem_id}/physical_quantities/{pq_id}", response_model=UnitSystemRead)
def remove_physical_quantity(unitsystem_id: UUID, pq_id: UUID, session: SessionDep):
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


@router.post("/addunits")
def add_physical_quantity_to_unit_system(session: SessionDep):
    # Get path to config directory
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config")
    units_yaml_path = os.path.join(config_dir, "units.yaml")
    if not os.path.exists(units_yaml_path):
        raise HTTPException(status_code=404, detail="Units configuration file not found")

    with open(units_yaml_path, "r") as file:
        data = yaml.safe_load(file)

    units = data.get("units", [])
    created_units = []
    for unit in units:
        # Check for existing unit by name and type
        if unit["type"] == "linear":
            exists = session.exec(
                select(LinearUnit).where(LinearUnit.name == unit["name"])
            ).first()
            if exists:
                continue
            new_unit = LinearUnit(
                name=unit["name"],
                base=unit["base"],
                factorToBase=unit["factorToBase"]
            )
        elif unit["type"] == "functional":
            exists = session.exec(
                select(FunctionalUnit).where(FunctionalUnit.name == unit["name"])
            ).first()
            if exists:
                continue
            new_unit = FunctionalUnit(
                name=unit["name"],
                base=unit["base"],
                toBase=unit["toBase"],
                fromBase=unit["fromBase"]
            )
        else:
            continue
        session.add(new_unit)
        created_units.append(new_unit)
    session.commit()
    return {"message": f"{len(created_units)} units added", "units": [u.name for u in created_units]}