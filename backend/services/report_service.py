from datetime import datetime
from bson import ObjectId
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from backend.database import users_col, reports_col
from backend.services.analytics_service import get_user_analytics

RECOMMENDATIONS = {
    "email": [
        "Always verify the sender's email domain matches the company's official domain.",
        "Hover over links before clicking — phishing URLs often mimic real ones with subtle typos.",
        "Legitimate organisations never ask for passwords via email.",
    ],
    "sms": [
        "Banks and services never ask you to reply with account details via SMS.",
        "Be suspicious of SMS links — type the URL directly into your browser instead.",
        "Urgency language ('Act now!', 'Your account will be closed') is a classic SMS phishing tactic.",
    ],
    "url": [
        "Check for HTTPS AND verify the domain — padlock alone does not guarantee safety.",
        "Watch for homograph attacks: 'paypa1.com' vs 'paypal.com'.",
        "Use a URL reputation tool (e.g., VirusTotal) before visiting unfamiliar links.",
    ],
    "voice": [
        "Never give personal or financial information to an unsolicited caller.",
        "Hang up and call back using the official number from the company's website.",
        "AI voice cloning can impersonate known contacts — verify via a separate channel.",
    ],
}

def generate_report(user_id: str) -> dict:
    user = users_col.find_one({"_id": ObjectId(user_id)})
    analytics = get_user_analytics(user_id)
    weakest = analytics.get("weakest_category", "email")

    report = {
        "user_id": ObjectId(user_id),
        "user_name": user["name"],
        "generated_at": datetime.utcnow(),
        "overall_score": user.get("score", 0),
        "overall_accuracy_pct": analytics.get("overall_accuracy_pct", 0),
        "accuracy_by_type": analytics.get("accuracy_by_type", {}),
        "weakest_category": weakest,
        "avg_response_time_sec": analytics.get("avg_response_time_sec", 0),
        "recommendations": RECOMMENDATIONS.get(weakest, RECOMMENDATIONS["email"]),
    }

    reports_col.insert_one(report)
    report["id"] = str(report.pop("_id"))
    report["user_id"] = str(report["user_id"])
    return report

def generate_pdf(report: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Phishing Awareness Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Trainee: {report['user_name']}", styles["Normal"]))
    story.append(Paragraph(f"Generated: {report['generated_at']}", styles["Normal"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Overall Performance", styles["Heading2"]))
    perf_data = [
        ["Metric", "Value"],
        ["Total Score", str(report["overall_score"])],
        ["Overall Accuracy", f"{report['overall_accuracy_pct']}%"],
        ["Avg Response Time", f"{report['avg_response_time_sec']}s"],
        ["Weakest Category", report["weakest_category"].upper()],
    ]
    t = Table(perf_data, colWidths=[200, 200])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A73E8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F3F4")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DADCE0")),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Accuracy by Category", styles["Heading2"]))
    acc_data = [["Category", "Accuracy"]] + [
        [k.upper(), f"{v}%"] for k, v in report.get("accuracy_by_type", {}).items()
    ]
    t2 = Table(acc_data, colWidths=[200, 200])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34A853")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F3F4")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DADCE0")),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t2)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Recommendations", styles["Heading2"]))
    for rec in report.get("recommendations", []):
        story.append(Paragraph(f"• {rec}", styles["Normal"]))
        story.append(Spacer(1, 6))

    doc.build(story)
    return buf.getvalue()
