import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    username: str
    first_name: str #why did you make this optional ? i have a confusion because in general i have notices that te last_name is ususally optional
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password:str

class UserRead(UserBase):
    id : uuid.UUID
    created_at : datetime # should this be current data and time? will we ensure that using frontend?

    class Config: # what is the use of this class? why is it inside USerRead why not all the classes?
        from_attributes = True

class Token(BaseModel): # here i have seen that we are not creating an inside config class can you tell me the reason for this?
    access_token: str
    token_type: str

class TokenData(BaseModel): # here again you have not created an inside config class why? also user_id and email are both optional why?
    user_id : Optional[uuid.UUID] = None
    email : Optional[str] = None
