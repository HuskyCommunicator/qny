from fastapi import APIRouter, Query

from prompt_templates import TEMPLATES


router = APIRouter(prefix="/role", tags=["role"])


@router.get("/search")
def search_roles(q: str = Query("") ):
    q_lower = q.lower()
    results = [name for name in TEMPLATES.keys() if q_lower in name.lower()]
    return {"results": results}


@router.get("/template/{name}")
def get_role_template(name: str):
    template = TEMPLATES.get(name)
    return {"name": name, "template": template}


