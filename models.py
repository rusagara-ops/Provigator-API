from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from uuid import UUID, uuid4

class Client(BaseModel):
    id: Optional[UUID] = uuid4()
    name: str
    country: str

class UpdateClient(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None

class UserSchema(BaseModel):
    fullname: str = Field(default=None)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "john@awesomity.rw",
                "password": "12345678"
            }
        }

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)

    class Config:
        schema_extra = {
            "example": {
                "email": "john@awesomity.rw",
                "password": "12345678"
            }
        }

class Project(BaseModel):
    id : Optional [UUID] =uuid4()
    pm_names: str
    name: str
    description: str
    thumbnail: str
    client: str
    type: Literal["App", "Web", "Dashboard"]
    url: str
    bug_report_url: str


class UpdateProject(BaseModel):
    pm_names: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    client: Optional[str] = None
    type: Optional[Literal["App", "Web", "Dashboard"]] = None
    url: Optional[str] = None
    bug_report_url: Optional[str] = None



