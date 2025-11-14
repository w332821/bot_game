#!/usr/bin/env python3
"""清理项目目录，只保留必要文件"""
import os
import shutil

# 要删除的文档
docs_to_remove = [
    'APP_ENDPOINTS.md',
    'APP_IMPLEMENTATION_STATUS.md',
    'BOT_IMPLEMENTATION_PROGRESS.md',
    'COMPATIBILITY_VERIFICATION.md',
    'DAY1_FINAL_VALIDATION_REPORT.md',
    'DEPLOYMENT.md',
    'DEPLOY_TO_SERVER.md',
    'FINAL_CHECKLIST.md',
    'PYTHON_FIXES.md',
    'REAL_API_INTEGRATION.md',
    'SETUP_GUIDE.md',
    'TESTING.md',
    'UPDATED_DEPLOY.md',
    'VALIDATION_REPORT.md',
    'WEBHOOK_SPEC.md',
]

# 要删除的脚本
scripts_to_remove = [
    'cleanup_docs.sh',
    'deploy.sh',
    'start.sh',
    'run_tests.sh',
    'test_webhook.sh',
    'run_comprehensive_tests.py',
    'validate_day1.py',
    'verify_fixes.py',
    'test_imports.py',
    'test_env_loading.py',
]

# 创建归档目录
os.makedirs('archive', exist_ok=True)

# 移动文档到归档
for doc in docs_to_remove:
    if os.path.exists(doc):
        shutil.move(doc, f'archive/{doc}')
        print(f'✓ 归档: {doc}')

# 删除旧脚本
for script in scripts_to_remove:
    if os.path.exists(script):
        os.remove(script)
        print(f'✓ 删除: {script}')

print('\n清理完成！')
print('保留的文件:')
print('  - README.md (主文档)')
print('  - CLAUDE.md (AI助手说明)')
print('  - QUICKSTART.md (快速开始)')
print('  - PM2_GUIDE.md (PM2启动指南)')
print('  - start_bot.sh (PM2启动脚本)')
print('  - ecosystem.config.js (PM2配置)')
