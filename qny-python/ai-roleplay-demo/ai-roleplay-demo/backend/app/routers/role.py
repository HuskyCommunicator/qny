from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from prompt_templates import ROLE_PROMPTS
from ..core.db import get_db
from ..models.chat import RoleTemplate


router = APIRouter(prefix="/role", tags=["role"])


@router.get("/search")
def search_roles(q: str = Query("") , db: Session = Depends(get_db)):
    q_lower = q.lower()
    builtin = [name for name in ROLE_PROMPTS.keys() if q_lower in name.lower()]
    customs = db.query(RoleTemplate.name).filter(RoleTemplate.name.like(f"%{q}%")).all()
    custom_names = [r[0] for r in customs]
    return {"results": list(dict.fromkeys(builtin + custom_names))}


@router.get("/template/{name}")
def get_role_template(name: str, db: Session = Depends(get_db)):
    template = ROLE_PROMPTS.get(name)
    if template is None:
        row = db.query(RoleTemplate).filter(RoleTemplate.name == name).first()
        if row:
            template = row.prompt
    return {"name": name, "template": template}


@router.post("/template")
def upsert_role_template(name: str, prompt: str, db: Session = Depends(get_db)):
    existed = db.query(RoleTemplate).filter(RoleTemplate.name == name).first()
    if existed:
        existed.prompt = prompt
    else:
        db.add(RoleTemplate(name=name, prompt=prompt))
    db.commit()
    return {"ok": True, "name": name}


