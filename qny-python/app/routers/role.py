from fastapi import APIRouter, Query, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import json

from prompt_templates import ROLE_PROMPTS, BUILTIN_ROLES
from ..core.db import get_db
from ..models.role import Role
from ..models.user import User
from ..core.security import get_current_user
from ..schemas.role import RoleInfo, RoleTemplateCreate, RoleTemplateUpdate, RoleTemplateOut, RoleTemplate
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


@router.get("/list", response_model=list[RoleInfo])
def list_roles(db: Session = Depends(get_db)):
    """获取所有角色列表（包含数据库中的实际角色）"""
    results = []
    
    # 获取数据库中的所有公开角色
    db_roles = db.query(Role).filter(
        Role.is_public == True,
        Role.is_active == True
    ).all()
    
    for role in db_roles:
        # 解析技能和标签
        skills = []
        tags = []
        
        if role.skills:
            try:
                skills = json.loads(role.skills) if isinstance(role.skills, str) else role.skills
            except:
                skills = []
        
        if role.tags:
            try:
                tags = json.loads(role.tags) if isinstance(role.tags, str) else role.tags
            except:
                tags = []
        
        results.append(RoleInfo(
            id=role.id,
            name=role.name,
            display_name=role.display_name,
            description=role.description,
            avatar_url=role.avatar_url,
            skills=skills,
            background=role.background,
            personality=role.personality,
            category=role.category,
            tags=tags,
            is_builtin=False,
            is_public=role.is_public,
            created_at=role.created_at
        ))
    
    # 如果没有数据库角色，返回内置角色模板
    if not results:
        for name, info in BUILTIN_ROLES.items():
            results.append(RoleInfo(
                id=None,  # 内置角色没有ID
                name=name,
                display_name=info["display_name"],
                description=info["description"],
                avatar_url=info["avatar_url"],
                skills=info["skills"],
                background=info["background"],
                personality=info["personality"],
                category=info["category"],
                tags=info["tags"],
                is_builtin=True,
                is_public=True,
                created_at=None
            ))
    
    return results


@router.post("/create-from-template", response_model=RoleInfo)
def create_role_from_template(
    template_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从模板创建角色实例"""
    # 检查模板是否存在
    if template_name not in BUILTIN_ROLES:
        raise HTTPException(status_code=404, detail="角色模板不存在")
    
    template_info = BUILTIN_ROLES[template_name]
    
    # 检查是否已经创建过这个角色
    existing_role = db.query(Role).filter(
        Role.name == template_name,
        Role.created_by == current_user.id
    ).first()
    
    if existing_role:
        # 返回已存在的角色
        skills = []
        tags = []
        
        if existing_role.skills:
            try:
                skills = json.loads(existing_role.skills) if isinstance(existing_role.skills, str) else existing_role.skills
            except:
                skills = []
        
        if existing_role.tags:
            try:
                tags = json.loads(existing_role.tags) if isinstance(existing_role.tags, str) else existing_role.tags
            except:
                tags = []
        
        return RoleInfo(
            id=existing_role.id,
            name=existing_role.name,
            display_name=existing_role.display_name,
            description=existing_role.description,
            avatar_url=existing_role.avatar_url,
            skills=skills,
            background=existing_role.background,
            personality=existing_role.personality,
            category=existing_role.category,
            tags=tags,
            is_builtin=False,
            is_public=existing_role.is_public,
            created_at=existing_role.created_at
        )
    
    # 创建新角色
    new_role = Role(
        name=template_name,
        display_name=template_info["display_name"],
        description=template_info["description"],
        system_prompt=template_info.get("system_prompt", ""),
        avatar_url=template_info["avatar_url"],
        skills=json.dumps(template_info["skills"]) if template_info["skills"] else None,
        background=template_info["background"],
        personality=template_info["personality"],
        category=template_info["category"],
        tags=json.dumps(template_info["tags"]) if template_info["tags"] else None,
        is_public=True,
        is_active=True,
        created_by=current_user.id
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return RoleInfo(
        id=new_role.id,
        name=new_role.name,
        display_name=new_role.display_name,
        description=new_role.description,
        avatar_url=new_role.avatar_url,
        skills=template_info["skills"],
        background=new_role.background,
        personality=new_role.personality,
        category=new_role.category,
        tags=template_info["tags"],
        is_builtin=False,
        is_public=new_role.is_public,
        created_at=new_role.created_at
    )


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


