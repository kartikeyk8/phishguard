"""
Gemini Service — generates fresh quiz questions per level and phishing type
"""
import json
import re
import google.generativeai as genai
from backend.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

DIFFICULTY_DESCRIPTIONS = {
    "beginner":     "simple and obvious — red flags should be easy to spot for a first-time user",
    "intermediate": "moderately complex — requires some knowledge of phishing tactics",
    "advanced":     "sophisticated and realistic — spear phishing, homograph domains, CEO fraud, AI voice cloning",
}

TYPE_CONTEXTS = {
    "email": "a realistic-looking phishing email showing From address, Subject line, and full email body",
    "sms":   "a realistic phishing SMS message showing sender ID and full message text",
    "url":   "a suspicious URL the user must analyse to determine if it is phishing or legitimate",
    "voice": "a realistic transcript of a vishing phone call the user must evaluate",
}


def generate_questions(difficulty: str, phishing_type: str, count: int = 5) -> list:
    diff_desc = DIFFICULTY_DESCRIPTIONS.get(difficulty, "moderate")
    type_ctx  = TYPE_CONTEXTS.get(phishing_type, "a phishing scenario")

    prompt = f"""You are a cybersecurity training expert creating phishing awareness quiz questions.

Generate exactly {count} quiz questions about {phishing_type} phishing at {difficulty} level.
Difficulty: {diff_desc}
Each question should present: {type_ctx}

Return ONLY a valid JSON array. No markdown, no backticks, no extra text.
Each object must have exactly these fields:
{{
  "content": "the full scenario text shown to the user — make it realistic and detailed",
  "options": ["option A", "option B", "option C", "option D"],
  "correct_answer": "exact text of correct option",
  "explanation": "clear explanation of why this is phishing and what the red flags are",
  "type": "{phishing_type}"
}}

Rules:
- Use realistic company names, domains, phone numbers, email addresses
- For email type: always include From: address, Subject:, and full email body text
- For sms type: include sender name and full SMS text with a suspicious link
- For url type: show a full URL and ask the user to identify if it is phishing
- For voice type: write a realistic call transcript with urgency and manipulation tactics
- The correct_answer must be word-for-word identical to one of the 4 options
- Make wrong options plausible so users have to think carefully
- Difficulty {difficulty}: {diff_desc}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)

        questions = json.loads(text)
        validated = []
        for i, q in enumerate(questions):
            if all(k in q for k in ["content", "options", "correct_answer", "explanation"]):
                q["id"]         = f"gemini_{phishing_type}_{difficulty}_{i}"
                q["type"]       = phishing_type
                q["difficulty"] = difficulty
                validated.append(q)

        return validated if validated else _fallback(difficulty, phishing_type)

    except Exception as e:
        print(f"Gemini error: {e}")
        return _fallback(difficulty, phishing_type)


def _fallback(difficulty: str, phishing_type: str) -> list:
    return [{
        "id":           f"fallback_{phishing_type}_{difficulty}_0",
        "type":         phishing_type,
        "difficulty":   difficulty,
        "content":      f"You receive a suspicious {phishing_type} message asking you to verify your account urgently by clicking a link. What do you do?",
        "options":      [
            "Click the link immediately to avoid account suspension",
            "Ignore it and verify directly through the official website",
            "Reply with your account details to confirm your identity",
            "Forward it to all your contacts as a warning",
        ],
        "correct_answer": "Ignore it and verify directly through the official website",
        "explanation":    "Always go directly to the official website rather than clicking any link in a suspicious message.",
    }]
