#!/usr/bin/env python3
"""
修复测试环境并运行pytest
解决langsmith与pydantic v2冲突问题
"""

import subprocess
import sys

def run_command(cmd, description):
    """运行shell命令"""
    print(f"\n{description}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode

def main():
    print("🧪 Game Bot 测试环境修复")
    print("=" * 50)

    # 1. 卸载冲突的langsmith
    print("\n🔧 步骤1: 检查并卸载langsmith...")
    ret = run_command(
        "pip show langsmith",
        "检查langsmith是否安装..."
    )

    if ret == 0:
        print("⚠️  检测到langsmith包，正在卸载...")
        run_command(
            "pip uninstall -y langsmith",
            "卸载langsmith..."
        )
        print("✅ 已卸载langsmith")
    else:
        print("✅ langsmith未安装，无需卸载")

    # 2. 初始化测试数据库
    print("\n🗄️  步骤2: 初始化测试数据库...")
    ret = run_command(
        "python -c \"from base.init_db import init_db_sync; init_db_sync('mysql+pymysql://root:123456@localhost:3306/game_bot_test', echo=False)\"",
        "创建测试数据库表..."
    )
    if ret == 0:
        print("✅ 测试数据库初始化完成")
    else:
        print("⚠️  测试数据库初始化可能失败，继续测试...")

    # 3. 运行测试
    print("\n🏃 步骤3: 运行pytest测试...")
    ret = run_command(
        "python -m pytest tests/unit/test_user_repository.py -v",
        "运行单元测试示例..."
    )

    if ret == 0:
        print("\n✅ 测试通过!")
        print("\n现在可以使用以下命令运行测试:")
        print("  python -m pytest tests/ -v              # 全部测试")
        print("  python -m pytest tests/unit/ -v         # 单元测试")
        print("  python -m pytest tests/integration/ -v  # 集成测试")
        print("  ./run_tests.sh                          # 使用交互式脚本")
    else:
        print("\n❌ 测试失败，请检查输出")
        sys.exit(1)

if __name__ == "__main__":
    main()
