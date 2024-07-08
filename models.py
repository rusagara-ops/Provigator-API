from pydantic import BaseModel, Field, EmailStr
from typing import Optional
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
