# AI 角色扮演网站 Demo

这是一个基于 FastAPI（后端） + Vue.js（前端）的 AI 角色扮演应用。

## ✨ 核心特色功能

### 🎭 智能角色扮演
- **多角色支持**：支持多种预设角色和自定义角色
- **角色记忆**：每个角色都有独特的记忆和性格
- **动态Prompt**：根据对话历史智能调整角色表现

### 🧠 智能记忆系统
- **短期记忆**：Redis 存储最近对话，快速响应
- **长期记忆**：MySQL 持久化存储，跨会话记忆
- **上下文理解**：智能解析对话历史，保持连贯性

### 🎤 多模态交互
- **语音识别**：百度语音转文字服务
- **语音合成**：百度语音合成，多种音色选择
- **流式对话**：实时显示 AI 回复过程

### 🔍 知识增强（RAG）
- **文档检索**：从知识库中检索相关信息
- **智能问答**：结合检索内容提供准确回答
- **多格式支持**：支持多种文档格式解析

### 🛡️ 安全与性能
- **JWT 认证**：安全的用户身份验证
- **登录保护**：防暴力破解，智能限流
- **高并发**：支持多用户同时使用

## 🏗️ 技术架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (React)   │    │   后端 (FastAPI) │    │   外部服务      │
│                 │    │                 │    │                 │
│ • 角色选择界面   │◄──►│ • 用户认证      │◄──►│ • 通义千问 LLM  │
│ • 对话界面      │    │ • 角色管理      │    │ • 阿里云语音    │
│ • 语音交互      │    │ • 对话处理      │    │ • 百度语音      │
│ • 流式显示      │    │ • 记忆管理      │    │ • Azure 语音    │
└─────────────────┘    │ • RAG 检索      │    │ • OpenAI API    │
                       │ • 语音处理      │    └─────────────────┘
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   数据存储      │
                       │                 │
                       │ • MySQL (长期)  │
                       │ • Redis (短期)  │
                       │ • 文件存储      │
                       └─────────────────┘
```

## 📋 系统模块说明

### 核心模块
- **角色管理**：支持角色搜索、模板管理、头像上传
- **对话系统**：文本对话、流式输出、语音交互
- **记忆系统**：短期记忆（Redis）+ 长期记忆（MySQL）
- **RAG检索**：文档索引、智能检索、知识增强
- **用户认证**：JWT认证、登录保护、权限管理

### 技术实现
- **配置管理**：所有配置在 `backend/.env` 中统一管理
- **数据库**：MySQL存储持久化数据，Redis缓存会话信息
- **AI服务**：集成通义千问等LLM服务
- **文件存储**：阿里云OSS存储用户上传文件

## 📚 RAG 文档管理

### 文档格式支持
- **结构化数据**：支持JSON格式的角色信息导入
- **文件上传**：支持PDF、Markdown等文档格式
- **批量管理**：支持文档的增删改查操作

### 检索机制
- **智能切分**：按内容结构自动切分文档
- **向量检索**：使用TF-IDF算法进行文档检索
- **上下文增强**：检索结果与对话历史结合

## 🎭 角色模板系统

### 模板来源
- **内置模板**：位于后端 `prompt_templates.py` 的预设角色
- **自定义模板**：存储在数据库中，通过API管理

### 模板管理
- **搜索角色**：支持按名称搜索可用角色
- **获取模板**：获取角色详细信息和Prompt模板
- **创建更新**：支持创建和更新自定义角色模板
- **头像管理**：支持角色头像上传和管理

### 使用方式
- 前端通过API获取角色列表供用户选择
- 对话时传递角色名称到后端
- 支持模板预览和详细信息展示

## 🚀 程序运行说明

### 环境要求
- **Python**: 3.11+
- **Node.js**: 18+ 或 20+
- **MySQL**: 5.7+ 或 8.0+
- **Redis**: 6.0+
- **阿里云服务**: OSS存储、通义千问API

### 快速启动

#### 1. 后端启动
```bash
# 进入后端目录
cd ai-roleplay-demo/ai-roleplay-demo/backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的配置信息

