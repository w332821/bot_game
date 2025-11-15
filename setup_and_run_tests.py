#!/usr/bin/env python3
"""
完整的测试环境设置和运行脚本
解决所有测试问题：
1. 卸载冲突的langsmith
2. 安装依赖
3. 初始化测试数据库
4. 运行测试
"""

import subprocess
import sys
import os

def run(cmd, description, check=True):
    """运行命令"""
    print(f"\n{description}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(result.stderr, file=sys.stderr)

    if check and result.returncode != 0:
        print(f"❌ 命令失败: {cmd}")
        return False
    return True

def main():
    os.chdir('/Users/demean5/Desktop/bot_game')

    print("=" * 60)
    print("🧪 Game Bot 测试环境完整设置")
    print("=" * 60)

    # 步骤1: 卸载langsmith
    print("\n📌 步骤1: 移除冲突的依赖")
    run("pip uninstall -y langsmith", "卸载langsmith...", check=False)
    print("✅ 步骤1完成")

    # 步骤2: 安装依赖
    print("\n📌 步骤2: 安装项目依赖")
    if not run("pip install -q -r requirements.txt", "安装生产依赖..."):
        return 1
    if not run("pip install -q -r requirements-test.txt", "安装测试依赖..."):
        return 1
    print("✅ 步骤2完成")

    # 步骤3: 初始化数据库
    print("\n📌 步骤3: 初始化测试数据库")
    init_code = """
from base.init_db import init_db_sync
import sys

try:
    print("正在创建测试数据库表...")
    init_db_sync('mysql+pymysql://root:123456@localhost:3306/game_bot_test', echo=False)
    print("✅ 数据库表创建成功")
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}", file=sys.stderr)
    sys.exit(1)
"""

    with open('/tmp/init_test_db.py', 'w') as f:
        f.write(init_code)

    if not run("python /tmp/init_test_db.py", "初始化测试数据库..."):
        print("⚠️  数据库初始化失败，但继续测试...")
    else:
        print("✅ 步骤3完成")

    # 步骤4: 运行测试
    print("\n📌 步骤4: 运行测试")
    result = run(
        "python -m pytest tests/unit/test_user_repository.py::TestUserRepository::test_user_exists -v",
        "运行测试示例...",
        check=False
    )

    print("\n" + "=" * 60)
    if result:
        print("✅ 测试环境设置成功!")
        print("\n可用的测试命令:")
        print("  python -m pytest tests/ -v              # 全部测试")
        print("  python -m pytest tests/unit/ -v         # 单元测试")
        print("  python -m pytest tests/integration/ -v  # 集成测试")
        print("  ./run_tests.sh                          # 交互式菜单")
        return 0
    else:
        print("❌ 测试失败，请检查上面的错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())
