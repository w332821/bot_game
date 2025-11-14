# 🚀 游戏机器人系统 - 安装指南

## Step 1: 安装Python依赖

```bash
cd /Users/demean5/Desktop/bot_game
pip install -r requirements.txt
```

## Step 2: 创建MySQL数据库

### 方式1: 使用MySQL命令行

```bash
# 登录MySQL
mysql -u root -p

# 执行SQL脚本
source /Users/demean5/Desktop/123321/database/schema_with_guide.sql

# 或者一条命令执行
mysql -u root -p < /Users/demean5/Desktop/123321/database/schema_with_guide.sql
```

### 方式2: 验证数据库创建成功

```bash
mysql -u root -p

# 进入MySQL后执行
USE game_bot;
SHOW TABLES;

# 应该显示12张表:
# +---------------------+
# | Tables_in_game_bot  |
# +---------------------+
# | account_changes     |
# | admin_accounts      |
# | bets                |
# | chats               |
# | deposit_records     |
# | draw_history        |
# | odds_config         |
# | operation_logs      |
# | rebate_records      |
# | user_stats          |
# | users               |
# | wallet_transfers    |
# +---------------------+

# 检查默认数据
SELECT * FROM admin_accounts;  # 应该有admin/admin123
SELECT * FROM odds_config;     # 应该有11条赔率配置

# 退出
exit;
```

## Step 3: 配置数据库连接

编辑 `config.yaml`，修改数据库密码（如果不是root/password）:

```yaml
db:
  database_uri: "mysql+asyncmy://root:你的密码@localhost:3306/game_bot"
  sync_database_uri: "mysql+pymysql://root:你的密码@localhost:3306/game_bot"
  echo: False
```

## Step 4: 配置悦聊Bot API

编辑 `.env` 文件，设置Bot API密钥：

```bash
BOT_API_BASE=http://127.0.0.1:65035
BOT_API_KEY=你的API密钥
BOT_API_SECRET=你的API密钥Secret
```

## Step 5: 测试数据库连接

```bash
cd /Users/demean5/Desktop/bot_game
python -m base.init_db
```

如果成功，应该看到：
```
✅ 数据库连接成功
✅ 所有表已创建
```

## Step 6: 启动服务

```bash
# 开发模式（端口3003）
uvicorn biz.application:app --reload --port 3003

# 或者
python biz/application.py
```

## Step 7: 访问API文档

浏览器打开：
- http://localhost:3003/docs
- http://localhost:3003/health

## 🎯 完成后应该看到

1. **数据库**: game_bot数据库，12张表
2. **服务器**: 端口3003运行
3. **API文档**: Swagger UI可访问
4. **Webhook**: POST /webhook接口ready

## 🔧 故障排查

### 问题1: MySQL连接失败

```bash
# 检查MySQL是否运行
mysql -u root -p

# 检查端口
netstat -an | grep 3306

# 检查用户权限
GRANT ALL PRIVILEGES ON game_bot.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### 问题2: Python依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 单独安装问题依赖
pip install sqlmodel
pip install fastapi
```

### 问题3: 端口被占用

```bash
# 检查端口占用
lsof -i :3003

# 杀死占用进程
kill -9 <PID>

# 或使用其他端口
uvicorn biz.application:app --port 4003
```

## ✅ 验收清单

- [ ] MySQL数据库game_bot创建成功
- [ ] 12张表全部存在
- [ ] admin_accounts有默认管理员
- [ ] odds_config有11条配置
- [ ] Python依赖安装成功
- [ ] uvicorn能启动服务
- [ ] http://localhost:3003/docs可访问
- [ ] http://localhost:3003/health返回200

全部通过后，进入下一步：创建业务模块！