# 启动服务
uvicorn main:app --reload --port 8000
```

#### 2. 前端启动
```bash
# 进入前端目录
cd ai-roleplay-demo/ai-roleplay-demo/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 3. 访问应用
- 前端地址：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 生产环境部署

#### 后端部署
```bash
# 构建生产版本
npm run build

# 使用Gunicorn启动
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 前端部署
```bash
# 构建生产版本
npm run build

# 将dist文件夹部署到Web服务器
```

## 🏗️ 架构设计

### 技术栈
- **后端**: FastAPI + SQLAlchemy + Pydantic
- **前端**: Vue.js + Element Plus + Axios
- **数据库**: MySQL + Redis
- **AI服务**: 通义千问 + 百度语音
- **存储**: 阿里云OSS

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue.js)  │    │   后端 (FastAPI) │    │   外部服务      │
│                 │    │                 │    │                 │
│ • 用户界面       │◄──►│ • API路由       │◄──►│ • 通义千问 LLM  │
│ • 角色选择       │    │ • 业务逻辑      │    │ • 百度语音      │
│ • 对话界面       │    │ • 数据模型      │    │ • 阿里云OSS     │
│ • 状态管理       │    │ • 服务层        │    │ • Redis缓存     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   数据存储      │
                       │                 │
                       │ • MySQL (持久化) │
                       │ • Redis (缓存)  │
                       └─────────────────┘
```

### 模块规格说明

#### 前端模块 (Vue.js)
**负责人**: 史鑫

**核心组件**:
- **用户认证模块**: 登录、注册、用户信息管理
- **角色管理模块**: 角色选择、角色创建、角色展示
- **对话模块**: 聊天界面、消息显示、流式输出
- **语音模块**: 语音录制、播放、控制
- **文件管理**: 文件上传、预览、管理

**技术实现**:
- Vue 3 + Composition API
- Element Plus UI组件库
- Pinia状态管理
- Axios HTTP客户端
- Vue Router路由管理

#### 后端模块 (FastAPI)
**负责人**: 赵愈炜、麦尔旦·克热木

**核心模块**:

1. **认证授权模块** (`app/routers/auth.py`)
   - JWT令牌生成和验证
   - 用户注册和登录
   - 权限控制和中间件

2. **角色管理模块** (`app/routers/role.py`)
   - 角色模板管理
   - 角色搜索和获取
   - 角色头像上传

3. **对话系统模块** (`app/routers/chat.py`)
   - 文本对话处理
   - 流式输出支持
   - 语音转文字和文字转语音

4. **RAG检索模块** (`app/routers/rag.py`)
   - 文档索引管理
   - 智能检索服务
   - 知识增强处理

5. **用户管理模块** (`app/routers/me.py`)
   - 用户信息管理
   - 个人设置
   - 数据统计

**服务层** (`app/services/`):
- **LLM服务**: 大语言模型调用和响应处理
- **语音服务**: 百度语音STT/TTS服务集成
- **存储服务**: OSS文件上传和管理
- **缓存服务**: Redis缓存管理
- **记忆服务**: 短期和长期记忆管理

**数据层** (`app/models/`):
- **用户模型**: 用户信息和认证
- **角色模型**: 角色模板和实例
- **对话模型**: 会话和消息记录
- **场景模型**: 场景和模板管理

### 开发分工

#### 前端开发 (史鑫)
- **用户界面设计**: 响应式布局、交互体验优化
- **组件开发**: 可复用组件库建设
- **状态管理**: Pinia store设计和实现
- **API集成**: 与后端接口对接
- **性能优化**: 代码分割、懒加载、缓存策略

#### 后端开发 (赵愈炜、麦尔旦·克热木)
- **API设计**: RESTful接口设计和实现
- **数据库设计**: 表结构设计和优化
- **业务逻辑**: 核心功能模块开发
- **AI集成**: LLM和语音服务集成
- **系统优化**: 性能调优、安全加固

### 技术规范

