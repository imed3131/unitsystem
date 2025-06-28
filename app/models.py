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
    value: str
    base : str
    createdAt: Optional[datetime] = None
    createdBy: Optional[UUID] = None
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

# Link models are no longer needed since each PhysicalQuantity only has one unit (either linear or functional)

# Association tables for many-to-many relationships

physicalquantity_linearunit_link = Table(
    "physicalquantity_linearunit_link",
    SQLModel.metadata,
    Column("physicalquantity_id", ForeignKey("physicalquantity.id"), primary_key=True),
    Column("linearunit_id", ForeignKey("linearunit.id"), primary_key=True),
)

physicalquantity_functionalunit_link = Table(
    "physicalquantity_functionalunit_link",
    SQLModel.metadata,
    Column("physicalquantity_id", ForeignKey("physicalquantity.id"), primary_key=True),
    Column("functionalunit_id", ForeignKey("functionalunit.id"), primary_key=True),
)

class LinearUnit(UnitBase, table=True):
    __tablename__ = "linearunit"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    factorToBase: float
    physical_quantities: List["PhysicalQuantity"] = Relationship(
        back_populates="linear_units",
        sa_relationship_kwargs={"secondary": physicalquantity_linearunit_link},
    )
    class Create(SQLModel):
        name: str
        value: str
        base: str
        factorToBase: float


class FunctionalUnit(UnitBase, table=True):
    __tablename__ = "functionalunit"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    toBase: str
    fromBase: str
    physical_quantities: List["PhysicalQuantity"] = Relationship(
        back_populates="functional_units",
        sa_relationship_kwargs={"secondary": physicalquantity_functionalunit_link},
    )
    class Create(SQLModel):
        name: str
        value: str
        base : str
        toBase: str
        fromBase: str
class PhysicalQuantity(SQLModel, table=True):
    __tablename__ = "physicalquantity"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    quantity: str
    # Many-to-many relationships
    linear_units: List["LinearUnit"] = Relationship(
        back_populates="physical_quantities",
        sa_relationship_kwargs={"secondary": physicalquantity_linearunit_link},
    )
    functional_units: List["FunctionalUnit"] = Relationship(
        back_populates="physical_quantities",
        sa_relationship_kwargs={"secondary": physicalquantity_functionalunit_link},
    )


    class Create(SQLModel):
        quantity: str

    class Read(SQLModel):
        id: UUID
        quantity: str
        linear_units: Optional[List["LinearUnit"]] = None
        functional_units: Optional[List["FunctionalUnit"]] = None
class UnitSystemRead(SQLModel):
    id: UUID
    name: str
    physical_quantities: List["PhysicalQuantity.Read"] = Field(default_factory=list)
    createdAt: datetime
    createdBy: Optional[UUID] = None
    updatedAt: datetime
    updatedBy: Optional[UUID] = None
    is_deleted: bool
    deleted_at: Optional[datetime]
    deleted_by: Optional[UUID] = None

class UnitSystemUpdate(SQLModel):
    name: Optional[str] = None
class UnitSystemCreate(SQLModel):
    name: str

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


#===========================================================================

class TestTemplateGeneralInfo(SQLModel, table=True):  # Changed to table=True
    __tablename__ = "testtemplategeneralinfo"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    value: str
    isLink: bool
    link: Optional[str] = None
    isFile: bool
    test_template_id: Optional[UUID] = Field(default=None, foreign_key="testtemplate.id")
    test_template: Optional["TestTemplate"] = Relationship(back_populates="generalInfo")
    
    class Create(SQLModel):
        name: str
        value: str
        isLink: bool
        link: Optional[str] = None
        isFile: bool
    
    class Read(SQLModel):
        name: str
        value: str
        isLink: bool
        link: Optional[str] = None
        isFile: bool


