import os
from typing import Optional

from dotenv import load_dotenv


# 读取 .env 配置
load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "AI Roleplay Backend")
        self.environment: str = os.getenv("ENV", "development")
        self.secret_key: str = os.getenv("SECRET_KEY", "change-this-in-production")
        self.algorithm: str = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

        # 数据库配置（默认使用 MySQL 示例；若未设置则回退至 sqlite）
        default_mysql = "mysql+pymysql://user:password@localhost:3307/qny_db?charset=utf8mb4"
        self.database_url: str = os.getenv("DATABASE_URL", default_mysql)

        # 外部 API Key（如需）
        self.api_key: Optional[str] = os.getenv("API_KEY")

        # CORS
        self.cors_allow_origins: list[str] = [
            origin.strip() for origin in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if origin.strip()
        ]


settings = Settings()


