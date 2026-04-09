from pydantic import BaseModel
from typing import List

class AnswerSubmit(BaseModel):
    question_id: str
    user_answer: str
    time_taken: float  # seconds

class QuizSubmit(BaseModel):
    difficulty: str
    answers: List[AnswerSubmit]

class QuizResult(BaseModel):
    total_questions: int
    correct: int
    incorrect: int
    score: int
    percentage: float
    passed: bool
    next_level: str
    details: list
