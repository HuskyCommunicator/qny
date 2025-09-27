import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException

try:
    import oss2
    OSS_AVAILABLE = True
except ImportError:
    OSS_AVAILABLE = False

from ..core.config import settings


class OSSService:
    def __init__(self):
        if not OSS_AVAILABLE:
            raise ImportError("oss2 package not installed. Run: pip install oss2")
        
        if not all([settings.oss_access_key_id, settings.oss_access_key_secret, 
                   settings.oss_endpoint, settings.oss_bucket_name]):
            raise ValueError("OSS configuration incomplete")
        
        auth = oss2.Auth(settings.oss_access_key_id, settings.oss_access_key_secret)
        self.bucket = oss2.Bucket(auth, settings.oss_endpoint, settings.oss_bucket_name)
        self.base_url = settings.oss_base_url or f"https://{settings.oss_bucket_name}.{settings.oss_endpoint.replace('https://', '')}"
    
    async def upload_file(self, file: UploadFile, folder: str = "avatars") -> str:
        """上传文件到 OSS，返回访问 URL"""
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        object_key = f"{folder}/{unique_filename}"
        
        # 读取文件内容
        content = await file.read()
        
        # 上传到 OSS
        result = self.bucket.put_object(object_key, content)
        
        if result.status == 200:
            return f"{self.base_url}/{object_key}"
        else:
            raise HTTPException(status_code=500, detail="文件上传失败")
    
    def delete_file(self, url: str) -> bool:
        """删除 OSS 文件"""
        try:
            # 从 URL 中提取 object_key
            object_key = url.replace(f"{self.base_url}/", "")
            result = self.bucket.delete_object(object_key)
            return result.status == 204
        except Exception:
            return False


# 全局 OSS 服务实例
oss_service: Optional[OSSService] = None

def get_oss_service() -> OSSService:
    """获取 OSS 服务实例"""
    global oss_service
    if oss_service is None:
        try:
            oss_service = OSSService()
        except (ImportError, ValueError) as e:
            raise HTTPException(status_code=500, detail=f"OSS 服务不可用: {str(e)}")
    return oss_service
