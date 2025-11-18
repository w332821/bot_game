#!/bin/bash

# ============================================
# 数据库迁移执行脚本
# ============================================

set -e

echo "=========================================="
echo "  数据库迁移工具"
echo "=========================================="
echo ""

# 配置
DB_NAME="game_bot"
MIGRATION_FILE="migrations/001_add_report_fields_safe.sql"

# 检查迁移文件是否存在
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ 错误: 迁移文件不存在 $MIGRATION_FILE"
    exit 1
fi

echo "📋 迁移信息:"
echo "   数据库: $DB_NAME"
echo "   脚本文件: $MIGRATION_FILE"
echo ""

# 提示用户确认
read -p "是否继续执行迁移? (y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ 迁移已取消"
    exit 0
fi

echo ""
echo "🚀 开始执行迁移..."
echo ""

# 执行迁移
mysql -u root -p "$DB_NAME" < "$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 迁移执行成功!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "❌ 迁移执行失败，请检查错误信息"
    echo "=========================================="
    exit 1
fi
