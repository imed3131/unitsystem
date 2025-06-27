# Auto-generated models from YAML schema
from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship


class Project(SQLModel, table=True):
    __tablename__ = "Project"


class Comment(SQLModel, table=True):
    __tablename__ = "Comment"


class Testtemplate(SQLModel, table=True):
    __tablename__ = "TestTemplate"


class Test(SQLModel, table=True):
    __tablename__ = "Test"


class Objecttemplate(SQLModel, table=True):
    __tablename__ = "ObjectTemplate"


class Object(SQLModel, table=True):
    __tablename__ = "Object"


class Observation(SQLModel, table=True):
    __tablename__ = "Observation"


class Attachment(SQLModel, table=True):
    __tablename__ = "Attachment"


class Attachmentlink(SQLModel, table=True):
    __tablename__ = "AttachmentLink"


class Product(SQLModel, table=True):
    __tablename__ = "Product"


class Manufacturer(SQLModel, table=True):
    __tablename__ = "Manufacturer"


class Unit(SQLModel, table=True):
    __tablename__ = "Unit"


class Linearunit(SQLModel, table=True):
    __tablename__ = "LinearUnit"


class Functionalunit(SQLModel, table=True):
    __tablename__ = "FunctionalUnit"


class Unitsystem(SQLModel, table=True):
    __tablename__ = "UnitSystem"

