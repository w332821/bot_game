#!/bin/bash
# PM2启动脚本 - 用于服务器后台运行

# 切换到项目目录
PROJECT_DIR="/root/bot_game/bot_game"
cd "$PROJECT_DIR"

# 将项目根目录添加到PYTHONPATH（解决模块导入问题）
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# 查找并加载conda（支持多种安装路径）
CONDA_PATHS=(
    "/opt/anaconda3/etc/profile.d/conda.sh"
    "$HOME/anaconda3/etc/profile.d/conda.sh"
    "/root/anaconda3/etc/profile.d/conda.sh"
    "/usr/local/anaconda3/etc/profile.d/conda.sh"
    "$(dirname $(dirname $(which conda 2>/dev/null) 2>/dev/null) 2>/dev/null)/etc/profile.d/conda.sh"
)

CONDA_FOUND=false
for conda_path in "${CONDA_PATHS[@]}"; do
    if [ -f "$conda_path" ]; then
        source "$conda_path"
        CONDA_FOUND=true
        echo "✓ 找到conda: $conda_path"
        break
    fi
done

if [ "$CONDA_FOUND" = false ]; then
    echo "❌ 错误: 找不到conda"
    echo "尝试查找的路径:"
    printf '%s\n' "${CONDA_PATHS[@]}"
    echo ""
    echo "请运行: which conda"
    exit 1
fi

# 激活conda环境
echo "激活conda环境: bot_game"
conda activate bot_game

# 检查Python和项目目录
echo "Python路径: $(which python)"
echo "项目目录: $PROJECT_DIR"
echo "PYTHONPATH: $PYTHONPATH"

# 启动应用（使用 -m 模块方式运行，确保导入路径正确）
python -m biz.application
