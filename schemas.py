from pydantic import BaseModel, StringConstraints, EmailStr
from typing import Annotated, Optional

class UserBase(BaseModel):
    first_name: Annotated[str, StringConstraints(min_length=2)]
    last_name: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=6)]

class UserSignup(UserBase):
    password: Annotated[str, StringConstraints(min_length=6)]
    password_confirm: Annotated[str, StringConstraints(min_length=6)]

class User(UserBase):
    id: str

class UserDb(User):
    hashed_password: str
    
class UserChangePassword(BaseModel):
    password: Annotated[str, StringConstraints(min_length=6)]
    new_password: Annotated[str, StringConstraints(min_length=6)]
    password_confirm: Annotated[str, StringConstraints(min_length=6)]
    
class UserDelete(BaseModel):
    confirm_delete_account: Optional[bool]
    
class UserJwt(BaseModel):
    id: str
    first_name: str
    
