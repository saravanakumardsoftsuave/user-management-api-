from pydoc import text
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.users_model import User, TodoItem
from utils.user_utils import hash_password, verify_password, token, get_user
from schemas.user_sechema import TodoItemBase, UserDetails, CommonResponse,UserUpdate
from sqlalchemy.future import select   


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserDetails) -> CommonResponse:
        try:
            user_exists = await self.db.execute(select(User).where(User.email == user.email, User.username == user.username))
            if user_exists.scalars().first():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
            if user.role.lower() not in ["user", "manager", "admin"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role specified")
            hashed_password = hash_password(user.password)
            new_user = User(
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    email=user.email,
                    phone=user.phone,
                    gender=user.gender,
                    date_of_birth=user.date_of_birth,
                    blood_group=user.blood_group,
                    marital_status=user.marital_status,
                    nationality=user.nationality,
                    address_line1=user.address_line1,
                    address_line2=user.address_line2,
                    city=user.city,
                    state=user.state,
                    country=user.country,
                    pincode=user.pincode,
                    employee_id=user.employee_id,
                    department=user.department,
                    designation=user.designation,
                    joining_date=user.joining_date,
                    work_location=user.work_location,
                    qualification=user.qualification,
                    experience_years=user.experience_years,
                    skills=user.skills,
                    role=user.role,
                    password=hashed_password )
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return JSONResponse(status_code=status.HTTP_201_CREATED,
                                content=CommonResponse(status="success", message="User created successfully").model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content=CommonResponse(status="error", message="Internal server error",
                                                       error=str(e)).model_dump())

    async def login(self, username: str, password: str) -> CommonResponse:
        try:
            result = await self.db.execute(select(User).where((User.email == username) | (User.username == username)))
            user = result.scalars().first()
            if not user or not verify_password(password, user.password):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            access_token = await token(data={"user_id": user.id,
                                        "role": user.role})
            return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=CommonResponse(
            status=True,
            message="Login successful",
            data={
                "access_token": access_token,
                "token_type": "bearer"
            }
        ).model_dump()
    )

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message="Internal server error",
                                                       error=str(e)).model_dump())

    async def get_all_users(self, current_user: User) -> list[CommonResponse]:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to get all users")
            result = text("""
                SELECT * FROM users """)
            user = self.db.execute(result).scalars().all()
            users=[]
            for u in user:
                users.append({
                    "id": u.id,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "username": u.username,
                    "email": u.email,
                    "phone": u.phone,
                    "gender": u.gender,
                })
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="User retrieved successfully", data=users).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message="Internal server error",
                                                       error=str(e)).model_dump())

    async def get_user_by_id(self, user_id: int, current_user: User) -> CommonResponse:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to get user by id")
            result = await self.db.execute(select(User).where(User.id == user_id,role="user"))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="User retrieved successfully", 
                                                       data=user).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message="Internal server error",
                                                       error=str(e)).model_dump())

    async def update_user(self, user_id: int, updated_user: UserUpdate, current_user: User) -> CommonResponse:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update users")
            result = await self.db.execute(select(User).where(User.id == user_id,role="user"))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
           
            query = text("""
                UPDATE users
                SET first_name = :first_name,
                    last_name  = :last_name,
                    username   = :username,
                    email      = :email,
                    phone      = :phone,
                    gender     = :gender
                WHERE id = :user_id
            """)

            await self.db.execute(
                query,
                {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "gender": user.gender,
                    "user_id": user_id,
                }
            )

            await self.db.commit()

            await self.db.refresh(user)
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="User updated successfully", 
                                                       data=user).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message="Internal server error",
                                                       error=str(e)).model_dump())

    async def delete_user(self, user_id: int, current_user: User) -> CommonResponse:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete users")
            
            result = await self.db.execute(select(User).where(User.id == user_id,role="user"))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            delete=text("""
                UPDATE users
                SET is_deleted = TRUE
                WHERE id = :user_id
            """)
            await self.db.execute(delete, {"user_id": user_id})
            await self.db.commit()
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="User deleted successfully").model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message="Internal server error",
                                                       error=str(e)).model_dump())

    async def create_todo_item(self, user_id: int, todo_item: TodoItemBase) -> CommonResponse:
        try:
            result = await self.db.execute(select(User).where(User.id == user_id, User.role.in_(["user", "manager"])))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            new_todo = TodoItem(
                user_id=user_id,
                title=todo_item.title,
                description=todo_item.description,
                is_completed=todo_item.is_completed
            )
            self.db.add(new_todo)
            await self.db.commit()
            await self.db.refresh(new_todo)
            return JSONResponse(status_code=status.HTTP_201_CREATED,
                                content=CommonResponse(status="success", message="Todo item created successfully", 
                                                       data=new_todo).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content=CommonResponse(status="error", message="Internal server error",
                                                       error=str(e)).model_dump())

    async def get_todo_items(self, user_id: int) -> list[CommonResponse]:
        try:
            result = await self.db.execute(select(TodoItem).where(TodoItem.user_id == user_id))
            todo_items = result.scalars().all()
            return [JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="Todo items retrieved successfully", data=item).model_dump()) for item in todo_items]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False , message="Internal server error",
                                                       error=str(e)).model_dump())

    async def update_todo_item(self, todo_id: int, updated_todo: TodoItemBase) -> CommonResponse:
        try:
            result = await self.db.execute(select(TodoItem).where(TodoItem.id == todo_id))
            todo_item = result.scalars().first()
            if not todo_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")

            update=text("""
                UPDATE todo_items
                SET title = :title,
                    description = :description
                WHERE id = :todo_id
            """)
            await self.db.execute(
                update,
                {
                    "title": updated_todo.title,
                    "description": updated_todo.description,
                    "is_completed": updated_todo.is_completed,
                    "todo_id": todo_id,
                }
            )
            await self.db.commit()
            await self.db.refresh(todo_item)
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="Todo item updated successfully", 
                                                       data=todo_item).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message="Internal server error",
                                                       error=str(e)).model_dump())

    async def delete_todo_item(self, todo_id: int) -> CommonResponse:
        try:
            result = await self.db.execute(select(TodoItem).where(TodoItem.id == todo_id))
            todo_item = result.scalars().first()
            if not todo_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
            delete=text("""
                DELETE FROM todo_items
                WHERE id = :todo_id
            """)
            await self.db.execute(delete, {"todo_id": todo_id})
            await self.db.commit()
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="Todo item deleted successfully").model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message="Internal server error",
                                                       error=str(e)).model_dump())