from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class StatusBase(BaseModel):
    name: str = Field(..., max_length=50)


class StatusCreate(StatusBase):
    pass


class Status(StatusBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str = Field(..., max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithTaskCount(BaseModel):
    username: str
    task_count: int

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None


class TaskCreate(TaskBase):
    status_id: int
    user_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status_id: Optional[int] = None
    user_id: Optional[int] = None


class TaskStatusUpdate(BaseModel):
    status_id: int


class Task(TaskBase):
    id: int
    status_id: int
    user_id: int

    class Config:
        from_attributes = True


class TaskWithDetails(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: Status
    user: User

    class Config:
        from_attributes = True


class UserWithInProgressTask(BaseModel):
    username: str
    title: str
    description: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class TaskCountByStatus(BaseModel):
    name: str
    task_count: int

    class Config:
        from_attributes = True

