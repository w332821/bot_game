# 部署Python Bot到服务器 - 完整指南

## ✅ 已修复的问题

### 1. ChatRepository.get_by_id() 方法缺失
- **文件**: `biz/chat/repo/chat_repo.py`
- **修复**: 添加 `get_by_id()` 别名方法

### 2. chat_repo.create() 方法名错误
- **文件**: `biz/game/webhook/webhook_api.py` (2处)
- **修复**: 将 `chat_repo.create()` 改为 `chat_repo.create_chat()`

### 3. Bot API 认证方式不匹配
- **文件**: `external/bot_api_client.py`
- **修复**: 重写认证为 HMAC-SHA256 签名，使用正确的请求头：
  - `X-API-Key`
  - `X-Signature`
  - `X-Timestamp`

## 📋 验证状态

已通过完整的导入测试：
```
✅ external.bot_api_client 导入成功
✅ ChatRepository 导入成功
✅ UserRepository 导入成功
✅ GameService 导入成功
✅ game_logic 导入成功
✅ webhook_api 导入成功
```

## 🚀 部署步骤

### 方案A: 使用 rsync 同步（推荐）

```bash
# 在本地执行
cd /Users/demean5/Desktop/bot_game

# 同步修复的文件
rsync -avz biz/chat/repo/chat_repo.py root@lbnlsj:/root/bot_game/biz/chat/repo/
rsync -avz biz/game/webhook/webhook_api.py root@lbnlsj:/root/bot_game/biz/game/webhook/
rsync -avz external/bot_api_client.py root@lbnlsj:/root/bot_game/external/

# SSH到服务器重启
ssh root@lbnlsj << 'EOF'
cd /root/bot_game
pm2 stop game-bot-nodejs
pm2 restart game-bot-python
pm2 logs game-bot-python --lines 50
EOF
```

### 方案B: 使用 scp 逐个复制

```bash
# 在本地执行
scp /Users/demean5/Desktop/bot_game/biz/chat/repo/chat_repo.py \
    root@lbnlsj:/root/bot_game/biz/chat/repo/

scp /Users/demean5/Desktop/bot_game/biz/game/webhook/webhook_api.py \
    root@lbnlsj:/root/bot_game/biz/game/webhook/

scp /Users/demean5/Desktop/bot_game/external/bot_api_client.py \
    root@lbnlsj:/root/bot_game/external/

# 然后SSH重启
ssh root@lbnlsj
cd /root/bot_game
pm2 stop game-bot-nodejs
pm2 restart game-bot-python
pm2 logs game-bot-python --lines 50
```

### 方案C: 使用 Git 同步（如果已配置）

```bash
# 在服务器上执行
cd /root/bot_game
git pull origin main  # 或你的分支名
pm2 stop game-bot-nodejs
pm2 restart game-bot-python
pm2 logs game-bot-python
```

## ⚙️ 环境变量检查

确保服务器上的 `/root/bot_game/.env` 文件包含正确的配置：

```bash
# 在服务器上检查
cat /root/bot_game/.env | grep BOT_API
```

应该看到：
```
BOT_API_BASE=http://127.0.0.1:65035
BOT_API_KEY=your_actual_api_key_here
BOT_API_SECRET=your_actual_api_secret_here
```

**重要**: 如果 `BOT_API_KEY` 和 `BOT_API_SECRET` 还是占位符，需要从 Node.js 服务获取真实的凭证。

### 获取真实的 Bot 凭证

如果需要重新注册 Bot 获取凭证：

```bash
# 方法1: 从 Node.js 的环境变量中获取
cd ~/yueliao-server
grep BOT_API .env

# 方法2: 查看 Node.js 的日志中是否有凭证信息
pm2 logs game-bot-nodejs --lines 200 | grep "API_KEY\|API_SECRET"

# 方法3: 如果都没有，可能需要重新注册Bot
# 参考 game-bot-master 中的注册脚本
```

## 🧪 测试验证

部署后执行以下测试：

