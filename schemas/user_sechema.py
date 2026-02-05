from  pydantic  import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserDetails(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    marital_status: Optional[str] = None
    nationality: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    joining_date: Optional[date] = None
    work_location: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[str] = None
    skills: Optional[str] = None

    role: Optional[str] = None


    class Config:
        orm_mode = True

class TodoItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: Optional[bool] = False
    class Config:
        orm_mode = True
        back_populates = "user"
        
class Todoupdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    class Config:
        orm_mode = True
        back_populates = "user"
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gender: Optional[str] = None

class CommonResponse(BaseModel):
    data: Optional[dict] = None
    status: Optional[bool] = None
    message: str
    error: Optional[str] = None