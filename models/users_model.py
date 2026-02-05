from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Identity
    first_name = Column(String(100))
    last_name = Column(String(100))
    username = Column(String(100), unique=True, index=True)
    email = Column(String(150), unique=True, index=True)
    phone = Column(String(15))
    password= Column(String(255))
    # Personal Details
    gender = Column(String(20))
    date_of_birth = Column(Date)
    blood_group = Column(String(5))
    marital_status = Column(String(20))
    nationality = Column(String(50))

    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    pincode = Column(String(10))

    # Professional Info
    employee_id = Column(String(50))
    department = Column(String(100))
    designation = Column(String(100))
    joining_date = Column(Date)
    work_location = Column(String(100))
    qualification = Column(String(150))
    experience_years = Column(String(20))
    skills = Column(String(255))

    # Role (for your admin/manager/user UI separation)
    role = Column(String(50))
    is_deleted = Column(Boolean, default=False)  # 0 for False, 1 for True
    todo_items = relationship("TodoItem", back_populates="user")

class TodoItem(Base):
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.id"))
    title = Column(String(255))
    description = Column(String(500))
    is_completed = Column(Integer, default=0)  # 0 for False, 1 for True

    user = relationship("User", back_populates="todo_items")
