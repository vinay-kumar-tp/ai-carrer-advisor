"""Document Vault — upload, serve/preview, manage and AI-optimize documents."""

from __future__ import annotations

import mimetypes
import os
import uuid

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.models import Document, JobListing
from app.schemas.schemas import (
    DocumentLabelUpdate,
    MessageResponse,
    ResumeOptimizeRequest,
)
from app.services import doc_extract, resume_optimizer

router = APIRouter()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Human labels for the vault groups.
DOC_TYPE_LABELS = {
    "resume": "Resume",
    "transcript": "Marksheet / Transcript",
    "certificate": "Certificate",
    "cover_letter": "Cover Letter",
    "portfolio": "Portfolio",
    "project": "Project Document",
    "id_proof": "ID Proof",
    "offer_letter": "Offer Letter",
    "other": "Other",
}

ALLOWED_EXT = {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".png", ".jpg", ".jpeg", ".webp"}


def _serialize(doc: Document) -> dict:
    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "label": doc.label or doc.filename,
        "doc_type": doc.doc_type,
        "type_label": DOC_TYPE_LABELS.get(doc.doc_type, "Other"),
        "file_size": doc.file_size,
        "is_public": bool(doc.is_public),
        "has_text": bool((doc.parsed_text or "").strip()) and not (doc.parsed_text or "").startswith("Sample extracted"),
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "download_url": f"/api/documents/{doc.id}/file",
    }


async def _own_doc(db: AsyncSession, doc_id: str, user_id: str) -> Document:
    doc = (
        await db.execute(select(Document).where(Document.id == doc_id, Document.user_id == user_id))
    ).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


# ─── Upload ──────────────────────────────────────────────────────

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("other"),
    label: str = Form(""),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext and ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds maximum allowed size")

    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Real text extraction (PDF/DOCX/TXT); empty for images / legacy .doc.
    parsed_text = doc_extract.extract_text(file.filename or "", content)

    doc = Document(
        user_id=user_id,
        doc_type=doc_type if doc_type in DOC_TYPE_LABELS else "other",
        filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        parsed_text=parsed_text,
        label=(label or "").strip() or (file.filename or "Document"),
    )
    db.add(doc)
    await db.flush()
    return _serialize(doc)


# ─── List ────────────────────────────────────────────────────────

@router.get("/")
async def list_documents(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    docs = (
        await db.execute(
            select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        )
    ).scalars().all()
    return [_serialize(d) for d in docs]


@router.get("/doc-types")
async def document_types():
    return [{"value": k, "label": v} for k, v in DOC_TYPE_LABELS.items()]


# ─── Serve / preview file (inline, auth-guarded) ─────────────────

@router.get("/{doc_id}/file")
async def get_document_file(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    doc = await _own_doc(db, doc_id, user_id)
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File is missing from storage")
    with open(doc.file_path, "rb") as handle:
        payload = handle.read()
    media = mimetypes.guess_type(doc.filename or "")[0] or "application/octet-stream"
    return Response(
        content=payload,
        media_type=media,
        headers={"Content-Disposition": f'inline; filename="{doc.filename}"'},
    )


# ─── Rename ──────────────────────────────────────────────────────

@router.put("/{doc_id}/label")
async def rename_document(
    doc_id: str,
    data: DocumentLabelUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    doc = await _own_doc(db, doc_id, user_id)
    doc.label = (data.label or "").strip() or doc.filename
    await db.flush()
    return _serialize(doc)


# ─── Delete ──────────────────────────────────────────────────────

@router.delete("/{doc_id}", response_model=MessageResponse)
async def delete_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    doc = await _own_doc(db, doc_id, user_id)
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass
    await db.delete(doc)
    return MessageResponse(message="Document deleted successfully")


# ─── AI resume optimization for a target job ─────────────────────

@router.post("/{doc_id}/optimize")
async def optimize_document(
    doc_id: str,
    data: ResumeOptimizeRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    doc = await _own_doc(db, doc_id, user_id)

    resume_text = (doc.parsed_text or "").strip()
    if resume_text.startswith("Sample extracted"):
        resume_text = ""
    if not doc_extract.looks_like_resume_text(resume_text):
        raise HTTPException(
            status_code=400,
            detail="Could not read text from this document. Upload a text-based PDF, DOCX or TXT resume to optimize it.",
        )

    # Resolve job context from an explicit job or free-form title/description.
    job_context: dict = {
        "title": data.job_title or "",
        "description": data.job_description or "",
        "skills": data.skills or [],
    }
    if data.job_id:
        job = (await db.execute(select(JobListing).where(JobListing.id == data.job_id))).scalar_one_or_none()
        if job:
            job_context = {
                "title": job.title,
                "description": job.description or "",
                "skills": [s for s in (job.required_skills or [])],
            }
    if not (job_context["title"] or job_context["description"] or job_context["skills"]):
        raise HTTPException(status_code=400, detail="Provide a job to optimize against.")

    report = await resume_optimizer.optimize_resume(resume_text, job_context)
    report["document"] = {"id": str(doc.id), "label": doc.label or doc.filename}
    report["job"] = {"title": job_context["title"], "skills": job_context["skills"]}
    return report
