# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 FastAPI + Vue 3 的AI角色扮演应用，包含完整的用户认证、角色管理、聊天对话等功能。项目分为前端（qny-vue）和后端（qny-python）两个主要模块。

## 技术栈

### 后端 (qny-python)
- **框架**: FastAPI
- **数据库**: SQLAlchemy (支持 MySQL/SQLite)
- **认证**: JWT Token (OAuth2PasswordBearer)
- **AI服务**: 集成语音转文字(STT)、文字转语音(TTS)、大语言模型(LLM)
- **部署**: Docker + Uvicorn

### 前端 (qny-vue)
- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **样式**: SCSS

## 开发命令

### 后端开发
```bash
# 进入后端目录
cd qny-python

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload

# Docker 构建
docker build -t qny-backend .
docker run -p 8000:8000 qny-backend
```

### 前端开发
```bash
# 进入前端目录
cd qny-vue

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 代码格式化
npm run format
```

## 项目架构

### 后端架构
- **app/core/**: 核心配置、数据库连接、安全模块
- **app/models/**: SQLAlchemy 数据模型
- **app/schemas/**: Pydantic 数据验证schema
- **app/routers/**: FastAPI 路由模块
  - auth.py: 用户认证（注册/登录）
  - chat.py: 聊天功能（文本/语音）
  - role.py: 角色管理
  - me.py: 用户中心
- **app/services/**: 业务逻辑服务
  - llm_service.py: 大语言模型交互
  - stt_service.py: 语音转文字
  - tts_service.py: 文字转语音

### 前端架构
- **src/views/**: 页面组件
  - Login.vue: 登录页面
  - AgentHall.vue: 智能体大厅
  - Chat.vue: 聊天界面
  - MyAgent.vue: 我的智能体
  - CreateAgent.vue: 创建智能体
- **src/components/**: 可复用组件
  - AgentCard.vue: 智能体卡片
  - Nav.vue: 导航栏
  - Aside.vue: 侧边栏

## 核心功能模块

### 1. 用户认证系统
- 基于 JWT Token 的用户认证
- 支持用户名/密码登录和邮箱注册
- Token 过期时间可配置

### 2. 智能体管理
- 智能体创建、编辑、删除
- 智能体角色设定和配置
- 智能体大厅和个人智能体列表

### 3. 聊天系统
- 文本聊天功能
- 语音输入（STT）
- 语音输出（TTS）
- 聊天历史记录

### 4. 用户中心
- 个人信息管理
- 聊天历史查看
- 智能体管理

## 配置文件

### 后端环境变量 (.env)
```
API_KEY=your_api_key_here
PROVIDER=openai
APP_NAME=AI Roleplay Backend
ENV=development
SECRET_KEY=change-this-in-production
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ai_roleplay?charset=utf8mb4
```

## 数据库设计

核心数据表：
- **users**: 用户信息表
- **roles**: 智能体角色表
- **chats**: 聊天记录表
- **messages**: 消息表

## API 接口

### 认证接口
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录

### 聊天接口
- `POST /chat/text` - 文本聊天
- `POST /chat/stt` - 语音转文字
- `POST /chat/tts` - 文字转语音

### 智能体接口
- `GET /role/list` - 获取智能体列表
- `POST /role/create` - 创建智能体
- `PUT /role/{id}` - 更新智能体
- `DELETE /role/{id}` - 删除智能体

### 用户接口
- `GET /me/profile` - 获取用户信息
- `GET /me/agents` - 获取用户的智能体
- `GET /me/chat-history` - 获取聊天历史

## 部署说明

### Docker 部署
```bash
# 构建并启动后端
docker build -t qny-backend ./qny-python
docker run -p 8000:8000 qny-backend

# 构建前端
cd qny-vue
npm run build
```

### 生产环境配置
- 需要配置真实的数据库连接
- 设置安全的 SECRET_KEY
- 配置正确的 CORS 允许域名
- 配置 AI 服务的 API Key

## 注意事项

1. **安全性**: 生产环境必须更改默认的 SECRET_KEY
2. **数据库**: 默认使用 MySQL，可配置为 SQLite
3. **AI服务**: 需要配置有效的 API Key 才能使用聊天功能
4. **跨域**: 开发环境允许所有跨域，生产环境需要配置具体的允许域名