### 1. 检查服务状态
```bash
pm2 list
# 应该看到 game-bot-python 状态为 online
# game-bot-nodejs 状态为 stopped
```

### 2. 查看启动日志
```bash
pm2 logs game-bot-python --lines 100
```

**期望看到**:
```
✅ 环境变量验证通过
✅ MongoDB连接成功 (如果使用MySQL则是数据库连接成功)
INFO: Application startup complete.
```

**不应该看到**:
```
❌ Bot API请求失败: 401
❌ Missing authentication headers
AttributeError: 'ChatRepository' object has no attribute 'get_by_id'
```

### 3. 测试 Webhook 接收
创建一个新群聊，Bot应该自动加入并发送欢迎消息。

查看日志：
```bash
pm2 logs game-bot-python --lines 50 | grep "group.created"
```

### 4. 测试消息处理
在群聊中发送 "查" 或下注命令（如 "1番100"），查看日志：
```bash
pm2 logs game-bot-python --lines 50 | grep "message.received"
```

### 5. 测试 Bot API 认证
应该不再看到 401 错误：
```bash
pm2 logs game-bot-python --err --lines 50 | grep 401
# 应该没有输出
```

## 🔧 故障排查

### 问题1: 仍然看到 401 认证错误

**原因**: Bot API 凭证未正确配置

**解决**:
```bash
cd /root/bot_game
# 检查 .env 文件
cat .env | grep BOT_API

# 如果是占位符，需要更新为真实凭证
# 可以从 game-bot-nodejs 的配置中复制
vi .env
# 编辑 BOT_API_KEY 和 BOT_API_SECRET

# 重启服务
pm2 restart game-bot-python
```

### 问题2: ImportError 或 ModuleNotFoundError

**原因**: 依赖包未安装

**解决**:
```bash
cd /root/bot_game
source venv/bin/activate  # 如果使用虚拟环境
pip install -r requirements.txt
pm2 restart game-bot-python
```

### 问题3: 数据库连接失败

**原因**: 数据库配置错误

**解决**:
```bash
cd /root/bot_game
cat config.yaml  # 检查数据库配置

# 测试数据库连接
python -c "import asyncio; from base.database import engine; asyncio.run(engine.connect())"

# 如果失败，检查数据库服务是否运行
systemctl status mysql  # 或 mariadb
```

### 问题4: 代码没有更新

**原因**: 文件传输失败或路径错误

**解决**:
```bash
# 在服务器上检查文件修改时间
ls -la /root/bot_game/biz/chat/repo/chat_repo.py
ls -la /root/bot_game/external/bot_api_client.py

# 如果时间不对，重新传输
# 或者直接在服务器上编辑
```

## 📊 性能监控

部署后持续监控：

```bash
# 实时查看日志
pm2 logs game-bot-python

# 查看进程状态
pm2 monit

# 查看重启次数（应该保持稳定）
pm2 list
# 如果重启次数持续增加，说明有问题

# 重置重启计数器（验证后）
pm2 reset game-bot-python
```

## ✅ 成功标志

部署成功的标志：

1. ✅ `pm2 list` 显示 `game-bot-python` 在线，`game-bot-nodejs` 停止
2. ✅ 日志中没有 401 认证错误
3. ✅ 日志中没有 AttributeError
4. ✅ 可以创建群聊，Bot 自动加入
5. ✅ 可以发送消息，Bot 正确响应
6. ✅ 下注功能正常工作
7. ✅ 余额查询正常工作
8. ✅ 自动开奖正常工作

## 🔄 回滚方案

如果 Python 版本出现问题，可以快速回滚到 Node.js 版本：

```bash
ssh root@lbnlsj
pm2 stop game-bot-python
pm2 start game-bot-nodejs
pm2 logs game-bot-nodejs
```

## 📞 支持

如果遇到其他问题：

1. 查看完整日志：`pm2 logs game-bot-python --lines 500`
2. 查看错误日志：`pm2 logs game-bot-python --err --lines 200`
3. 检查系统资源：`htop` 或 `free -h`
4. 检查磁盘空间：`df -h`
