#!/bin/bash

# pytest自动化测试运行脚本
# 修复langsmith与pydantic v2冲突问题

set -e

echo "🧪 Game Bot 自动化测试"
echo "======================"
echo ""

# 检查并卸载冲突的langsmith包
echo "🔧 检查依赖冲突..."
if pip show langsmith > /dev/null 2>&1; then
    echo "⚠️  检测到langsmith包（与pydantic v2冲突），正在卸载..."
    pip uninstall -y langsmith > /dev/null 2>&1
    echo "✅ 已卸载langsmith"
fi

# 安装测试依赖
echo "📦 检查测试依赖..."
pip install -q -r requirements-test.txt 2>&1 | grep -E "(Installing|Requirement)" || echo "依赖已安装"
echo "✅ 测试依赖已就绪"
echo ""

# 显示测试选项
echo "请选择测试类型:"
echo "  1) 认证模块测试 (test_auth_api.py)"
echo "  2) 报表模块测试 (test_reports_api.py)"
echo "  3) 新增模块测试 (认证+报表)"
echo "  4) 全部测试"
echo "  5) 单元测试"
echo "  6) 集成测试"
echo "  7) 指定文件"
echo "  8) 覆盖率报告 (新增模块)"
echo "  9) 覆盖率报告 (全部)"
echo ""

read -p "请选择 (1-9): " choice

case "$choice" in
    1)
        echo "🔐 运行认证模块测试..."
        python -m pytest test/test_auth_api.py -v --asyncio-mode=auto
        ;;
    2)
        echo "📊 运行报表模块测试..."
        python -m pytest test/test_reports_api.py -v --asyncio-mode=auto
        ;;
    3)
        echo "🆕 运行新增模块测试..."
        python -m pytest test/test_auth_api.py test/test_reports_api.py -v --asyncio-mode=auto
        ;;
    4)
        echo "🏃 运行全部测试..."
        python -m pytest test/ -v --asyncio-mode=auto
        ;;
    5)
        echo "🏃 运行单元测试..."
        python -m pytest test/unit/ -v --asyncio-mode=auto
        ;;
    6)
        echo "🏃 运行集成测试..."
        python -m pytest test/integration/ -v --asyncio-mode=auto
        ;;
    7)
        echo ""
        read -p "输入测试文件路径: " test_file
        echo "🏃 运行 $test_file..."
        python -m pytest "$test_file" -v --asyncio-mode=auto
        ;;
    8)
        echo "📈 生成新增模块覆盖率报告..."
        python -m pytest test/test_auth_api.py test/test_reports_api.py -v --asyncio-mode=auto \
            --cov=biz/auth \
            --cov=biz/reports \
            --cov-report=html \
            --cov-report=term-missing

        echo ""
        echo "📊 覆盖率报告已生成到 htmlcov/index.html"
        echo "   运行 'open htmlcov/index.html' 查看详细报告"
        ;;
    9)
        echo "📈 生成全部覆盖率报告..."
        python -m pytest test/ -v --asyncio-mode=auto \
            --cov=biz \
            --cov=external \
            --cov=utils \
            --cov-report=html \
            --cov-report=term-missing

        echo ""
        echo "📊 覆盖率报告已生成到 htmlcov/index.html"
        echo "   运行 'open htmlcov/index.html' 查看详细报告"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 测试完成!"
