import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
#-----------------------------USER SCHEMAS--------------------------------#
class UserBase(BaseModel):
    email: str
    username: str
    first_name: str 
    last_name: Optional[str] = None

class UserCreateManual(UserBase): #if the user is signing up with email and password
    password:str


class UsernameCheckResponse(BaseModel): #to check the availability of the username during registration
    username: str
    available: bool

class UserCreateGoogle(BaseModel): #if user is signing up with google auth
    email : str
    first_name : Optional[str] = None
    last_name : Optional[str] = None
    google_sub : str


class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password:str

class UserRead(UserBase):
    id : uuid.UUID
    created_at : datetime 

    class Config: 
        from_attributes = True

class AuthResponse(BaseModel):
    access_token:str
    token_type:str
    user : UserRead

class GoogleLoginRequest(BaseModel):
    id_token: str
#-----------------------------AUTH SCHEMAS--------------------------------#
class Token(BaseModel): 
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id : Optional[uuid.UUID] = None
    email : Optional[str] = None


#----------------------------QUIZ SCHEMAS--------------------------------#
#questions schema:
class QuestionBase(BaseModel):
     
    question_text : str
    image_url : Optional[str] = None
    options : list[str]
    question_type : str
    difficulty_level : int
    explanation : Optional[str] = None
    
class QuestionRead(QuestionBase):
    id : uuid.UUID
    class Config:
        from_attributes = True
#quiz schema:
class QuizCreate(BaseModel):
    quiz_mode : str = "Randomized" 
    total_questions : int = Field( ge = 10, le = 60, description = "number of questions must be between 10 and 60")

class QuizRead(BaseModel):
    id : uuid.UUID
    quiz_mode : str
    status : str
    started_at : datetime
    expires_at : datetime
    completed_at : Optional[datetime] = None
    score : int
    total_questions : int

    class Config:
        from_attributes = True

class QuizResumePayload(BaseModel):
    quiz : QuizRead
    questions : list[QuestionRead]
    saved_response : list[dict]

#------------------------- RESPONSE SCHEMA------------------------#

class ResponseSubmit(BaseModel):
    question_id : uuid.UUID
    selected_option: str
    response_time_seconds: int = 0
    marked_for_review: bool

class QuizResult(BaseModel):
    id : uuid.UUID
    score : int
    accuracy : float
    completed_at :datetime