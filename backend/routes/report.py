from fastapi import APIRouter, Depends
from fastapi.responses import Response
from backend.services.report_service import generate_report, generate_pdf
from backend.utils.dependencies import get_current_user

router = APIRouter()

@router.get("/generate")
def report(current_user=Depends(get_current_user)):
    return generate_report(current_user["id"])

@router.get("/download")
def download(current_user=Depends(get_current_user)):
    report_data = generate_report(current_user["id"])
    pdf_bytes = generate_pdf(report_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=awareness_report.pdf"}
    )