#### 代码规范
- **Python**: 遵循PEP 8规范，使用Black格式化
- **JavaScript**: 遵循ESLint规范，使用Prettier格式化
- **注释**: 关键函数和类必须添加文档字符串
- **命名**: 使用有意义的变量和函数名

#### 接口规范
- **RESTful**: 遵循REST API设计原则
- **状态码**: 正确使用HTTP状态码
- **错误处理**: 统一的错误响应格式
- **版本控制**: API版本管理策略

#### 数据库规范
- **命名**: 使用下划线命名法
- **索引**: 为查询字段添加适当索引
- **约束**: 设置必要的外键和唯一约束
- **迁移**: 使用数据库迁移管理表结构变更

### 环境配置
在 `backend/.env` 文件中配置以下关键参数：
- **数据库**: `DATABASE_URL` - MySQL连接字符串
- **缓存**: `REDIS_URL` - Redis连接字符串  
- **AI服务**: `DASHSCOPE_API_KEY` - 通义千问API密钥
- **语音服务**: `BAIDU_APP_ID` - 百度语音服务配置
- **存储**: `OSS_ACCESS_KEY_ID` - 阿里云OSS配置
- **安全**: `SECRET_KEY` - JWT密钥

### 数据库初始化
```bash
# 创建数据库表
python init_db.py

# 运行数据迁移
python migrate_new_features.py
```

## 📞 技术支持

如果在部署或使用过程中遇到问题，可以：

1. 查看详细的运行说明文档
2. 查看架构设计文档了解系统结构
3. 检查服务器日志文件
4. 确认所有配置项是否正确设置

## 🚀 后续功能开发规划

### 🎨 高级角色系统
- **角色关系网络**：角色之间的复杂关系映射
- **角色成长系统**：根据对话内容动态调整角色属性
- **角色情感状态**：追踪角色的情绪变化和状态
- **多角色对话**：支持多个角色同时参与的群聊模式

### 🧠 智能记忆增强
- **情感记忆**：记录用户的情感状态和偏好
- **知识图谱**：构建用户知识网络
- **记忆压缩**：智能压缩长期记忆，保留关键信息
- **记忆搜索**：快速检索历史对话内容

### 🎭 沉浸式体验
- **3D 角色形象**：集成 3D 角色模型和动画
- **场景系统**：不同场景下的角色表现差异
- **剧情模式**：预设剧情线和分支选择
- **成就系统**：用户与角色的互动成就

### 🔮 AI 能力扩展
- **多模态理解**：图像、视频内容理解
- **实时翻译**：多语言实时对话翻译
- **情感分析**：实时分析用户情感状态
- **个性化推荐**：基于用户偏好的内容推荐

### 🛠️ 开发者工具
- **角色编辑器**：可视化角色创建工具
- **对话分析**：对话质量分析和优化建议
- **A/B 测试**：不同角色表现的对比测试
- **API 监控**：详细的性能监控和分析

### 🌐 社交功能
- **角色分享**：用户创建的角色社区分享
- **对话记录**：精美的对话记录导出
- **角色投票**：社区评选最受欢迎角色
- **协作创作**：多人协作创建角色

### 📱 移动端优化
- **PWA 支持**：渐进式 Web 应用
- **离线模式**：基础功能离线使用
- **推送通知**：角色消息推送
- **手势交互**：移动端优化的交互体验

## 🔧 常见问题与解决方案

### 服务器部署问题

#### 1. Python 版本问题
```bash
# 检查 Python 版本
python3 --version

# 如果版本不匹配，安装正确版本
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

#### 2. 虚拟环境问题
```bash
# 如果虚拟环境创建失败
sudo apt install python3-venv

# 重新创建虚拟环境
rm -rf ai_backend_env_venv
python3.11 -m venv ai_backend_env_venv
source ai_backend_env_venv/bin/activate
```

#### 3. 依赖安装问题
```bash
# 安装系统依赖
sudo apt install build-essential libssl-dev libffi-dev python3-dev

# 升级 pip
pip install --upgrade pip setuptools wheel

