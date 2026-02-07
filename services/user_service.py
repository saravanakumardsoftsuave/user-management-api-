from sqlalchemy import text
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
    INTERNAL_SERVER_ERROR_MSG = "Internal server error"
    USER_NOT_FOUND_MSG = "User not found"
    TODO_NOT_FOUND_MSG = "Todo item not found"
    
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
                                content=CommonResponse(status=True, message="User created successfully").model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status="error", message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())

    async def login(self, username: str, password: str) -> CommonResponse:
        try:
            result = await self.db.execute(select(User).where((User.email == username) | (User.username == username)))
            user = result.scalars().first()
            if not user or not verify_password(password, user.password):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            access_token =token(data={"user_id": user.id,
                                        "role": user.role})
            return {
                   "access_token": access_token,
            "token_type": "bearer",
            "role": user.role
            }
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail=CommonResponse(status=False, message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())

    async def get_all_users(self) :
        try:
            
            role = "User"
            is_deleted = False

            query = text("""
            SELECT id, first_name, last_name, username, email, phone, gender
            FROM users
            WHERE role = :role AND is_deleted = :is_deleted
            """)

            result = await self.db.execute(
            query,
            {"role": role, "is_deleted": is_deleted}
            )
            rows = result.mappings().all()

            users = [dict(row) for row in rows]

            return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=CommonResponse(
                status=True,
                message="User retrieved successfully",
                data=users
            ).model_dump()
            )
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, 
                                                      message=self.INTERNAL_SERVER_ERROR_MSG, 
                                                      error=str(e)).model_dump())

    async def get_user_by_id(self, user_id: int, current_user: User) -> CommonResponse:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to get user by id")
            result = await self.db.execute(select(User).where(User.id == user_id,role="user"))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.USER_NOT_FOUND_MSG)
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="User retrieved successfully", 
                                                       data=user).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())

    async def update_user(self, user_id: int, updated_user: UserUpdate, current_user: User) -> CommonResponse:
        try:
            if current_user.role != "Admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update users")
            result = await self.db.execute(select(User).where(User.id == user_id,User.role=="User",User.is_deleted==False))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.USER_NOT_FOUND_MSG)
           
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
        "first_name": updated_user.first_name,
        "last_name": updated_user.last_name,
        "username": updated_user.username,
        "email": updated_user.email,
        "phone": updated_user.phone,
        "gender": updated_user.gender,
        "user_id": user_id,
    }
)

            await self.db.commit()

            await self.db.refresh(user)
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="User updated successfully", 
                                                      ).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())

    async def delete_user(self, user_id: int, current_user: User) -> CommonResponse:
        try:
            if current_user.role != "Admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete users")
            
            result = await self.db.execute(select(User).where(User.id == user_id,User.role=="User"))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.USER_NOT_FOUND_MSG)
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
                                detail=CommonResponse(status=False, message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())

    async def create_todo_item(self, user_id: int, todo_item: TodoItemBase) -> CommonResponse:
        try:
            result = await self.db.execute(select(User).where(User.id == user_id, User.role.in_(["User", "Manager"])))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.USER_NOT_FOUND_MSG)

            new_todo = TodoItem(
                user_id=user_id,
                title=todo_item.title,
                description=todo_item.description,
            )
            self.db.add(new_todo)
            await self.db.commit()
            await self.db.refresh(new_todo)
            return JSONResponse(status_code=status.HTTP_201_CREATED,
                                content=CommonResponse(status=True, message="Todo item created successfully", 
                                                       ).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content=CommonResponse(status=False, message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())

    async def get_todo_items(self, user_id: int) -> JSONResponse:
        try:
            result = await self.db.execute(
                select(TodoItem).where(
                    TodoItem.user_id == user_id,
                    TodoItem.is_completed == False
                )
            )

            todo_items = result.scalars().all()

            # Convert SQLAlchemy objects to dict properly
            items = [
                {
                    "id": item.id,
                    "user_id": item.user_id,
                    "title": item.title,
                    "description": item.description,
                    "is_completed": item.is_completed
                }
                for item in todo_items
            ]

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=CommonResponse(
                    status=True,
                    message="Todo items retrieved successfully",
                    data=items
                ).model_dump()
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=CommonResponse(
                    status=False,
                    message=self.INTERNAL_SERVER_ERROR_MSG,
                    error=str(e)
                ).model_dump()
            )

    async def update_todo_item(self,current_user_id: int, todo_id: int, updated_todo: TodoItemBase) -> CommonResponse:
        try:
            result = await self.db.execute(select(TodoItem).where(TodoItem.id == todo_id, TodoItem.user_id == current_user_id))
            todo_item = result.scalars().first()
            if not todo_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.TODO_NOT_FOUND_MSG)

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
                    "todo_id": todo_id,
                }
            )
            await self.db.commit()
            await self.db.refresh(todo_item)
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="Todo item updated successfully", 
                                                       ).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())
    async def markscomplete(self, current_user_id: int, todo_id: int) -> CommonResponse:
        try:
            result = await self.db.execute(select(TodoItem).where(TodoItem.id == todo_id, TodoItem.user_id == current_user_id))
            todo_item = result.scalars().first()
            if not todo_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.TODO_NOT_FOUND_MSG)

            update=text("""
                UPDATE todo_items
                SET is_completed = TRUE
                WHERE id = :todo_id
            """)
            await self.db.execute(
                update,
                {
                    "todo_id": todo_id,
                }
            )
            await self.db.commit()
            await self.db.refresh(todo_item)
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="Todo item marked as complete successfully", 
                                                       ).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())

    async def delete_todo_item(self, current_user_id: int, todo_id: int) -> CommonResponse:
        try:
            result = await self.db.execute(select(TodoItem).where(TodoItem.id == todo_id, TodoItem.user_id == current_user_id))
            todo_item = result.scalars().first()
            if not todo_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.TODO_NOT_FOUND_MSG)
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
                                detail=CommonResponse(status=False, message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())
        
    async def revoke_user(self, user_id: int, current_user: User) -> CommonResponse:
        try:
            if current_user.role != "Admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete users")
            
            result = await self.db.execute(select(User).where(User.id == user_id,User.role=="User"))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            delete=text("""
                UPDATE users
                SET is_deleted = FALSE
                WHERE id = :user_id
            """)
            await self.db.execute(delete, {"user_id": user_id})
            await self.db.commit()
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="User deleted successfully").model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())

    async def revoke_users(self) :
        try:
            
            role = "User"
            is_deleted = True

            query = text("""
            SELECT id, first_name, last_name, username, email, phone, gender
            FROM users
            WHERE role = :role AND is_deleted = :is_deleted
            """)

            result = await self.db.execute(
            query,
            {"role": role, "is_deleted": is_deleted}
            )
            rows = result.mappings().all()

            users = [dict(row) for row in rows]

            return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=CommonResponse(
                status=True,
                message="User revoked successfully",
                data=users
            ).model_dump()
            )
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False, 
                                                      message="Internal server error", 
                                                      error=str(e)).model_dump())
    async def update_current(self, user_id: int, updated_user: UserUpdate) -> CommonResponse:
                try:
                    
                    result = await self.db.execute(select(User).where(User.id == user_id,User.is_deleted==False))
                    user = result.scalars().first()
                    if not user:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self.USER_NOT_FOUND_MSG)
                
                    update_data = updated_user.dict(exclude_unset=True)

                    set_clause = ", ".join([f"{key} = :{key}" for key in update_data.keys()])

                    query = text(f"""
                        UPDATE users
                        SET {set_clause}
                        WHERE id = :user_id
                    """)
                    update_data["user_id"] = user_id
                    await self.db.execute(query, update_data)

                    await self.db.commit()

                    await self.db.refresh(user)
                    return JSONResponse(status_code=status.HTTP_200_OK,
                                        content=CommonResponse(status=True, message="User updated successfully", 
                                                            ).model_dump())
                except Exception as e:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                        detail=CommonResponse(status=False, message=self.INTERNAL_SERVER_ERROR_MSG,
                                                            error=str(e)).model_dump())
    async def get_todo(self, user_id: int) -> list[CommonResponse]:
        try:
            result = await self.db.execute(select(TodoItem).where(TodoItem.user_id == user_id, TodoItem.is_completed == True))
            todo_items = result.scalars().all()
            items = [
                {
                    "id": item.id,
                    "user_id": item.user_id,
                    "title": item.title,
                    "description": item.description,
                    "is_completed": item.is_completed
                }
                for item in todo_items
            ]
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=CommonResponse(status=True, message="Todo items retrieved successfully", data=items).model_dump())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=CommonResponse(status=False , message=self.INTERNAL_SERVER_ERROR_MSG,
                                                       error=str(e)).model_dump())