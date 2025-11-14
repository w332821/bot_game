# PM2 启动指南

## 项目结构说明

```
/root/bot_game/bot_game/          # 项目根目录
├── biz/                           # Python 业务代码
│   └── application.py            # Python 应用入口
├── base/                          # Python 基础设施
├── external/                      # Python 外部接口
├── game-bot-master/              # Node.js 版本（旧版本）
│   └── bot-server.js             # Node.js 应用入口
├── .env                          # 环境变量配置
├── config.yaml                   # 数据库配置
├── ecosystem.config.js           # PM2 配置文件
└── start_bot.sh                  # Python 启动脚本
```

---

## 方式一：使用 ecosystem.config.js（推荐）

### 1. 确保 ecosystem.config.js 存在

已创建在项目根目录，配置了两个应用：
- `game-bot-python` - Python 版本（新版本）
- `game-bot-nodejs` - Node.js 版本（旧版本）

### 2. 启动命令

```bash
cd /root/bot_game/bot_game

# 启动 Python 版本
pm2 start ecosystem.config.js --only game-bot-python

# 启动 Node.js 版本
pm2 start ecosystem.config.js --only game-bot-nodejs

# 同时启动两个
pm2 start ecosystem.config.js

# 重启
pm2 restart game-bot-python
pm2 restart game-bot-nodejs

# 停止
pm2 stop game-bot-python
pm2 stop game-bot-nodejs

# 删除
pm2 delete game-bot-python
pm2 delete game-bot-nodejs

# 查看日志
pm2 logs game-bot-python
pm2 logs game-bot-nodejs
```

---

## 方式二：直接使用 PM2 命令（简单快速）

### Python 版本启动

**前提条件：**
1. 已激活 conda 环境 `bot_game`
2. 在项目根目录 `/root/bot_game/bot_game`

**启动命令：**

```bash
# 方法1：使用 start_bot.sh 脚本（推荐）
cd /root/bot_game/bot_game
pm2 start start_bot.sh --name game-bot-python --interpreter bash

# 方法2：直接指定 Python 解释器
cd /root/bot_game/bot_game
conda activate bot_game
pm2 start biz/application.py \
  --name game-bot-python \
  --interpreter $(which python) \
  --cwd /root/bot_game/bot_game
```

### Node.js 版本启动

```bash
cd /root/bot_game/bot_game/game-bot-master
pm2 start bot-server.js --name game-bot-nodejs
```

---

## 常用 PM2 命令

```bash
# 查看所有进程
pm2 list

# 查看详细信息
pm2 show game-bot-python

# 实时日志
pm2 logs game-bot-python --lines 100

# 查看监控
pm2 monit

# 重启所有应用
pm2 restart all

# 停止所有应用
pm2 stop all

# 保存当前配置（开机自启）
pm2 save

# 设置开机自启
pm2 startup
```

---

## 故障排查

### 1. 进程状态为 `errored`

```bash
# 查看错误日志
pm2 logs game-bot-python --err --lines 50

# 删除旧进程重新启动
pm2 delete game-bot-python
pm2 start ecosystem.config.js --only game-bot-python
```

### 2. 找不到 Python 模块 (ModuleNotFoundError)

确保：
- 当前目录是项目根目录 `/root/bot_game/bot_game`
- 使用 `--cwd` 参数指定正确路径
- conda 环境已激活

### 3. 环境变量未加载

确保：
- `.env` 文件存在且包含正确的 API 密钥
- `config.yaml` 数据库配置正确
- 重启应用后生效

### 4. conda 环境问题

```bash
# 检查 conda 路径
which conda

# 初始化 conda（如果需要）
conda init bash
source ~/.bashrc

# 激活环境
conda activate bot_game

# 检查 Python 路径
which python
```

---

## 服务器快速启动步骤

**完整启动流程（从零开始）：**

```bash
# 1. 进入项目目录
cd /root/bot_game/bot_game

# 2. 检查配置文件
ls -la .env config.yaml

# 3. 删除所有旧进程
pm2 delete all

# 4. 启动 Python 版本
pm2 start start_bot.sh --name game-bot-python --interpreter bash

# 5. 查看日志确认启动成功
pm2 logs game-bot-python --lines 50

# 6. 保存配置
pm2 save

# 7. 查看状态
pm2 list
```

预期输出：
```
┌────┬──────────────────┬─────────┬──────┬──────────┬─────────┬─────────┐
│ id │ name             │ mode    │ ↺    │ status   │ cpu     │ memory  │
├────┼──────────────────┼─────────┼──────┼──────────┼─────────┼─────────┤
│ 0  │ game-bot-python  │ fork    │ 0    │ online   │ 0%      │ 45.2mb  │
└────┴──────────────────┴─────────┴──────┴──────────┴─────────┴─────────┘
```

---

## 注意事项

1. **只运行一个版本**：Python 版本和 Node.js 版本不要同时运行（都监听 3003 端口）
2. **环境变量**：确保 `.env` 文件中的 `BOT_API_KEY` 和 `BOT_API_SECRET` 已配置
3. **数据库**：确保 MySQL 服务运行且 `config.yaml` 配置正确
4. **端口占用**：如果 3003 端口被占用，先停止旧进程
5. **日志位置**：日志在 `/root/.pm2/logs/` 目录下
