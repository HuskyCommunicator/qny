from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from ..services.rag_service import rag, rebuild_from_db
from ..core.db import get_db
from ..models.chat import Document
from ..services.doc_service import extract_text_from_pdf, extract_text_from_markdown, chunk_text


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/index")
def index_docs(doc_ids: List[str], documents: List[str], db: Session = Depends(get_db)):
    if len(doc_ids) != len(documents):
        return {"ok": False, "message": "doc_ids 与 documents 长度不一致"}
    # 写入/更新数据库
    for i, d_id in enumerate(doc_ids):
        text = documents[i]
        existed = db.query(Document).filter(Document.doc_id == d_id).first()
        if existed:
            existed.text = text
        else:
            db.add(Document(doc_id=d_id, text=text))
    db.commit()
    # 从 DB 重建索引
    rows = db.query(Document.doc_id, Document.text).all()
    rebuild_from_db(rows)
    return {"ok": True, "count": len(doc_ids)}


@router.post("/upsert")
def upsert_docs(doc_ids: List[str], documents: List[str], db: Session = Depends(get_db)):
    if len(doc_ids) != len(documents):
        return {"ok": False, "message": "doc_ids 与 documents 长度不一致"}
    for i, d_id in enumerate(doc_ids):
        text = documents[i]
        existed = db.query(Document).filter(Document.doc_id == d_id).first()
        if existed:
            existed.text = text
        else:
            db.add(Document(doc_id=d_id, text=text))
    db.commit()
    rows = db.query(Document.doc_id, Document.text).all()
    rebuild_from_db(rows)
    return {"ok": True, "count": len(doc_ids)}


@router.post("/delete")
def delete_docs(doc_ids: List[str], db: Session = Depends(get_db)):
    q = db.query(Document).filter(Document.doc_id.in_(doc_ids))
    deleted = q.delete(synchronize_session=False)
    db.commit()
    rows = db.query(Document.doc_id, Document.text).all()
    rebuild_from_db(rows)
    return {"ok": True, "deleted": int(deleted)}


@router.post("/upload")
async def upload_and_index(file: UploadFile = File(...), prefix: str = "upload/", chunk_size: int = 600, db: Session = Depends(get_db)):
    data = await file.read()
    name = file.filename or "file"
    ext = (name.rsplit(".", 1)[-1] or "").lower()
    if ext in ("pdf",):
        text = extract_text_from_pdf(data)
    elif ext in ("md", "markdown"):
        text = extract_text_from_markdown(data)
    else:
        # 默认尝试按 UTF-8 文本解析
        text = data.decode("utf-8", errors="ignore")
    chunks = chunk_text(text, max_len=chunk_size)
    ids = [f"{prefix}{name}#p{i+1}" for i in range(len(chunks))]
    # upsert 到 DB
    for i, d_id in enumerate(ids):
        txt = chunks[i]
        existed = db.query(Document).filter(Document.doc_id == d_id).first()
        if existed:
            existed.text = txt
        else:
            db.add(Document(doc_id=d_id, text=txt))
    db.commit()
    rows = db.query(Document.doc_id, Document.text).all()
    rebuild_from_db(rows)
    return {"ok": True, "count": len(ids), "doc_ids": ids}


@router.post("/search")
def search_docs(query: str, top_k: int = 3):
    hits = rag.search(query, top_k=top_k)
    return {"hits": [{"doc_id": d, "text": t, "score": s} for d, t, s in hits]}


