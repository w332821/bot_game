#!/bin/bash
# 一键部署脚本 - Python Bot 到服务器

set -e

SERVER="root@lbnlsj"
REMOTE_PATH="/root/bot_game"
LOCAL_PATH="/Users/demean5/Desktop/bot_game"

echo "🚀 开始部署 Python Bot..."

# 1. 打包
echo "📦 打包文件..."
cd "$LOCAL_PATH"
tar -czf /tmp/bot_deploy.tar.gz \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='*.log' \
  --exclude='node_modules' \
  --exclude='game-bot-master' \
  --exclude='.DS_Store' \
  --exclude='*.md' \
  --exclude='test_imports.py' \
  --exclude='verify_fixes.py' \
  --exclude='deploy.sh' \
  .

# 2. 上传
echo "📤 上传到服务器..."
scp /tmp/bot_deploy.tar.gz "$SERVER:/tmp/"

# 3. 部署
echo "🔧 部署并重启..."
ssh "$SERVER" << 'ENDSSH'
set -e

# 备份旧版本
if [ -d /root/bot_game ]; then
  echo "💾 备份旧版本..."
  mv /root/bot_game /root/bot_game_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
fi

# 解压新版本
echo "📂 解压文件..."
mkdir -p /root/bot_game
tar -xzf /tmp/bot_deploy.tar.gz -C /root/bot_game/
rm /tmp/bot_deploy.tar.gz

# 恢复配置文件
if [ -f /root/bot_game_backup_*/config.yaml ]; then
  echo "📋 恢复配置文件..."
  cp /root/bot_game_backup_*/config.yaml /root/bot_game/
fi

if [ -f /root/bot_game_backup_*/.env ]; then
  cp /root/bot_game_backup_*/.env /root/bot_game/
fi

# 重启服务
echo "🔄 重启服务..."
cd /root/bot_game
pm2 stop game-bot-nodejs || true
pm2 restart game-bot-python || pm2 start biz/application.py --name game-bot-python --interpreter python

sleep 3

echo ""
echo "✅ 部署完成！"
echo ""
echo "📊 服务状态："
pm2 list | grep game-bot

echo ""
echo "📋 最近日志："
pm2 logs game-bot-python --lines 20 --nostream
ENDSSH

# 4. 清理
rm /tmp/bot_deploy.tar.gz

echo ""
echo "🎉 完成！Python Bot 已部署到服务器"
