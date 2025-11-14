#!/bin/bash
# 文档清理脚本

echo "📚 开始整理项目文档..."
echo ""

# 1. 删除过时的进度和验证文档
echo "🗑️  删除过时文档..."
rm -f BOT_IMPLEMENTATION_PROGRESS.md
rm -f DAY1_FINAL_VALIDATION_REPORT.md
rm -f VALIDATION_REPORT.md
rm -f APP_IMPLEMENTATION_STATUS.md
rm -f TESTING.md
echo "✅ 已删除 5 个过时文档"
echo ""

# 2. 创建 docs 目录存放技术文档
echo "📁 创建 docs 目录..."
mkdir -p docs
mv WEBHOOK_SPEC.md docs/ 2>/dev/null || echo "  - WEBHOOK_SPEC.md 已在 docs/"
mv APP_ENDPOINTS.md docs/ 2>/dev/null || echo "  - APP_ENDPOINTS.md 已在 docs/"
mv REAL_API_INTEGRATION.md docs/ 2>/dev/null || echo "  - REAL_API_INTEGRATION.md 已在 docs/"
mv README_APP.md docs/ 2>/dev/null || echo "  - README_APP.md 已在 docs/"
echo "✅ 技术文档已移到 docs/ 目录"
echo ""

# 3. 显示当前文档结构
echo "📋 当前文档结构:"
echo ""
echo "根目录:"
ls -1 *.md 2>/dev/null | sed 's/^/  - /'
echo ""
echo "docs/ 目录:"
ls -1 docs/*.md 2>/dev/null | sed 's/^docs\//  - /'
echo ""

echo "✅ 文档整理完成!"
echo ""
echo "保留的文档:"
echo "  - README.md           (项目主文档)"
echo "  - CLAUDE.md           (AI项目说明)"
echo "  - QUICKSTART.md       (快速开始)"
echo "  - SETUP_GUIDE.md      (安装指南)"
echo ""
echo "技术文档 (docs/):"
echo "  - APP_ENDPOINTS.md          (API端点)"
echo "  - WEBHOOK_SPEC.md           (Webhook规范)"
echo "  - REAL_API_INTEGRATION.md   (API集成)"
echo "  - README_APP.md             (App端说明)"
