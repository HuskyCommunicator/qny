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


from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.db import get_db
from app.core.security import get_current_user
from app.models import User, Role, UserRole
from app.schemas import (
    RoleCreate, RoleUpdate, RoleOut, RoleList, RoleSearchParams,
    UserRoleCreate, UserRoleUpdate, UserRoleOut, RoleTemplate
)
from app.utils.logger import get_logger

router = APIRouter(prefix="/role", tags=["role"])
logger = get_logger(__name__)


@router.post("/create", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新角色"""
    # 检查角色名称是否已存在
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名称已存在"
        )

    # 创建角色
    role = Role(
        name=role_data.name,
        description=role_data.description,
        system_prompt=role_data.system_prompt,
        avatar_url=role_data.avatar_url,
        is_public=role_data.is_public,
        config=role_data.config,
        tags=role_data.tags,
        category=role_data.category,
        created_by=current_user.id
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    logger.info(f"用户 {current_user.username} 创建了角色: {role.name}")
    return role


@router.put("/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新角色信息"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    # 检查权限：只有创建者或管理员可以更新
    if role.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限更新此角色"
        )

    # 更新字段
    update_data = role_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)

    db.commit()
    db.refresh(role)

    logger.info(f"用户 {current_user.username} 更新了角色: {role.name}")
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    # 检查权限：只有创建者或管理员可以删除
    if role.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此角色"
        )

    # 软删除：设置为不活跃
    role.is_active = False
    db.commit()

    logger.info(f"用户 {current_user.username} 删除了角色: {role.name}")


@router.get("/detail/{role_id}", response_model=RoleOut)
async def get_role(role_id: int, db: Session = Depends(get_db)):
    """获取角色详情"""
    role = db.query(Role).filter(
        and_(Role.id == role_id, Role.is_active == True)
    ).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return role


@router.get("/list", response_model=RoleList)
async def get_role_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """获取角色列表"""
    # 构建查询条件
    query = db.query(Role).filter(Role.is_active == True)

    if is_public is not None:
        query = query.filter(Role.is_public == is_public)

    if category:
        query = query.filter(Role.category == category)

    # 获取总数
    total = query.count()

    # 分页查询
    roles = query.offset((page - 1) * size).limit(size).all()

    return RoleList(
        roles=roles,
        total=total,
        page=page,
        size=size
    )


@router.get("/search-roles", response_model=List[RoleOut])
async def search_roles(
    q: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    is_public: bool = Query(True),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """搜索角色"""
    query = db.query(Role).filter(Role.is_active == True)

    if is_public:
        query = query.filter(Role.is_public == True)

    # 关键词搜索
    if q:
        search_condition = or_(
            Role.name.contains(q),
            Role.description.contains(q),
            Role.system_prompt.contains(q)
        )
        query = query.filter(search_condition)

    # 分类筛选
    if category:
        query = query.filter(Role.category == category)

    # 标签筛选
    if tags:
        # 将逗号分隔的标签字符串转换为列表
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        for tag in tag_list:
            query = query.filter(Role.tags.contains([tag]))

    roles = query.limit(limit).all()
    return roles


# 用户智能体管理接口
@router.post("/my/add", response_model=UserRoleOut, status_code=status.HTTP_201_CREATED)
async def add_user_role(
    user_role_data: UserRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加角色到用户的智能体列表"""
    # 检查角色是否存在
    role = db.query(Role).filter(
        and_(Role.id == user_role_data.role_id, Role.is_active == True)
    ).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    # 检查是否已添加
    existing = db.query(UserRole).filter(
        and_(UserRole.user_id == current_user.id, UserRole.role_id == role.id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已添加该角色"
        )

    # 创建用户角色关系
    user_role = UserRole(
        user_id=current_user.id,
        role_id=role.id,
        custom_name=user_role_data.custom_name,
        custom_config=user_role_data.custom_config
    )

    db.add(user_role)
    db.commit()
    db.refresh(user_role)

    logger.info(f"用户 {current_user.username} 添加了角色: {role.name}")
    return user_role


@router.get("/my/list", response_model=List[UserRoleOut])
async def get_my_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的智能体列表"""
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == current_user.id
    ).all()

    return user_roles


@router.put("/my/{user_role_id}", response_model=UserRoleOut)
async def update_user_role(
    user_role_id: int,
    update_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户智能体配置"""
    user_role = db.query(UserRole).filter(
        and_(UserRole.id == user_role_id, UserRole.user_id == current_user.id)
    ).first()
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="智能体不存在"
        )

    # 更新字段
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user_role, field, value)

    db.commit()
    db.refresh(user_role)

    logger.info(f"用户 {current_user.username} 更新了智能体配置")
    return user_role


@router.delete("/my/{user_role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_role(
    user_role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除用户智能体"""
    user_role = db.query(UserRole).filter(
        and_(UserRole.id == user_role_id, UserRole.user_id == current_user.id)
    ).first()
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="智能体不存在"
        )

    db.delete(user_role)
    db.commit()

    logger.info(f"用户 {current_user.username} 删除了智能体")


# 角色模板管理接口
@router.get("/templates", response_model=List[RoleTemplate])
async def get_all_templates():
    """获取所有角色模板"""
    from prompt_templates import get_all_templates

    templates = get_all_templates()
    return list(templates.values())


@router.get("/templates/{template_name}", response_model=RoleTemplate)
async def get_template(template_name: str):
    """获取指定角色模板"""
    from prompt_templates import get_template

    template = get_template(template_name)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    return template


@router.get("/templates/by-category/{category}", response_model=List[RoleTemplate])
async def get_templates_by_category(category: str):
    """按分类获取角色模板"""
    from prompt_templates import get_templates_by_category

    templates = get_templates_by_category(category)
    return templates


@router.get("/templates/search", response_model=List[RoleTemplate])
async def search_templates(q: str = Query(..., min_length=1)):
    """搜索角色模板"""
    from prompt_templates import search_templates

    templates = search_templates(q)
    return templates


@router.post("/create-from-template/{template_name}", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
async def create_role_from_template(
    template_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从模板创建角色"""
    from prompt_templates import get_template

    template = get_template(template_name)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )

    # 检查角色名称是否已存在
    existing_role = db.query(Role).filter(Role.name == template.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名称已存在"
        )

    # 从模板创建角色
    role = Role(
        name=template.name,
        description=template.description,
        system_prompt=template.system_prompt,
        avatar_url=template.avatar_url,
        is_public=True,  # 从模板创建的角色默认为公开
        config=template.config,
        tags=template.tags,
        category=template.category,
        created_by=current_user.id
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    logger.info(f"用户 {current_user.username} 从模板创建了角色: {role.name}")
    return role


# 保留原有的模板接口（向后兼容）
@router.get("/template/{name}")
async def get_role_template_legacy(name: str):
    """获取角色模板（向后兼容）"""
    from prompt_templates import TEMPLATES

    template = TEMPLATES.get(name)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    return {"name": name, "template": template}
