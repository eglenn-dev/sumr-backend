from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.schemas import token as token_schema
from app.schemas import user as user_schema
from app.schemas import msg as msg_schema
from app.crud import crud_user
from app.api import deps
from app.db.session import get_db 

router = APIRouter()

@router.post("/login/token", response_model=token_schema.Token)
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud_user.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/", response_model=user_schema.UserRead, status_code=status.HTTP_201_CREATED)
def create_new_user(
    *,
    db: Session = Depends(get_db),
    user_in: user_schema.UserCreate,
):
    """
    Create new user. Public endpoint.
    """
    user = crud_user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )
    user_email = crud_user.get_user_by_email(db, email=user_in.email)
    if user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    user = crud_user.create_user(db=db, user_in=user_in)
    return user

@router.get("/users/me", response_model=user_schema.UserRead)
def read_users_me(
    current_user: user_schema.UserRead = Depends(deps.get_current_active_user),
):
    """
    Get current user.
    """
    return current_user