import uuid

from pydantic import EmailStr
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING, Optional, Dict , List
from sqlmodel import SQLModel, Field
from uuid import UUID
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy import Table, Column, ForeignKey
from sqlmodel import SQLModel
# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# ============================================================================

# There start the added code 

class UnitBase(SQLModel):
    name: str
    base: str
    createdAt: datetime
    createdBy: UUID
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None

class Unit(UnitBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class UnitSystem(SQLModel, table=True):
    __tablename__ = "unitsystem"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    createdAt: datetime
    createdBy: Optional[UUID] = None
    updatedAt: datetime
    updatedBy: Optional[UUID] = None
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None

    physical_quantities: List["PhysicalQuantity"] = Relationship(back_populates="unit_system")

# Link models defined early
class LinearUnitPhysicalQuantityLink(SQLModel, table=True):
    __tablename__ = "linearunitphysicalquantitylink"
    linear_unit_id: UUID = Field(foreign_key="linearunit.id", primary_key=True)
    physical_quantity_id: UUID = Field(foreign_key="physicalquantity.id", primary_key=True)

class FunctionalUnitPhysicalQuantityLink(SQLModel, table=True):
    __tablename__ = "functionalunitphysicalquantitylink"
    functional_unit_id: UUID = Field(foreign_key="functionalunit.id", primary_key=True)
    physical_quantity_id: UUID = Field(foreign_key="physicalquantity.id", primary_key=True)

class LinearUnit(UnitBase, table=True):
    __tablename__ = "linearunit"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    factorToBase: float
    physical_quantities: List["PhysicalQuantity"] = Relationship(
        back_populates="linear_units",
        link_model=LinearUnitPhysicalQuantityLink
    )

class FunctionalUnit(UnitBase, table=True):
    __tablename__ = "functionalunit"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    toBase: str
    fromBase: str
    physical_quantities: List["PhysicalQuantity"] = Relationship(
        back_populates="functional_units",
        link_model=FunctionalUnitPhysicalQuantityLink
    )

class PhysicalQuantity(SQLModel, table=True):
    __tablename__ = "physicalquantity"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    quantity: str
    value: str
    unit_system_id: Optional[UUID] = Field(default=None, foreign_key="unitsystem.id")
    
    # Relationships
    unit_system: Optional["UnitSystem"] = Relationship(back_populates="physical_quantities")
    linear_units: List["LinearUnit"] = Relationship(
        back_populates="physical_quantities",
        link_model=LinearUnitPhysicalQuantityLink
    )
    functional_units: List["FunctionalUnit"] = Relationship(
        back_populates="physical_quantities",
        link_model=FunctionalUnitPhysicalQuantityLink
    )
    class Create(SQLModel):
        quantity: str
        value: str
    class Read(SQLModel):
        quantity: str
        value: str
        linear_units: List["LinearUnit"] 
        functional_units: List["FunctionalUnit"]
class UnitSystemRead(SQLModel):
    name: str
    physical_quantities: list["PhysicalQuantity.Read"]
    createdAt: datetime
    updatedAt: datetime
    is_deleted: bool
    deleted_at: Optional[datetime]

class UnitSystemUpdate(SQLModel):
    name: Optional[str] = None
    physical_quantities: Optional[List["PhysicalQuantity"]] = None  # List of Unit IDs
    updatedBy: Optional[UUID] = None
class UnitSystemCreate(SQLModel):
    name: str
    physical_quantities: List["PhysicalQuantity.Create"] # List of PhysicalQuantity Create models

#===========================================================================

# Project models 
if TYPE_CHECKING:
    pass

class ProjectMetaData(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id")
    name: str
    value: str
    project: "Project" = Relationship(back_populates="project_metadata")
    
    class Create(SQLModel):
        name: str
        value: str

class ProjectRule(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id")
    name: str
    isLink: bool
    isFile: bool
    link: Optional[str] = None
    project: "Project" = Relationship(back_populates="rules")
    
    class Create(SQLModel):
        name: str
        isLink: bool
        isFile: bool
        link: Optional[str] = None

class ProjectObjective(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id")
    name: str
    valueMin: Optional[float] = None
    valueMax: Optional[float] = None
    physicalQuantity: Optional[str] = None
    text: Optional[str] = None
    isOptional: bool
    project: "Project" = Relationship(back_populates="objectives")
    
    class Create(SQLModel):
        name: str
        valueMin: Optional[float] = None
        valueMax: Optional[float] = None
        physicalQuantity: Optional[str] = None
        text: Optional[str] = None
        isOptional: bool

class ProjectDeliverable(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id")
    name: str
    content: str
    isOptional: bool
    project: "Project" = Relationship(back_populates="deliverables")
    
    class Create(SQLModel):
        name: str
        content: str
        isOptional: bool

class ProjectConstraint(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id")
    name: str
    value: str
    project: "Project" = Relationship(back_populates="constraints")
    
    class Create(SQLModel):
        name: str
        value: str

class ProjectAttachment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="project.id")
    name: str
    project: "Project" = Relationship(back_populates="attachments")
    
    class Create(SQLModel):
        name: str
        attachmentId: UUID

class ProjectBase(SQLModel):
    name: str
    client: str
    status: str
    type: str
    startDate: datetime
    expectedDeliveryDate: datetime
    version: int
    isLastVersion: bool
    createdAt: datetime
    createdBy: UUID
    updatedAt: datetime
    updatedBy: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None

class Project(ProjectBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    

    project_metadata: List["ProjectMetaData"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    rules: List["ProjectRule"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    objectives: List["ProjectObjective"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    deliverables: List["ProjectDeliverable"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    constraints: List["ProjectConstraint"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    attachments: List["ProjectAttachment"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class UpdateProject(SQLModel):
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    client: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    startDate: Optional[datetime] = None
    expectedDeliveryDate: Optional[datetime] = None
    version: Optional[int] = None
    isLastVersion: Optional[bool] = None
    updatedAt: Optional[datetime] = None
    updatedBy: Optional[UUID] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None


# ===========================================================================


class RealCondition(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    test_id: UUID = Field(foreign_key="test.id")
    name: str
    value: str
    physicalQuantity: str
    required: bool
    test: "Test" = Relationship(back_populates="realConditions")

    class Create(SQLModel):
        name: str
        value: str
        physicalQuantity: str
        required: bool


class Reading(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    test_id: UUID = Field(foreign_key="test.id")
    name: str
    value: Optional[str] = None  # formula
    physicalQuantity: str
    isRequired: bool
    test: "Test" = Relationship(back_populates="readings")

    class Create(SQLModel):
        name: str
        value: Optional[str] = None
        physicalQuantity: str
        isRequired: bool


class VLReading(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    test_id: UUID = Field(foreign_key="test.id")
    name: str
    value: Optional[str] = None  # formula
    physicalQuantity: str
    isRequired: bool
    test: "Test" = Relationship(back_populates="vlReadings")

    class Create(SQLModel):
        name: str
        value: Optional[str] = None
        physicalQuantity: str
        isRequired: bool



class TestBase(SQLModel):
    isVLCompatible: bool
    version: int
    isLastVersion: bool
    createdAt: datetime
    createdBy: UUID
    updatedAt: datetime
    updatedBy: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None

class TestCreate(SQLModel):
    isVLCompatible: bool
    version: int
    isLastVersion: bool
    updatedBy: UUID
    createdBy: UUID



class TestUpdate(SQLModel):
    isVLCompatible: Optional[bool] = None
    version: Optional[int] = None
    isLastVersion: Optional[bool] = None


class Test(TestBase, table=True):
    __tablename__ = "test"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    realConditions: List[RealCondition] = Relationship(
        back_populates="test", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    readings: List[Reading] = Relationship(
        back_populates="test", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    vlReadings: List[VLReading] = Relationship(
        back_populates="test", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )