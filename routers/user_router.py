from urllib import request
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession 
from database import get_db
from models.users_model import  User, TodoItem
from utils.user_utils import get_user, token
from schemas.user_sechema import UserDetails, UserUpdate, CommonResponse, TodoItemBase,Todoupdate, UserSUpdate
from services.user_service import UserService

INTERNAL_SERVER_ERROR_MESSAGE = "Internal server error"

user_router = APIRouter(
    prefix="/user", 
    tags=["user"]
)

@user_router.post("/createuser")
async def create_user(user: UserDetails, db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.create_user(user)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=CommonResponse(message=INTERNAL_SERVER_ERROR_MESSAGE,
                                                   error=str(e)).model_dump())


@user_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.login(form_data.username, form_data.password)
        return response
    except Exception as e: 
        raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=CommonResponse(
        status=False,
        message=INTERNAL_SERVER_ERROR_MESSAGE,
        error=str(e)
    ).model_dump()
)
 

@user_router.get("/allusers")
async def get_all_users(current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try: 
        
        user_service = UserService(db)
        response = await user_service.get_all_users()
        return response
    except Exception as e: 
        raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=CommonResponse(
        status=False,
        message=INTERNAL_SERVER_ERROR_MESSAGE,
        error=str(e)
    ).model_dump()
)

@user_router.get("/me")
async def read_users_me(request: Request, current_user: User = Depends(get_user)):
    
    return current_user

@user_router.get("/getuser/{user_id}")
async def get_user_by_id(user_id: int, current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.get_user_by_id(user_id, current_user)
        return response
    except Exception as e: 
         raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=CommonResponse(
        status=False,
        message=INTERNAL_SERVER_ERROR_MESSAGE,
        error=str(e)
    ).model_dump()
)

@user_router.put("/updateuser/{id}")
async def update_user(id:int,updated_user: UserUpdate, current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.update_user(id, updated_user,current_user)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
       detail=CommonResponse(
        status=False,
        message=INTERNAL_SERVER_ERROR_MESSAGE,
        error=str(e)
    ).model_dump()
)

@user_router.delete("/deleteuser/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.delete_user(user_id,current_user)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=CommonResponse(message=INTERNAL_SERVER_ERROR_MESSAGE,
                                                   error=str(e)).model_dump())

@user_router.post("/todo")
async def create_todo_item(todo_item: Todoupdate, current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.create_todo_item(current_user.id, todo_item)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=CommonResponse(message=INTERNAL_SERVER_ERROR_MESSAGE,
                                                   error=str(e)).model_dump())       

@user_router.get("/gettodo")
async def read_todo_items(current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.get_todo_items(current_user.id)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=CommonResponse(message=INTERNAL_SERVER_ERROR_MESSAGE,
                                                   error=str(e)).model_dump())

@user_router.put("/todoupdate/{todo_id}")
async def update_todo_item(todo_id: int, updated_todo: Todoupdate, current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.update_todo_item(current_user.id, todo_id, updated_todo)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=CommonResponse(message=INTERNAL_SERVER_ERROR_MESSAGE,
                                                   error=str(e)).model_dump())

@user_router.put("/markscomplete/{todo_id}")
async def markscompleted(todo_id: int, current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.markscomplete(current_user.id, todo_id)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=CommonResponse(message=INTERNAL_SERVER_ERROR_MESSAGE,
                                                   error=str(e)).model_dump())
@user_router.delete("/deletetodo/{todo_id}")
async def delete_todo_item(todo_id: int, current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.delete_todo_item(current_user.id, todo_id)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=CommonResponse(message=INTERNAL_SERVER_ERROR_MESSAGE,
                                                   error=str(e)).model_dump())

    
@user_router.put("/revokeuser/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.revoke_user(user_id,current_user)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=CommonResponse(message=INTERNAL_SERVER_ERROR_MESSAGE,
                                                   error=str(e)).model_dump())

@user_router.get("/allRevoke")
async def get_all_users(current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try: 
        
        user_service = UserService(db)
        response = await user_service.revoke_users()
        return response
    except Exception as e: 
        raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=CommonResponse(
        status=False,
        message=INTERNAL_SERVER_ERROR_MESSAGE,
        error=str(e)
    ).model_dump()
)


@user_router.put("/current/{id}")
async def update_user(id:int,updated_user: UserSUpdate, current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.update_current(id, updated_user)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
       detail=CommonResponse(
        status=False,
        message=INTERNAL_SERVER_ERROR_MESSAGE,
        error=str(e)
    ).model_dump()
)


@user_router.get("/todo_list")
async def read_todo(current_user: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    try:
        user_service = UserService(db)
        response = await user_service.get_todo(current_user.id)
        return response
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=CommonResponse(message=INTERNAL_SERVER_ERROR_MESSAGE,
                                                   error=str(e)).model_dump())