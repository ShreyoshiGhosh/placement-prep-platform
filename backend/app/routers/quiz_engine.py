from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func

import uuid
from datetime import datetime, timedelta
import math
from typing import List

from ..security import get_current_user
from ..database import get_db

from ..models import (
    User,
    Quiz,
    Question,
    Response,
    UserTopicStat,
    QuestionTopic,
    Topic,
)

from ..schemas import (
    QuizCreate,
    QuizResumePayload,
    ResponseSubmit,
    QuizResult,
)

router = APIRouter(tags=["Aptitude Engine"])


# =========================
# START QUIZ
# =========================
@router.post("/quiz/start", response_model=QuizResumePayload)
def start_quiz(
    quiz_data: QuizCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user_id = current_user.id

    existing_quiz = db.query(Quiz).filter(
        Quiz.user_id == current_user_id,
        Quiz.status == "in_progress"
    ).first()

    if existing_quiz:
        if datetime.utcnow() > existing_quiz.expires_at:
            existing_quiz.status = "completed"
            existing_quiz.completed_at = existing_quiz.expires_at
            db.commit()
        else:
            raise HTTPException(
                status_code=400,
                detail="You have an active quiz. Resume or submit it first."
            )

    total = quiz_data.total_questions
    num_easy = math.floor(total * 0.4)
    num_medium = math.floor(total * 0.3)
    num_hard = total - num_easy - num_medium

    easy_questions = db.query(Question).filter(
        Question.difficulty_level == 1
    ).order_by(func.random()).limit(num_easy).all()

    medium_questions = db.query(Question).filter(
        Question.difficulty_level == 2
    ).order_by(func.random()).limit(num_medium).all()

    hard_questions = db.query(Question).filter(
        Question.difficulty_level == 3
    ).order_by(func.random()).limit(num_hard).all()

    all_questions = easy_questions + medium_questions + hard_questions

    now = datetime.utcnow()

    new_quiz = Quiz(
        user_id=current_user_id,
        quiz_mode=quiz_data.quiz_mode,
        status="in_progress",
        started_at=now,
        total_questions=total,
        expires_at=now + timedelta(minutes=total * 1.0),
    )

    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    for q in all_questions:
        db.add(Response(
            user_id=current_user_id,
            quiz_id=new_quiz.id,
            question_id=q.id,
            difficulty_at_attempt=q.difficulty_level
        ))

    db.commit()

    return QuizResumePayload(
        quiz=new_quiz,
        questions=all_questions,
        saved_response=[]
    )


# =========================
# RESUME QUIZ
# =========================
@router.get("/quiz/resume", response_model=QuizResumePayload)
def resume_quiz(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    current_user_id = current_user.id

    quiz = db.query(Quiz).filter(
        Quiz.user_id == current_user_id,
        Quiz.status == "in_progress"
    ).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="No active quiz found")

    if datetime.utcnow() > quiz.expires_at:
        quiz.status = "completed"
        quiz.completed_at = quiz.expires_at
        db.commit()
        raise HTTPException(status_code=400, detail="Test expired")

    responses = db.query(Response).filter(
        Response.quiz_id == quiz.id
    ).all()

    question_ids = [r.question_id for r in responses]

    questions = db.query(Question).filter(
        Question.id.in_(question_ids)
    ).all()

    formatted_responses = [
        {
            "question_id": str(r.question_id),
            "selected_option": r.selected_option,
            "visited": r.visited,
            "marked_for_review": r.marked_for_review,
        }
        for r in responses
    ]

    return QuizResumePayload(
        quiz=quiz,
        questions=questions,
        saved_response=formatted_responses
    )


# =========================
# SAVE RESPONSE
# =========================
@router.post("/quiz/{quiz_id}/response")
def save_single_response(
    quiz_id: uuid.UUID,
    sub: ResponseSubmit,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id,
    Quiz.user_id == current_user.id,
    ).first()

    if not quiz or quiz.status != "in_progress":
        raise HTTPException(status_code=400, detail="Active quiz not found")

    if datetime.utcnow() > quiz.expires_at:
        raise HTTPException(status_code=400, detail="Test expired")

    question = db.query(Question).filter(
        Question.id == sub.question_id
    ).first()

    response_row = db.query(Response).filter(
        Response.quiz_id == quiz.id,
        Response.question_id == sub.question_id
    ).first()

    if not response_row:
        raise HTTPException(
            status_code=400,
            detail="Question not part of this quiz"
        )

    is_correct = (sub.selected_option == question.correct_option)

    response_row.selected_option = sub.selected_option
    response_row.is_correct = is_correct
    response_row.visited = True
    response_row.marked_for_review = sub.marked_for_review
    response_row.response_time_seconds = (
        response_row.response_time_seconds or 0
    ) + sub.response_time_seconds

    db.commit()
    return {"status": "saved"}


# =========================
# SUBMIT QUIZ
# =========================
@router.post("/quiz/{quiz_id}/submit", response_model=QuizResult)
def submit_quiz(
    quiz_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id,
    ).first()

    if not quiz or quiz.status != "in_progress":
        raise HTTPException(status_code=400, detail="Active quiz not found")

    now = datetime.utcnow()
    quiz.completed_at = min(now, quiz.expires_at)
    quiz.status = "completed"

    responses = db.query(Response).filter(
        Response.quiz_id == quiz_id
    ).all()

    answered = [r for r in responses if r.selected_option is not None]

    score = sum(1 for r in answered if r.is_correct)
    total_diff = sum(r.difficulty_at_attempt for r in answered)

    quiz.score = score
    quiz.accuracy = (score / quiz.total_questions * 100) if quiz.total_questions else 0
    quiz.average_difficulty = (
        total_diff / len(answered) if answered else 0
    )

    # =========================
    # UPDATE TOPIC STATS
    # =========================
    for r in answered:
        linked_topics = db.query(QuestionTopic).filter(
            QuestionTopic.question_id == r.question_id
        ).all()

        for qt in linked_topics:

            stat = db.query(UserTopicStat).filter(
                UserTopicStat.user_id == quiz.user_id,
                UserTopicStat.topic_id == qt.topic_id
            ).first()

            if not stat:
                stat = UserTopicStat(
                    user_id=quiz.user_id,
                    topic_id=qt.topic_id,
                    questions_attempted=0,
                    questions_correct=0
                )
                db.add(stat)

            stat.questions_attempted += 1

            previous_correct = db.query(Response).filter(
                Response.user_id == quiz.user_id,
                Response.question_id == r.question_id,
                Response.is_correct == True,
                Response.quiz_id != quiz.id
            ).first()

            if r.is_correct and not previous_correct:
                stat.questions_correct += 1

            stat.last_practiced = quiz.completed_at

    db.commit()
    db.refresh(quiz)

    return QuizResult(
        id=quiz.id,
        score=quiz.score,
        accuracy=quiz.accuracy,
        completed_at=quiz.completed_at
    )


# =========================
# SEED DATA
# =========================
@router.post("/seed-dummy-data")
def seed_data(db: Session = Depends(get_db)):

    topic = Topic(name="Algebra", description="Basic Math")
    db.add(topic)
    db.commit()
    db.refresh(topic)

    questions = []

    for i in range(15):
        q = Question(
            question_text=f"Dummy Question {i}",
            options=["A", "B", "C", "D"],
            correct_option="A",
            question_type="MCQ",
            difficulty_level=(i % 3) + 1
        )
        db.add(q)
        db.flush()  # gets ID without commit

        qt = QuestionTopic(
            question_id=q.id,
            topic_id=topic.id
        )
        db.add(qt)

    db.commit()

    return {"message": "Database seeded with 15 questions!"}