#!/usr/bin/env python3
"""
测试环境变量加载
验证 .env 文件是否正确加载
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("环境变量加载测试")
print("=" * 60)

# 加载 .env 文件
load_dotenv()

# 检查关键环境变量
env_vars = {
    'BOT_API_BASE': os.getenv('BOT_API_BASE'),
    'BOT_API_KEY': os.getenv('BOT_API_KEY'),
    'BOT_API_SECRET': os.getenv('BOT_API_SECRET'),
    'WEBHOOK_PORT': os.getenv('WEBHOOK_PORT'),
    'DATABASE_URI': os.getenv('DATABASE_URI'),
}

print("\n环境变量状态:")
print("-" * 60)

all_loaded = True
for key, value in env_vars.items():
    if value:
        # 对于敏感信息，只显示前几位和后几位
        if 'SECRET' in key or 'KEY' in key:
            if len(value) > 10:
                display_value = f"{value[:8]}...{value[-8:]}"
            else:
                display_value = "***"
        else:
            display_value = value

        print(f"✅ {key}: {display_value}")
    else:
        print(f"❌ {key}: 未设置")
        all_loaded = False

print("-" * 60)

if all_loaded:
    print("\n✅ 所有环境变量已正确加载！")
    exit(0)
else:
    print("\n❌ 部分环境变量未加载，请检查 .env 文件")
    exit(1)
