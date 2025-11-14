#!/bin/bash

# Game Bot 快速启动脚本
# 使用bot_game conda环境启动服务

set -e

echo "🎮 Game Bot 启动脚本"
echo "===================="
echo ""

# 检查conda环境
if [ ! -d "/opt/anaconda3/envs/bot_game" ]; then
    echo "❌ bot_game conda环境不存在"
    echo "请先创建环境: conda create -n bot_game python=3.11"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "⚠️  未找到config.yaml，复制示例配置..."
    if [ -f "config.example.yaml" ]; then
        cp config.example.yaml config.yaml
        echo "✅ 已创建config.yaml，请编辑数据库配置"
        echo "❌ 启动失败：请先配置数据库连接"
        exit 1
    else
        echo "❌ 未找到config.example.yaml"
        exit 1
    fi
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件"
    echo "请创建.env文件并配置Bot API密钥:"
    echo ""
    echo "BOT_API_BASE_URL=https://bot-api.yueliao.com"
    echo "BOT_API_KEY=your_api_key"
    echo "BOT_API_SECRET=your_api_secret"
    echo ""
    echo "❌ 启动失败：请先配置.env文件"
    exit 1
fi

echo "✅ 配置文件检查通过"
echo ""

# 询问是否初始化数据库
read -p "是否需要初始化数据库？(y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 初始化数据库..."
    /opt/anaconda3/envs/bot_game/bin/python -m base.init_db
    echo "✅ 数据库初始化完成"
    echo ""
fi

# 启动服务
echo "🚀 启动服务..."
echo "服务地址: http://localhost:3003"
echo "文档地址: http://localhost:3003/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

/opt/anaconda3/envs/bot_game/bin/python biz/application.py