class TestTemplateCondition(SQLModel, table=True):  # Changed to table=True
    __tablename__ = "testtemplatecondition"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    value: float
    physicalQuantity: str
    required: bool
    test_template_id: Optional[UUID] = Field(default=None, foreign_key="testtemplate.id")
    test_template: Optional["TestTemplate"] = Relationship(back_populates="conditions")
    
    class Create(SQLModel):
        name: str
        value: float
        physicalQuantity: str
        required: bool
    
    class Read(SQLModel):
        name: str
        value: float
        physicalQuantity: str
        required: bool


class TestTemplateReading(SQLModel, table=True):  # Changed to table=True
    __tablename__ = "testtemplatereading"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    value: Optional[str] = None  # formula
    physicalQuantity: str
    isRequired: bool
    test_template_id: Optional[UUID] = Field(default=None, foreign_key="testtemplate.id")
    test_template: Optional["TestTemplate"] = Relationship(back_populates="readings")
    
    class Create(SQLModel):
        name: str
        value: Optional[str] = None
        physicalQuantity: str
        isRequired: bool
    
    class Read(SQLModel):
        name: str
        value: Optional[str] = None
        physicalQuantity: str
        isRequired: bool


class TestTemplateBase(SQLModel):
    name: str
    tags: List[str] = Field(default_factory=list, sa_column=Column(PG_JSONB))
    isVLCompatible: bool
    version: int
    isLastVersion: bool

    createdAt: datetime
    updatedBy: Optional[UUID] = None
    updatedAt: datetime
    updatedBy: Optional[UUID] = None

    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None


