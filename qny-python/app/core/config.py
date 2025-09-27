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

        # 数据库配置
        default_mysql = "mysql+pymysql://user:password@localhost:3306/ai_roleplay?charset=utf8mb4"
        self.database_url: str = os.getenv("DATABASE_URL", default_mysql)

        # 通义千问（DashScope/OpenAI 兼容）
        self.dashscope_api_key: Optional[str] = os.getenv("DASHSCOPE_API_KEY")
        self.llm_provider: str = os.getenv("LLM_PROVIDER", "dashscope")
        self.llm_model: str = os.getenv("LLM_MODEL", "qwen-plus")
        self.llm_base_url: str = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.llm_timeout_sec: int = int(os.getenv("LLM_TIMEOUT_SEC", "30"))
        self.llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "3"))

        # CORS
        cors = os.getenv("CORS_ALLOW_ORIGINS", "*")
        self.cors_allow_origins: list[str] = ["*"] if cors.strip() == "*" else [
            origin.strip() for origin in cors.split(",") if origin.strip()
        ]

        # 登录保护阈值
        self.login_max_attempts: int = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
        self.login_lockout_minutes: int = int(os.getenv("LOGIN_LOCKOUT_MINUTES", "15"))
        self.login_delay_ms: int = int(os.getenv("LOGIN_DELAY_MS", "300"))

        # Redis 配置
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        # 阿里云 OSS 配置
        self.oss_access_key_id: str = os.getenv("OSS_ACCESS_KEY_ID", "")
        self.oss_access_key_secret: str = os.getenv("OSS_ACCESS_KEY_SECRET", "")
        self.oss_endpoint: str = os.getenv("OSS_ENDPOINT", "")
        self.oss_bucket_name: str = os.getenv("OSS_BUCKET_NAME", "")
        self.oss_base_url: str = os.getenv("OSS_BASE_URL", "")

        # Debug 打印
        print(f"[Config] ENV={self.environment}, DB={self.database_url}")
        print(f"[Config] LLM provider={self.llm_provider}, model={self.llm_model}, base_url={self.llm_base_url}")
        print(f"[Config] DashScope API key loaded={'YES' if self.dashscope_api_key else 'NO'}")

settings = Settings()
