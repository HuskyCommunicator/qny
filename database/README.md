# 数据库说明

本目录包含AI角色扮演聊天应用的数据库相关文件。

## 文件说明

### schema.sql
- 数据库表结构定义
- 包含所有必要的表、索引和外键关系
- 支持用户管理、AI角色、聊天会话和消息功能

### init_data.sql
- 初始数据插入脚本
- 包含默认管理员用户和示例AI角色
- 可用于快速搭建演示环境

### database_setup.sh
- 数据库初始化脚本（可选）
- 自动创建数据库、表结构和初始数据

## 数据库结构

### 主要表
1. **users** - 用户信息表
2. **agents** - AI角色表
3. **chat_sessions** - 聊天会话表
4. **chat_messages** - 聊天消息表
5. **user_agents** - 用户与AI角色的多对多关系表

### 字段说明
- 所有表都包含 `created_at` 和 `updated_at` 时间戳
- 使用外键约束确保数据完整性
- 适当的索引优化查询性能

## 使用方法

### 手动创建数据库
```sql
-- 创建数据库
CREATE DATABASE qny_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE qny_db;

-- 执行表结构创建
SOURCE schema.sql;

-- 插入初始数据
SOURCE init_data.sql;
```

### 或使用MySQL命令行
```bash
mysql -u root -p -e "CREATE DATABASE qny_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p qny_db < schema.sql
mysql -u root -p qny_db < init_data.sql
```

## 默认账号

### 管理员账号
- 用户名: admin
- 密码: admin123

### 示例AI角色
- 哈利波特
- 苏格拉底
- 夏洛克·福尔摩斯
- 爱因斯坦
- 莎士比亚
- 达芬奇
- 孔子
- 玛丽·居里
- 李白

## 注意事项

1. 确保MySQL版本 >= 5.7
2. 字符集使用utf8mb4以支持完整的Unicode字符
3. 生产环境部署前请修改默认密码
4. 定期备份数据库数据