# 分步安装关键依赖
pip install fastapi uvicorn sqlalchemy pymysql redis
pip install -r requirements.txt
```

### 应用运行问题

#### 1. 数据库连接问题
- 检查 `DATABASE_URL` 格式：`mysql+pymysql://user:password@host:port/database`
- 确认数据库用户权限和网络连通性
- 可临时使用 SQLite：`DATABASE_URL=sqlite:///./data.db`

```bash
# 测试数据库连接
python -c "
from sqlalchemy import create_engine
engine = create_engine('your_database_url')
with engine.connect() as conn:
    print('数据库连接成功')
"
```

#### 2. LLM 调用问题
- 确认 `DASHSCOPE_API_KEY` 有效且有余额
- 检查网络连接和防火墙设置
- 查看后端日志中的错误信息

```bash
# 测试 API 连接
curl -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"model":"qwen-plus","messages":[{"role":"user","content":"hello"}]}' \
     https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
```

#### 3. Redis 连接问题
- 确认 Redis 服务运行：`redis-cli ping`
- 检查 `REDIS_URL` 格式：`redis://localhost:6379/0`

```bash
# 安装和启动 Redis
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 测试连接
redis-cli ping
```

#### 4. OSS 上传问题
- 确认阿里云 OSS 配置正确
- 检查 AccessKey 权限（需要 PutObject 权限）
- 确认 Bucket 存在且可访问

#### 5. 跨域问题
- 调整 `CORS_ALLOW_ORIGINS` 为前端域名
- 开发环境可设为 `*`，生产环境建议指定具体域名

#### 6. 端口和防火墙问题
```bash
# 检查端口是否开放
sudo ufw allow 8000
sudo ufw status

# 或者使用 iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

### 性能优化问题

#### 1. 内存不足
```bash
# 检查内存使用
free -h
htop

# 添加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 2. 数据库性能
```bash
# MySQL 配置优化
sudo vim /etc/mysql/mysql.conf.d/mysqld.cnf

# 添加配置
[mysqld]
innodb_buffer_pool_size = 1G
max_connections = 200
query_cache_size = 64M
```

### 日志和监控

#### 1. 应用日志
```bash
# 查看实时日志
tail -f /var/log/ai-roleplay.log

# 或者使用 journalctl (如果使用 systemd)
sudo journalctl -u ai-roleplay -f
```

#### 2. 系统监控
```bash
# 安装监控工具
sudo apt install htop iotop nethogs

# 监控系统资源
htop           # CPU 和内存
iotop          # 磁盘 I/O
nethogs        # 网络使用
```

## 📈 性能优化建议

### 数据库优化
- 为常用查询字段添加索引
- 使用连接池管理数据库连接
- 定期清理无用数据和日志
- 考虑读写分离

### 缓存优化
- Redis 合理设置 TTL，避免内存溢出
- 使用 Redis 集群提高可用性
- 缓存热点数据和查询结果

### API 性能
- 设置合适的超时和重试参数
- 使用异步处理长时间任务
- 实现请求限流和熔断机制

### RAG 系统优化
- 定期清理无用文档，控制索引大小
- 使用更高效的向量数据库（如 Milvus、Qdrant）
- 优化文档切分策略

### 文件存储优化
- 使用 CDN 加速 OSS 访问
- 图片压缩和格式优化
- 实现文件上传进度显示

### 服务器优化
- 使用 Gunicorn + Uvicorn 提高并发能力
- 配置 Nginx 反向代理和负载均衡
- 启用 Gzip 压缩减少传输大小

## 🏷️ 版本信息

- **当前版本**: v1.0.0
- **Python 版本**: 3.11+
- **FastAPI 版本**: 最新稳定版
- **数据库**: MySQL 5.7+ / 8.0+
- **缓存**: Redis 6.0+

## 📞 技术支持

如果在部署或使用过程中遇到问题，可以：

1. 查看本文档的常见问题部分
2. 检查服务器日志文件
3. 确认所有配置项是否正确设置
4. 验证网络连接和防火墙设置

## 📄 许可证

本项目采用 MIT 许可证，详情请查看 LICENSE 文件。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request
