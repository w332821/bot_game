#!/bin/bash
# 测试环境完整设置脚本

set -e

echo "🧪 Game Bot 测试环境设置"
echo "=========================="

# 1. 卸载冲突的langsmith
echo ""
echo "🔧 步骤1: 移除冲突的依赖..."
pip uninstall -y langsmith 2>/dev/null || echo "langsmith未安装"
echo "✅ 依赖冲突已解决"

# 2. 安装所有依赖
echo ""
echo "📦 步骤2: 安装项目依赖..."
pip install -q -r requirements.txt
pip install -q -r requirements-test.txt
echo "✅ 依赖安装完成"

# 3. 初始化测试数据库
echo ""
echo "🗄️  步骤3: 初始化测试数据库..."
python -m base.init_db
echo "✅ 数据库初始化完成"

# 4. 运行测试示例
echo ""
echo "🏃 步骤4: 运行测试示例..."
python -m pytest tests/unit/test_user_repository.py::TestUserRepository::test_user_exists -v

echo ""
echo "✅ 测试环境设置完成!"
echo ""
echo "现在可以使用以下命令:"
echo "  python -m pytest tests/ -v                  # 全部测试"
echo "  python -m pytest tests/unit/ -v             # 单元测试"
echo "  python -m pytest tests/integration/ -v      # 集成测试"
echo "  ./run_tests.sh                              # 交互式测试菜单"
