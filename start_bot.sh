#!/bin/bash
# PM2启动脚本 - 简化版，直接使用Python完整路径

# 项目目录
PROJECT_DIR="/root/bot_game/bot_game"
cd "$PROJECT_DIR"

# 设置PYTHONPATH
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# 直接使用conda环境中的Python完整路径（不需要conda activate）
# 根据实际情况修改路径
PYTHON_PATHS=(
    "/root/miniconda3/envs/bot_game/bin/python"
    "/root/anaconda3/envs/bot_game/bin/python"
    "/opt/anaconda3/envs/bot_game/bin/python"
)

# 查找可用的Python
PYTHON_BIN=""
for python_path in "${PYTHON_PATHS[@]}"; do
    if [ -f "$python_path" ]; then
        PYTHON_BIN="$python_path"
        echo "✓ 找到Python: $PYTHON_BIN"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "❌ 错误: 找不到Python解释器"
    echo "尝试的路径:"
    printf '%s\n' "${PYTHON_PATHS[@]}"
    echo ""
    echo "请运行: conda activate bot_game && which python"
    exit 1
fi

# 显示配置
echo "项目目录: $PROJECT_DIR"
echo "Python版本: $($PYTHON_BIN --version)"
echo "PYTHONPATH: $PYTHONPATH"
echo ""
echo "启动应用..."

# 启动应用
$PYTHON_BIN -m biz.application