class TestTemplate(TestTemplateBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Remove the explicit foreign key and let the relationship handle it
    generalInfo: Optional["TestTemplateGeneralInfo"] = Relationship(
        back_populates="test_template",
        sa_relationship_kwargs={"uselist": False}
    )

    conditions: List["TestTemplateCondition"] = Relationship(
        back_populates="test_template", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    readings: List["TestTemplateReading"] = Relationship(
        back_populates="test_template", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    class Create(SQLModel):
        name: str
        tags: List[str] = Field(default_factory=list, sa_column=Column(PG_JSONB))
        isVLCompatible: bool
        version: int
        isLastVersion: bool
        generalInfo: Optional["TestTemplateGeneralInfo.Create"]
        conditions: List["TestTemplateCondition.Create"] = []
        readings: List["TestTemplateReading.Create"] = []
    
    class Read(SQLModel):
        id: UUID
        name: str
        tags: List[str] = Field(default_factory=list, sa_column=Column(PG_JSONB))
        isVLCompatible: bool
        version: int
        isLastVersion: bool
        createdAt: datetime
        is_deleted: bool = False
        updatedAt: datetime
        deleted_at: Optional[datetime] = None
        generalInfo: Optional["TestTemplateGeneralInfo.Read"] = None
        conditions: List["TestTemplateCondition.Read"] = []
        readings: List["TestTemplateReading.Read"] = []
    
    class Update(SQLModel):
        name: Optional[str] = None
        tags: Optional[List[str]] = None
        isVLCompatible: Optional[bool] = None
        version: Optional[int] = None


#========================================================================================

# =================== ObjectTemplate and related models ===================

class ObjectTemplateRule(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    object_template_id: UUID = Field(foreign_key="objecttemplate.id")
    name: str
    value: str
    isLink: bool
    link: Optional[str] = None
    isFile: bool

    object_template: "ObjectTemplate" = Relationship(back_populates="rules")

    class Create(SQLModel):
        name: str
        value: str
        isLink: bool
        link: Optional[str] = None
        isFile: bool

class ObjectTemplateBase(SQLModel):
    name: str
    description: str
    type: str
    tags: List[str] = Field(default_factory=list, sa_column=Column(PG_JSONB))
    allowedComposition: List[List[str]] = Field(default_factory=list, sa_column=Column(PG_JSONB))
    fabricant: str
    fournisseur: str
    version: int
    isLastVersion: bool
    createdAt: datetime
    createdBy: Optional[UUID] = None
    updatedAt: datetime
    updatedBy: Optional[UUID] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None

class ObjectTemplate(ObjectTemplateBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rules: List["ObjectTemplateRule"] = Relationship(
        back_populates="object_template", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    attachments: List["Attachment"] = Relationship(
        back_populates="object_template", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Create(SQLModel):
        name: str
        description: str
        type: str
        tags: List[str] = Field(default_factory=list)
        allowedComposition:  List[List[str]] = Field(default_factory=list)
        rules: List["ObjectTemplateRule.Create"] 
        attachments: List["Attachment.Create"]
        fabricant: str
        fournisseur: str
        version: int
        isLastVersion: bool
    
    class Read(SQLModel):
        id: UUID
        name: str
        description: str
        type: str
        tags: List[str]
        allowedComposition:  List[List[str]]
        rules: List["ObjectTemplateRule"] 
        attachments: List["Attachment.Read"]
        fabricant: str
        fournisseur: str
        version: int
        isLastVersion: bool
        createdAt: datetime
        updatedAt: datetime
        is_deleted: bool
        deleted_at: Optional[datetime] = None
        deleted_by: Optional[UUID] = None

    class Update(SQLModel):
        name: Optional[str] = None
        description: Optional[str] = None
        type: Optional[str] = None
        tags: Optional[List[str]] = None
        allowedComposition: Optional[List[List[str]]] = None
        fabricant: Optional[str] = None
        fournisseur: Optional[str] = None
        version: Optional[int] = None
        isLastVersion: Optional[bool] = None

class AttachmentFileStorage(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    provider: str
    path: str
    bucket: Optional[str] = None

    attachment: Optional["Attachment"] = Relationship(back_populates="file_storage")

    class Create(SQLModel):
        provider: str
        path: str
        bucket: Optional[str] = None

class Attachment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    file_name: str
    file_type: str
    file_storage_id: Optional[UUID] = Field(default=None, foreign_key="attachmentfilestorage.id")
    file_storage: Optional["AttachmentFileStorage"] = Relationship(back_populates="attachment")
    size_bytes: int
    file_hash: Optional[str] = None
    uploaded_by: Optional[UUID] = None
    uploaded_at: datetime
    reference_count: int
    meta_data: dict = Field(default_factory=dict, sa_column=Column(PG_JSONB))
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None
    object_template_id: Optional[UUID] = Field(default=None, foreign_key="objecttemplate.id")
    object_template: Optional["ObjectTemplate"] = Relationship(back_populates="attachments")

    class Create(SQLModel):
        file_name: str
        file_type: str
        file_storage: Optional["AttachmentFileStorage.Create"]  =  None 
        size_bytes: int
        file_hash: Optional[str] = None
        reference_count: int = 1
        meta_data: dict = Field(default_factory=dict)
    class Read(SQLModel):
        id: UUID
        file_name: str
        file_type: str
        file_storage_id: Optional[UUID] = None
        file_storage: Optional["AttachmentFileStorage"] = None  # This will include the full object
        size_bytes: int
        file_hash: Optional[str] = None
        uploaded_by: Optional[UUID] = None
        uploaded_at: datetime
        reference_count: int
        meta_data: dict
        is_deleted: bool
        deleted_at: Optional[datetime] = None
        deleted_by: Optional[UUID] = None
        object_template_id: Optional[UUID] = None
    class Update(SQLModel):
        file_name: Optional[str] = None
        file_type: Optional[str] = None
        size_bytes: Optional[int] = None
        file_hash: Optional[str] = None
        reference_count: Optional[int] = None
        meta_data: Optional[dict] = None 
        file_storage: Optional["AttachmentFileStorage.Create"] = None

class AttachmentLink(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    attachment_id: UUID = Field(foreign_key="attachment.id")
    attachment: "Attachment" = Relationship()
    class_type: str
    object_id: UUID
    added_by: Optional[UUID] = None
    added_at: datetime
    is_required: bool
    link_metadata: dict = Field(default_factory=dict, sa_column=Column(PG_JSONB))
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None

    class Create(SQLModel):
        attachment_id: UUID
        class_type: str
        object_id: UUID
        is_required: bool
        link_metadata: dict = Field(default_factory=dict)