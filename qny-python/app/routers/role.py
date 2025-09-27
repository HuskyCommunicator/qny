from fastapi import APIRouter, Query, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import json

from ..core.db import get_db
from ..models.chat import RoleTemplate
from ..schemas.role import RoleInfo, RoleTemplateCreate, RoleTemplateUpdate, RoleTemplateOut
from ..services.oss_service import get_oss_service

# 导入 prompt_templates
try:
    import sys
    import os
    # 添加 backend 目录到 Python 路径
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    from prompt_templates import ROLE_PROMPTS, BUILTIN_ROLES
except ImportError as e:
    print(f"[WARNING] Failed to import prompt_templates: {e}")
    # 如果导入失败，提供默认值
    ROLE_PROMPTS = {}
    BUILTIN_ROLES = {}


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
        # 如果 OSS 不可用，返回错误信息
        raise HTTPException(status_code=503, detail=f"文件上传服务不可用: {str(e)}")


@router.get("/search", response_model=list[RoleInfo])
def search_roles(q: str = Query(""), db: Session = Depends(get_db)):
    """搜索角色，返回丰富的角色信息"""
    try:
        print(f"[DEBUG] Searching roles with query: '{q}'")
        print(f"[DEBUG] BUILTIN_ROLES keys: {list(BUILTIN_ROLES.keys())}")
        
        q_lower = q.lower()
        results = []
        
        # 搜索内置角色
        for name, info in BUILTIN_ROLES.items():
            if q_lower in name.lower() or q_lower in info["display_name"].lower():
                print(f"[DEBUG] Found builtin role: {name}")
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
        
        # 搜索自定义角色（暂时跳过，因为数据库表结构可能未更新）
        try:
            customs = db.query(RoleTemplate).filter(RoleTemplate.name.like(f"%{q}%")).all()
            print(f"[DEBUG] Found {len(customs)} custom roles")
            for custom in customs:
                skills = json.loads(custom.skills) if custom.skills else None
                results.append(RoleInfo(
                    name=custom.name,
                    display_name=getattr(custom, 'display_name', None),
                    description=getattr(custom, 'description', None),
                    avatar_url=getattr(custom, 'avatar_url', None),
                    skills=skills,
                    background=getattr(custom, 'background', None),
                    personality=getattr(custom, 'personality', None),
                    is_builtin=False
                ))
        except Exception as db_error:
            print(f"[WARNING] Custom roles query failed (table structure may need update): {db_error}")
            # 继续执行，只返回内置角色
        
        print(f"[DEBUG] Returning {len(results)} results")
        return results
        
    except Exception as e:
        print(f"[ERROR] Role search failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"角色搜索失败: {str(e)}")


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


