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
echo "  1) 全部测试"
echo "  2) 单元测试"
echo "  3) 集成测试"
echo "  4) 指定文件"
echo "  5) 带覆盖率报告"
echo ""

read -p "请选择 (1-5): " choice

case "$choice" in
    1)
        echo "🏃 运行全部测试..."
        python -m pytest tests/ -v
        ;;
    2)
        echo "🏃 运行单元测试..."
        python -m pytest tests/unit/ -v
        ;;
    3)
        echo "🏃 运行集成测试..."
        python -m pytest tests/integration/ -v
        ;;
    4)
        echo ""
        read -p "输入测试文件路径: " test_file
        echo "🏃 运行 $test_file..."
        python -m pytest "$test_file" -v
        ;;
    5)
        echo "🏃 运行全部测试并生成覆盖率报告..."
        python -m pytest tests/ -v \
            --cov=biz \
            --cov=external \
            --cov=utils \
            --cov-report=html \
            --cov-report=term-missing

        echo ""
        echo "📊 覆盖率报告已生成到 htmlcov/index.html"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 测试完成!"
