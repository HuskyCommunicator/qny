#!/bin/bash

# AI角色扮演聊天应用数据库设置脚本

# 数据库配置
DB_NAME="qny_db"
DB_USER="qny_user"
DB_PASS="Med2071226570"
DB_HOST="localhost"
DB_PORT="3307"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 开始设置AI角色扮演聊天应用数据库${NC}"

# 检查MySQL是否可访问
echo -e "${YELLOW}📋 检查MySQL连接...${NC}"
if ! mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS -e "SELECT 1;" &> /dev/null; then
    echo -e "${RED}❌ 无法连接到MySQL服务器${NC}"
    echo -e "${YELLOW}请检查：${NC}"
    echo -e "  - MySQL服务是否运行"
    echo -e "  - 用户名密码是否正确"
    echo -e "  - 网络连接是否正常"
    exit 1
fi

echo -e "${GREEN}✅ MySQL连接成功${NC}"

# 创建数据库
echo -e "${YELLOW}📋 创建数据库 $DB_NAME...${NC}"
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据库创建成功${NC}"
else
    echo -e "${RED}❌ 数据库创建失败${NC}"
    exit 1
fi

# 创建表结构
echo -e "${YELLOW}📋 创建表结构...${NC}"
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS $DB_NAME < schema.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 表结构创建成功${NC}"
else
    echo -e "${RED}❌ 表结构创建失败${NC}"
    exit 1
fi

# 插入初始数据
echo -e "${YELLOW}📋 插入初始数据...${NC}"
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS $DB_NAME < init_data.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 初始数据插入成功${NC}"
else
    echo -e "${RED}❌ 初始数据插入失败${NC}"
    exit 1
fi

# 验证数据库
echo -e "${YELLOW}📋 验证数据库...${NC}"
TABLE_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS $DB_NAME -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$DB_NAME';" -s -N)
USER_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS $DB_NAME -e "SELECT COUNT(*) FROM users;" -s -N)
AGENT_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS $DB_NAME -e "SELECT COUNT(*) FROM agents;" -s -N)

echo -e "${GREEN}📊 数据库设置完成：${NC}"
echo -e "  📚 数据库: $DB_NAME"
echo -e "  📋 表数量: $TABLE_COUNT"
echo -e "  👥 用户数量: $USER_COUNT"
echo -e "  🤖 AI角色数量: $AGENT_COUNT"

echo -e "${GREEN}🎉 数据库设置完成！${NC}"
echo -e "${YELLOW}默认账号：${NC}"
echo -e "  用户名: admin"
echo -e "  密码: admin123"

echo -e "${YELLOW}🔗 后端API配置：${NC}"
echo -e "  请确保 .env 文件中的数据库连接信息正确："
echo -e "  DATABASE_URL=mysql+pymysql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME"