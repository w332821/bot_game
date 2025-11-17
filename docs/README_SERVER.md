# 🎮 Game Bot 服务器部署指南

## 📁 项目结构

```
/root/bot_game/bot_game/
├── biz/                    # Python 业务代码
│   ├── application.py     # 应用入口 ⭐
│   ├── containers.py      # 依赖注入
│   ├── game/             # 游戏逻辑
│   ├── user/             # 用户管理
│   ├── chat/             # 群聊管理
│   └── odds/             # 赔率配置
├── base/                  # 基础设施
├── external/              # 外部API
├── .env                   # 环境变量 ⭐
├── config.yaml           # 数据库配置 ⭐
├── ecosystem.config.js   # PM2配置 ⭐
└── start_bot.sh          # 启动脚本 ⭐
```

---

## 🚀 快速启动（服务器上）

### 一键启动

```bash
cd /root/bot_game/bot_game
pm2 start start_bot.sh --name game-bot-python --interpreter bash
pm2 logs game-bot-python
```

### 使用 ecosystem.config.js

```bash
cd /root/bot_game/bot_game
pm2 start ecosystem.config.js --only game-bot-python
pm2 logs game-bot-python
```

---

## 📝 常用命令

```bash
# 查看状态
pm2 list

# 重启应用
pm2 restart game-bot-python

# 停止应用
pm2 stop game-bot-python

# 查看日志
pm2 logs game-bot-python --lines 100

# 删除应用
pm2 delete game-bot-python

# 保存配置（开机自启）
pm2 save
```

---

## ⚙️ 配置文件说明

### 1. `.env` - 环境变量

```bash
# Bot API凭证（必填）
BOT_API_KEY=bot_6f00c30fddca681b4b78a70403823200
BOT_API_SECRET=1da850e2272f0185b9dd7d1197ef0ad87ae79d830e6d38ffedf0b9ac0a99e4dd

# 服务器配置
BOT_API_BASE=http://127.0.0.1:65035
WEBHOOK_PORT=3003
```

### 2. `config.yaml` - 数据库配置

```yaml
db:
  database_uri: "mysql+asyncmy://root:password@localhost:3306/game_bot"
  sync_database_uri: "mysql+pymysql://root:password@localhost:3306/game_bot"
```

---

## 🔧 故障排查

### 问题1: 进程状态为 `errored`

```bash
# 查看错误日志
pm2 logs game-bot-python --err --lines 50

# 删除重启
pm2 delete game-bot-python
pm2 start start_bot.sh --name game-bot-python --interpreter bash
```

### 问题2: 端口被占用

```bash
# 查看端口占用
lsof -i :3003

# 停止所有game-bot进程
pm2 delete all
```

### 问题3: ModuleNotFoundError: No module named 'biz'

这是因为Python找不到项目模块。已在 `start_bot.sh` 中添加了 `PYTHONPATH` 设置。

如果仍然报错，手动检查：
```bash
cd /root/bot_game/bot_game
export PYTHONPATH="/root/bot_game/bot_game:$PYTHONPATH"
conda activate bot_game
python -c "import biz"
```

### 问题4: 找不到conda或conda init错误

**方法1：找到正确的conda路径**
```bash
# 找到conda位置
which conda

# 假设输出是 /opt/anaconda3/bin/conda
# 那么conda.sh路径就是
ls -la /opt/anaconda3/etc/profile.d/conda.sh

# 编辑start_bot.sh，确保包含正确路径
```

**方法2：初始化conda**
```bash
conda init bash
source ~/.bashrc
```

**方法3：直接使用Python完整路径（不依赖conda activate）**

编辑 `start_bot.sh` 最后一行：
```bash
# 改为使用完整Python路径
/opt/anaconda3/envs/bot_game/bin/python biz/application.py
```

---

## 📚 相关文档

- PM2_GUIDE.md - PM2详细使用指南
- README.md - 项目完整说明
- QUICKSTART.md - 快速开始
- CLAUDE.md - AI开发说明

---

## ✅ 启动检查清单

启动前确保：

- [ ] conda环境 `bot_game` 已创建
- [ ] `.env` 文件包含正确的API密钥
- [ ] `config.yaml` 数据库配置正确
- [ ] MySQL服务正在运行
- [ ] 端口3003未被占用
- [ ] `start_bot.sh` 有执行权限

启动后验证：

- [ ] `pm2 list` 显示状态为 `online`
- [ ] 日志无错误信息
- [ ] 访问 `http://localhost:3003/health` 返回正常
- [ ] Webhook能正常接收消息