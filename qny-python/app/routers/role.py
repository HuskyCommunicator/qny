from fastapi import APIRouter, Query, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import json

from prompt_templates import ROLE_PROMPTS, BUILTIN_ROLES
from ..core.db import get_db
from ..models.chat import RoleTemplate
from ..schemas.role import RoleInfo, RoleTemplateCreate, RoleTemplateUpdate, RoleTemplateOut
from ..services.oss_service import get_oss_service


router = APIRouter(prefix="/role", tags=["role"])


@router.post("/upload-avatar")
async def upload_avatar(file: UploadFile = File(...)):
    """上传角色头像"""
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    
    # 验证文件大小 (5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")
    
    try:
        oss_service = get_oss_service()
        avatar_url = await oss_service.upload_file(file, folder="avatars")
        return {"avatar_url": avatar_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/search", response_model=list[RoleInfo])
def search_roles(q: str = Query(""), db: Session = Depends(get_db)):
    """搜索角色，返回丰富的角色信息"""
    q_lower = q.lower()
    results = []
    
    # 搜索内置角色
    for name, info in BUILTIN_ROLES.items():
        if q_lower in name.lower() or q_lower in info["display_name"].lower():
            results.append(RoleInfo(
                name=name,
                display_name=info["display_name"],
                description=info["description"],
                avatar_url=info["avatar_url"],
                skills=info["skills"],
                background=info["background"],
                personality=info["personality"],
                is_builtin=True
            ))
    
    # 搜索自定义角色
    customs = db.query(RoleTemplate).filter(RoleTemplate.name.like(f"%{q}%")).all()
    for custom in customs:
        skills = json.loads(custom.skills) if custom.skills else None
        results.append(RoleInfo(
            name=custom.name,
            display_name=custom.display_name,
            description=custom.description,
            avatar_url=custom.avatar_url,
            skills=skills,
            background=custom.background,
            personality=custom.personality,
            is_builtin=False
        ))
    
    return results


@router.get("/template/{name}", response_model=RoleInfo)
def get_role_template(name: str, db: Session = Depends(get_db)):
    """获取角色模板，返回完整的角色信息"""
    # 先检查内置角色
    if name in BUILTIN_ROLES:
        info = BUILTIN_ROLES[name]
        return RoleInfo(
            name=name,
            display_name=info["display_name"],
            description=info["description"],
            avatar_url=info["avatar_url"],
            skills=info["skills"],
            background=info["background"],
            personality=info["personality"],
            is_builtin=True
        )
    
    # 检查自定义角色
    row = db.query(RoleTemplate).filter(RoleTemplate.name == name).first()
    if row:
        skills = json.loads(row.skills) if row.skills else None
        return RoleInfo(
            name=row.name,
            display_name=row.display_name,
            description=row.description,
            avatar_url=row.avatar_url,
            skills=skills,
            background=row.background,
            personality=row.personality,
            is_builtin=False
        )
    
    raise HTTPException(status_code=404, detail="角色不存在")


@router.get("/template/{name}/prompt")
def get_role_prompt(name: str, db: Session = Depends(get_db)):
    """获取角色 Prompt 模板（仅返回 prompt 文本）"""
    template = ROLE_PROMPTS.get(name)
    if template is None:
        row = db.query(RoleTemplate).filter(RoleTemplate.name == name).first()
        if row:
            template = row.prompt
        else:
            raise HTTPException(status_code=404, detail="角色不存在")
    return {"name": name, "prompt": template}


@router.post("/template", response_model=RoleTemplateOut)
def create_role_template(payload: RoleTemplateCreate, db: Session = Depends(get_db)):
    """创建角色模板"""
    existed = db.query(RoleTemplate).filter(RoleTemplate.name == payload.name).first()
    if existed:
        raise HTTPException(status_code=400, detail="角色名称已存在")
    
    skills_json = json.dumps(payload.skills) if payload.skills else None
    role = RoleTemplate(
        name=payload.name,
        prompt=payload.prompt,
        display_name=payload.display_name,
        description=payload.description,
        avatar_url=payload.avatar_url,
        skills=skills_json,
        background=payload.background,
        personality=payload.personality
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.put("/template/{name}", response_model=RoleTemplateOut)
def update_role_template(name: str, payload: RoleTemplateUpdate, db: Session = Depends(get_db)):
    """更新角色模板"""
    role = db.query(RoleTemplate).filter(RoleTemplate.name == name).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if payload.prompt is not None:
        role.prompt = payload.prompt
    if payload.display_name is not None:
        role.display_name = payload.display_name
    if payload.description is not None:
        role.description = payload.description
    if payload.avatar_url is not None:
        role.avatar_url = payload.avatar_url
    if payload.skills is not None:
        role.skills = json.dumps(payload.skills)
    if payload.background is not None:
        role.background = payload.background
    if payload.personality is not None:
        role.personality = payload.personality
    
    db.commit()
    db.refresh(role)
    return role


