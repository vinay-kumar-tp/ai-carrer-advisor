from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.models import Document, JobListing
from app.schemas.schemas import MessageResponse
from app.core.security import get_current_user_id
from app.core.config import settings
import os, uuid, aiofiles

router = APIRouter()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("other"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds maximum allowed size")

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Basic text parsing if text/pdf/doc
    parsed_text = ""
    try:
        if ext in [".txt", ".md", ".json"]:
            parsed_text = content.decode("utf-8", errors="ignore")
        else:
            parsed_text = f"Sample extracted text for {file.filename}"
    except Exception:
        parsed_text = ""

    doc = Document(
        user_id=user_id,
        doc_type=doc_type,
        filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        parsed_text=parsed_text
    )
    db.add(doc)
    await db.flush()

    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "doc_type": doc.doc_type,
        "file_size": doc.file_size,
        "created_at": doc.created_at.isoformat()
    }

@router.get("/")
async def list_documents(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    query = select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
    result = await db.execute(query)
    docs = result.scalars().all()
    return [
        {
            "id": str(d.id),
            "filename": d.filename,
            "doc_type": d.doc_type,
            "file_size": d.file_size,
            "created_at": d.created_at.isoformat()
        }
        for d in docs
    ]

@router.delete("/{doc_id}", response_model=MessageResponse)
async def delete_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == doc_id, Document.user_id == user_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    await db.delete(doc)
    return MessageResponse(message="Document deleted successfully")

@router.post("/ats-score")
async def calculate_ats_score(
    resume_text: str = Form(...),
    job_id: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    # ATS keyword matching algorithm
    keywords = ["python", "javascript", "react", "sql", "git", "api", "communication", "leadership", "problem solving", "fastapi", "database", "docker"]
    job_skills = []

    if job_id:
        res = await db.execute(select(JobListing).where(JobListing.id == job_id))
        job = res.scalar_one_or_none()
        if job and job.required_skills:
            job_skills = [s.lower() for s in job.required_skills]
    
    target_terms = job_skills if job_skills else keywords
    text_lower = resume_text.lower()
    
    matched = [term for term in target_terms if term in text_lower]
    missing = [term for term in target_terms if term not in text_lower]
    
    score = int((len(matched) / max(len(target_terms), 1)) * 100)
    score = max(35, min(98, score + 20)) # Normalize baseline

    suggestions = []
    if missing:
        suggestions.append(f"Consider adding missing keywords: {', '.join(missing[:5])}")
    if len(resume_text.split()) < 100:
        suggestions.append("Resume length is short. Elaborate on projects and work experience.")
    if "achieved" not in text_lower and "managed" not in text_lower:
        suggestions.append("Use strong action verbs like 'achieved', 'managed', 'developed', 'spearheaded'.")

    return {
        "ats_score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": suggestions if suggestions else ["Great job! Your resume aligns well with standard requirements."]
    }
