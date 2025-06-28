
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




@router.get("/physicalquantities", response_model=list[PhysicalQuantity.Read])
def get_all_physical_quantities(session: SessionDep):
    statement = select(PhysicalQuantity)
    return session.exec(statement).all()


# ==================================================

# Reading a specific unit system by ID, updating it, and soft deleting it
@router.get("/{unitsystem_id}", response_model=UnitSystemRead)
def read_unit_system(unitsystem_id: UUID, session: SessionDep):
    unit = session.get(UnitSystem, unitsystem_id)
    if not unit or unit.is_deleted:
        raise HTTPException(status_code=404, detail="UnitSystem not found")
    unitread = UnitSystemRead(
        id=unit.id,
        name=unit.name,
        createdAt=unit.createdAt,
        updatedAt=unit.updatedAt,
        is_deleted=unit.is_deleted,
        deleted_at=unit.deleted_at,
        physical_quantities=session.exec(
            select(PhysicalQuantity)
        ).all())
    return unitread

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
    unitread = UnitSystemRead(
    id=unit.id,
    name=unit.name,
    createdAt=unit.createdAt,
    updatedAt=unit.updatedAt,
    is_deleted=unit.is_deleted,
    deleted_at=unit.deleted_at,
    physical_quantities=session.exec(
        select(PhysicalQuantity)
    ).all())
    return unitread

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



@router.delete("/physicalquantities/{pq_id}", status_code=204)
def delete_physical_quantity(pq_id: UUID, session: SessionDep):
    pq = session.get(PhysicalQuantity, pq_id)
    if not pq:
        raise HTTPException(status_code=404, detail="PhysicalQuantity not found")
    session.delete(pq)
    session.commit()

@router.patch("/physicalquantities/{pq_id}", response_model=PhysicalQuantity.Read)
def update_physical_quantity(pq_id: UUID, data: PhysicalQuantity.Create, session: SessionDep):
    pq = session.get(PhysicalQuantity, pq_id)
    if not pq:
        raise HTTPException(status_code=404, detail="PhysicalQuantity not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(pq, key, value)
    session.add(pq)
    session.commit()
    session.refresh(pq)
    return pq

@router.post("/physicalquantities/{pq_id}/addlinearunit", response_model=LinearUnit.Create)
def add_linear_unit_to_physical_quantity(
    pq_id: UUID,
    unit_data: LinearUnit.Create,
    session: SessionDep
):
    pq = session.get(PhysicalQuantity, pq_id)
    if not pq:
        raise HTTPException(status_code=404, detail="PhysicalQuantity not found")
    unit = LinearUnit(
        name=unit_data.name,
        value=unit_data.value,
        base = unit_data.base , 
        factorToBase=unit_data.factorToBase,
    )
    session.add(unit)
    session.commit()
    session.refresh(unit)

    pq.linear_units.append(unit)
    session.add(pq)
    session.commit()
    session.refresh(pq)
    return unit 

@router.post("/physicalquantities/{pq_id}/addfunctionalunit", response_model=FunctionalUnit.Create)
def add_functional_unit_to_physical_quantity(
    pq_id: UUID,
    unit_data: FunctionalUnit.Create,
    session: SessionDep
):
    pq = session.get(PhysicalQuantity, pq_id)
    if not pq:
        raise HTTPException(status_code=404, detail="PhysicalQuantity not found")
    unit = FunctionalUnit(
        name=unit_data.name,
        value=unit_data.value,
        base = unit_data.base , 
        toBase=unit_data.toBase,
        fromBase=unit_data.fromBase,
    )
    session.add(unit)
    session.commit()
    session.refresh(unit)

    pq.functional_units.append(unit)
    session.add(pq)
    session.commit()
    session.refresh(pq)
    return unit

@router.post("/addphysicalquantities")
def add_physical_quantities_from_yaml(session: SessionDep):
    # Get path to config directory
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config")
    units_yaml_path = os.path.join(config_dir, "units.yaml")
    if not os.path.exists(units_yaml_path):
        raise HTTPException(status_code=404, detail="Units configuration file not found")

    with open(units_yaml_path, "r") as file:
        data = yaml.safe_load(file)

    physical_quantities = data.get("physicalQuantities", [])
    created_quantities = []
    for pq in physical_quantities:
        name = pq.get("name")
        if not name:
            continue
        new_pq = PhysicalQuantity(
            quantity=name
        )
        session.add(new_pq)
        created_quantities.append(new_pq)
        session.commit()
    return {"message": f"{len(created_quantities)} physical quantities added", "physical_quantities": [q.quantity for q in created_quantities]}
