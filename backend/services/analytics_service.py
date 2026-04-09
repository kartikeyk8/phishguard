import pandas as pd
import numpy as np
from bson import ObjectId
from backend.database import results_col, questions_col

def get_user_analytics(user_id: str) -> dict:
    records = list(results_col.find({"user_id": ObjectId(user_id)}))
    if not records:
        return {"message": "No quiz data yet"}

    df = pd.DataFrame(records)

    # Enrich with question type
    q_ids = df["question_id"].unique().tolist()
    q_map = {
        str(q["_id"]): q["type"]
        for q in questions_col.find({"_id": {"$in": q_ids}})
    }
    df["type"] = df["question_id"].apply(lambda x: q_map.get(str(x), "unknown"))

    # Accuracy per category
    accuracy_by_type = (
        df.groupby("type")["correct"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "correct", "count": "total"})
    )
    accuracy_by_type["accuracy_pct"] = (
        accuracy_by_type["correct"] / accuracy_by_type["total"] * 100
    ).round(1)

    # Weakest category
    weakest = accuracy_by_type["accuracy_pct"].idxmin()

    # Average response times
    avg_time_by_type = df.groupby("type")["time_taken"].mean().round(2).to_dict()

    # Overall stats
    overall_accuracy = round(df["correct"].mean() * 100, 1)
    avg_response_time = round(float(np.mean(df["time_taken"])), 2)

    return {
        "overall_accuracy_pct": overall_accuracy,
        "avg_response_time_sec": avg_response_time,
        "weakest_category": weakest,
        "accuracy_by_type": accuracy_by_type["accuracy_pct"].to_dict(),
        "avg_time_by_type": avg_time_by_type,
        "total_questions_answered": len(df),
    }
