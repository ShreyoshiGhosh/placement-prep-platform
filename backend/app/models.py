import uuid
from datetime import datetime,timedelta
from typing import Optional, List
# pyrefly: ignore [missing-import]
from sqlmodel import SQLModel, Field, Relationship, Column

# pyrefly: ignore [missing-import]
from sqlalchemy.dialects.postgresql import JSONB



#------------------- LINK TABLES --------------------#
class QuestionTopic( SQLModel, table = True):
    __tablename__ = "question_topics"

    question_id: uuid.UUID = Field(foreign_key="questions.id", primary_key=True)
    topic_id: uuid.UUID = Field(foreign_key = "topics.id", primary_key=True)



class QuestionTag(SQLModel, table = True):
    __tablename__ = "question_tags"

    question_id: uuid.UUID = Field(foreign_key="questions.id", primary_key =True)
    tag_id: uuid.UUID = Field(foreign_key = "tags.id", primary_key= True)

#------------------ CORE MODELS --------------------#

class User(SQLModel, table = True):
    __tablename__ = "users"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key = True) 
    username: str = Field(unique = True, index = True, max_length = 50)
    email:str = Field(unique = True, index = True, max_length = 255)
    password_hash:str 
    first_name: Optional[str] = Field(default = None, max_length = 100)
    last_name: Optional[str] = Field(default = None, max_length = 100)
    created_at: datetime = Field(default_factory = datetime.utcnow)
    updated_at: datetime = Field(default_factory = datetime.utcnow)


class Topic(SQLModel, table = True):
    __tablename__ = "topics"

    id : Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key = True)
    name :str = Field(unique = True, index= True, max_length = 100)
    description : Optional[str] = Field(default = None)
    created_at: datetime = Field(default_factory = datetime.utcnow)
   
    questions: List["Question"] = Relationship(back_populates="topics", link_model = QuestionTopic)


class Tag(SQLModel, table = True):
    __tablename__ = "tags"

    id : Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key = True)
    name : str = Field(unique=True, index = True, max_length = 50)
 
    questions : List["Question"] = Relationship(back_populates="tags", link_model = QuestionTag)



class Question(SQLModel, table= True):
    __tablename__ = "questions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key = True)
    question_text: str = Field(unique =True, nullable = False)
    image_url: Optional[str] = Field(default = None)
    options: List[str] = Field(sa_column = Column(JSONB, nullable = False))
    correct_option:str = Field(nullable = False)
    question_type:str = Field(nullable = False)
    difficulty_level: int = Field(nullable = False)
    explanation:Optional[str] = Field(default = None)
    created_at: datetime = Field(default_factory = datetime.utcnow)
    updated_at: datetime = Field(default_factory = datetime.utcnow)

    #relationships
    topics: List["Topic"] = Relationship(back_populates = "questions", link_model = QuestionTopic)
    tags: List["Tag"] = Relationship(back_populates = "questions", link_model = QuestionTag)


class Response(SQLModel,table = True):
    __tablename__ = "responses"

    id: uuid.UUID = Field(default_factory = uuid.uuid4, primary_key = True)
    user_id: uuid.UUID = Field(foreign_key = "users.id", nullable = False)
    quiz_id : Optional[uuid.UUID] = Field(default = None, foreign_key = "quizzes.id" , nullable = True)
    question_id : uuid.UUID = Field(foreign_key = "questions.id", nullable = False)
    selected_option: Optional[str] = Field(default = None, nullable = True)
    is_correct: Optional[bool] = Field(default = None, nullable = True) 
    response_time_seconds: int = Field(default = None, nullable = True) 
    difficulty_at_attempt: Optional[int] = Field(default = None,nullable = True)
    visited: bool = Field(default=False,nullable=False)
    marked_for_review: bool = Field(default=False,nullable=False)
    answered_at: datetime = Field(default_factory = datetime.utcnow)

    
class Quiz( SQLModel, table = True):
    __tablename__ ="quizzes"
    id : uuid.UUID = Field(default_factory = uuid.uuid4, primary_key = True)
    user_id: uuid.UUID = Field(foreign_key = "users.id", nullable = False)
    quiz_mode:str = Field(nullable = False)
    status: str = Field(nullable = False)
    started_at : datetime = Field(default_factory = datetime.utcnow, nullable = False)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)
    expires_at : datetime = Field(nullable = False)
    score: int = Field(default = 0, nullable = True) 
    total_questions : int = Field(default = 0, nullable = True) 
    accuracy : Optional[float] = Field(default= None,nullable = True) 
    average_difficulty : Optional[float] = Field(default = None, nullable = True) 


class UserTopicStat(SQLModel, table = True):
    __tablename__ = "user_topic_stats"

    id: uuid.UUID = Field(default_factory = uuid.uuid4, primary_key = True)
    user_id: uuid.UUID = Field(foreign_key = "users.id", nullable = False)
    topic_id: uuid.UUID = Field(foreign_key = "topics.id", nullable = False)
    skill_score: Optional[float] = Field(default = None, nullable = True)
    questions_attempted: Optional[int] = Field(default= 0, nullable = True)    
    questions_correct: Optional[int] = Field(default=0, nullable = True)
    average_response_time: Optional[float] = Field(default = None, nullable = True)
    last_practiced: datetime = Field(default_factory= datetime.utcnow, nullable = True)
    updated_at: datetime = Field(default_factory= datetime.utcnow, nullable = True)


