# AI 角色扮演网站 Demo

这是一个基于 FastAPI（后端） + React（前端）的 AI 角色扮演应用示例。

## 后端（FastAPI）

### 技术栈
- FastAPI, SQLAlchemy, Pydantic
- JWT 认证（python-jose）
- 数据库：MySQL（可通过 `DATABASE_URL` 切换到 SQLite 等）

### 目录结构（后端）
```
backend/
├─ main.py
├─ prompt_templates.py
├─ requirements.txt
├─ Dockerfile
└─ app/
   ├─ core/ (config、security、db)
   ├─ models/ (user、chat)
   ├─ schemas/ (auth、user、chat)
   ├─ routers/ (auth、chat、role、me)
   ├─ services/ (llm、tts、stt 占位)
   └─ utils/ (logger)
```

### 环境变量（在 `backend/.env` 中配置）
```
APP_NAME=AI Roleplay Backend
ENV=development
SECRET_KEY=请修改
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ALLOW_ORIGINS=*
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ai_roleplay?charset=utf8mb4
API_KEY=
```

> 提示：未设置 `DATABASE_URL` 时，后端会默认使用 MySQL 示例串。你也可以改为 `sqlite:///./data.db` 进行本地快速试用。

### 安装与启动（后端）
```bash
cd ai-roleplay-demo/ai-roleplay-demo/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Docker 运行（后端）
```bash
cd ai-roleplay-demo/ai-roleplay-demo/backend
docker build -t ai-roleplay-backend .
docker run -p 8000:8000 --env-file .env ai-roleplay-backend
```

### 登录模块接口

- 注册：POST `/auth/register`
  - 请求体（JSON）
    ```json
    { "username": "alice", "email": "a@b.com", "password": "Passw0rd" }
    ```
  - 响应（UserOut）包含 `id/username/email/is_active/full_name`

- 登录：POST `/auth/login`
  - 表单（`application/x-www-form-urlencoded`）字段：`username`, `password`
  - 响应（Token）：
    ```json
    { "access_token": "<JWT>", "token_type": "bearer" }
    ```

- 获取当前用户：GET `/me`
  - 头部：`Authorization: Bearer <access_token>`
  - 响应（UserOut）

### 其他接口
- 角色搜索与模板：`/role/search?q=xxx`、`/role/template/{name}`
- 文本聊天：POST `/chat/text`
- 语音识别：POST `/chat/stt`（表单文件字段 `file`）
- 文本转语音（占位）：POST `/chat/tts`

## 前端（React + Vite）

开发启动：
```bash
cd ai-roleplay-demo/ai-roleplay-demo/frontend
npm install
npm run dev
```

## 常见问题
- 无法连接数据库：检查 `DATABASE_URL`、数据库用户权限与端口是否可达。
- 401 未授权：确认携带 `Authorization: Bearer <access_token>`，并且 token 未过期。
- 跨域问题：根据需要调整 `CORS_ALLOW_ORIGINS`。
