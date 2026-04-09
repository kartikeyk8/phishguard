from pydantic import BaseModel
from typing import List, Optional

class PhishingQuestion(BaseModel):
    type: str          # email | sms | url | voice
    content: str       # The question body / scenario
    options: List[str] # 4 answer choices
    correct_answer: str
    difficulty: str    # beginner | intermediate | advanced
    explanation: str   # Why it is/isn't phishing

class QuestionOut(PhishingQuestion):
    id: str
