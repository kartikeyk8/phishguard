from datetime import datetime
from bson import ObjectId
from backend.database import results_col, users_col

PASS_THRESHOLD = 70.0
CORRECT_POINTS = 10
WRONG_POINTS   = -5
LEVEL_ORDER    = ["beginner", "intermediate", "advanced"]

# In-memory session store: maps session_key -> questions list
_session = {}


def store_questions(session_key: str, questions: list):
    _session[session_key] = questions


def score_quiz(user_id: str, difficulty: str, phishing_type: str, answers: list, session_key: str) -> dict:
    questions = _session.get(session_key, [])
    q_map     = {q["id"]: q for q in questions}

    score   = 0
    correct = 0
    details = []

    for ans in answers:
        q = q_map.get(ans.question_id)
        if not q:
            continue
        is_correct = ans.user_answer.strip() == q["correct_answer"].strip()
        points     = CORRECT_POINTS if is_correct else WRONG_POINTS
        score     += points
        if is_correct:
            correct += 1

        results_col.insert_one({
            "user_id":     ObjectId(user_id),
            "question_id": ans.question_id,
            "type":        phishing_type,
            "difficulty":  difficulty,
            "user_answer": ans.user_answer,
            "correct":     is_correct,
            "time_taken":  ans.time_taken,
            "score":       points,
            "created_at":  datetime.utcnow(),
        })

        details.append({
            "question_id":    ans.question_id,
            "correct":        is_correct,
            "correct_answer": q["correct_answer"],
            "explanation":    q.get("explanation", ""),
            "points":         points,
        })

    total      = len(answers)
    percentage = round((correct / total * 100) if total else 0, 1)
    passed     = percentage >= PASS_THRESHOLD

    current_idx = LEVEL_ORDER.index(difficulty) if difficulty in LEVEL_ORDER else 0
    if passed and current_idx < len(LEVEL_ORDER) - 1:
        next_level = LEVEL_ORDER[current_idx + 1]
        users_col.update_one({"_id": ObjectId(user_id)},
                             {"$set": {"level": next_level}, "$inc": {"score": max(score, 0)}})
    else:
        users_col.update_one({"_id": ObjectId(user_id)},
                             {"$inc": {"score": max(score, 0)}})
        next_level = difficulty

    # Clear session
    _session.pop(session_key, None)

    return {
        "total_questions": total,
        "correct":         correct,
        "incorrect":       total - correct,
        "score":           score,
        "percentage":      percentage,
        "passed":          passed,
        "next_level":      "report" if (passed and difficulty == "advanced") else next_level,
        "details":         details,
    }
