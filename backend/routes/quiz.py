from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from backend.utils.dependencies import get_current_user
from backend.services.gemini_service import generate_questions
from backend.services.quiz_service import store_questions, score_quiz
from backend.services.email_simulation import send_phishing_email
from backend.services.sms_simulation import send_phishing_sms
from backend.services.url_analysis import analyse_url

router = APIRouter()


class AnswerSubmit(BaseModel):
    question_id: str
    user_answer: str
    time_taken: float

class QuizSubmit(BaseModel):
    difficulty: str
    phishing_type: str
    session_key: str
    answers: List[AnswerSubmit]

class URLRequest(BaseModel):
    url: str


@router.get("/questions/{difficulty}/{phishing_type}")
def get_questions(difficulty: str, phishing_type: str, current_user=Depends(get_current_user)):
    if difficulty not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(400, "Invalid difficulty")
    if phishing_type not in ["email", "sms", "url", "voice"]:
        raise HTTPException(400, "Invalid phishing type")

    # Generate fresh questions from Gemini
    questions   = generate_questions(difficulty, phishing_type, count=5)
    session_key = f"{current_user['id']}_{difficulty}_{phishing_type}"
    store_questions(session_key, questions)

    # Trigger real simulation
    simulation = None
    if phishing_type == "email":
        simulation = send_phishing_email(
            to_email   = current_user["email"],
            difficulty = difficulty,
            user_name  = current_user["name"],
        )
    elif phishing_type == "sms":
        simulation = send_phishing_sms(
            to_phone   = current_user.get("phone", ""),
            difficulty = difficulty,
        )

    # Strip correct_answer before sending to client
    client_qs = [{k: v for k, v in q.items() if k != "correct_answer"} for q in questions]

    return {
        "questions":   client_qs,
        "difficulty":  difficulty,
        "type":        phishing_type,
        "session_key": session_key,
        "simulation":  simulation,
        "total":       len(client_qs),
    }


@router.post("/submit")
def submit(body: QuizSubmit, current_user=Depends(get_current_user)):
    result = score_quiz(
        user_id      = current_user["id"],
        difficulty   = body.difficulty,
        phishing_type= body.phishing_type,
        answers      = body.answers,
        session_key  = body.session_key,
    )
    return result


@router.post("/analyse-url")
def analyse(body: URLRequest, current_user=Depends(get_current_user)):
    if not body.url or len(body.url) < 4:
        raise HTTPException(400, "Please provide a valid URL")
    return analyse_url(body.url)
