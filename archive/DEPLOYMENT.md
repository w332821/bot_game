# 服务器部署指南

## 数据库架构说明

**重要发现：Node.js版本使用JSON文件存储，Python版本使用MySQL数据库**

- Node.js版本：数据存储在 `game-data.json` 文件中（使用内存Map和Array）
- Python版本：数据存储在MySQL数据库中（使用SQLModel ORM）

如果需要迁移现有数据，需要从JSON文件导入到MySQL数据库。

## 数据库表结构

Python版本创建以下6个表：

1. **users** - 用户表
   - 主键：id (用户ID，来自悦聊平台)
   - 字段：username, chat_id, balance, score, rebate_ratio, status, role等

2. **bets** - 投注表
   - 主键：id (投注ID)
   - 字段：user_id, game_type, lottery_type, bet_amount, odds, result, pnl等

3. **chats** - 群聊表
   - 主键：id (群聊ID)
   - 字段：name, game_type, owner_id, auto_draw, member_count等

4. **draws** - 开奖历史表
   - 主键：id (自增)
   - 字段：issue, game_type, draw_time, numbers, draw_code等

5. **odds** - 赔率表
   - 主键：id (自增)
   - 字段：game_type, lottery_type, odds_value等

6. **admins** - 管理员表
   - 主键：id (管理员ID)
   - 字段：username, password_hash, role, balance等

## 部署步骤

### 1. 上传项目文件

```bash
# 在本地打包项目
cd /Users/demean5/Desktop
tar -czf bot_game.tar.gz bot_game/

# 上传到服务器
scp bot_game.tar.gz root@your-server:/root/

# 在服务器上解压
ssh root@your-server
cd /root
tar -xzf bot_game.tar.gz
```

### 2. 配置数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE IF NOT EXISTS game_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 确保root用户使用密码认证
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';
FLUSH PRIVILEGES;
EXIT;
```

### 3. 配置项目

```bash
cd /root/bot_game

# 编辑配置文件
vim config.yaml
```

确保`config.yaml`内容正确：
```yaml
db:
  database_uri: "mysql+asyncmy://root:123456@localhost:3306/game_bot"
  sync_database_uri: "mysql+pymysql://root:123456@localhost:3306/game_bot"
  echo: false
```

### 4. 配置环境变量

```bash
# 创建.env文件
cat > .env << 'EOF'
# 悦聊Bot API配置
BOT_API_KEY=your_bot_api_key_here
BOT_API_SECRET=your_bot_api_secret_here

# Bot API服务器地址
BOT_API_BASE_URL=http://myrepdemo.top:3002

# 图片服务器配置（用于开奖图片URL）
IMAGE_HOST=myrepdemo.top
IMAGE_PORT=65035

# 应用配置
APP_ENV=production
LOG_LEVEL=INFO
EOF

# 修改BOT_API_KEY和BOT_API_SECRET为实际值
vim .env
```

### 5. 激活Conda环境并安装依赖

```bash
# 激活conda环境
conda activate bot_game

# 安装依赖
pip install -r requirements.txt
```

### 6. 初始化数据库表

```bash
# 运行数据库初始化脚本
python3 -m base.init_db

# 验证表是否创建成功
mysql -u root -p123456 -e "use game_bot; show tables;"
```

应该看到6个表：
```
+--------------------+
| Tables_in_game_bot |
+--------------------+
| admins             |
| bets               |
| chats              |
| draws              |
| odds               |
| users              |
+--------------------+
```

### 7. （可选）迁移现有数据

如果服务器上有Node.js版本的`game-data.json`文件，需要迁移数据：

```bash
# 运行数据迁移脚本（稍后创建）
python3 scripts/migrate_from_json.py /path/to/game-bot-master/game-data.json
```

### 8. 停止Node.js服务

```bash
# 停止旧的Node.js游戏机器人服务
pm2 stop yueliao-bot

# 停止管理后台（如果不再需要）
pm2 stop admin

# 查看PM2状态
pm2 list
```

### 9. 启动Python服务

```bash
# 使用PM2启动Python服务
pm2 start /opt/anaconda3/envs/bot_game/bin/python \
  --name "game-bot-python" \
  --interpreter none \
  -- -m uvicorn biz.application:app \
  --host 0.0.0.0 \
  --port 3003 \
  --workers 2

# 查看日志
pm2 logs game-bot-python

# 保存PM2配置
pm2 save
```

### 10. 验证服务

```bash
# 检查服务是否在3003端口运行
lsof -i :3003

# 测试健康检查端点
curl http://localhost:3003/health

# 查看API文档
# 浏览器访问：http://your-server:3003/docs
```

### 11. 测试游戏功能

在悦聊群聊中测试以下命令：
- 发送 "余额" - 查询余额
- 发送 "帮助" - 查看帮助信息
- 发送 "反0 100" - 下注测试（澳洲幸运8）
- 发送 "历史" - 查看开奖历史

### 12. 删除旧代码（确认无误后）

```bash
# 确认Python版本运行正常后，删除Node.js备份
cd /root
rm -rf game-bot-master

# 删除PM2中的旧服务配置
pm2 delete yueliao-bot
pm2 delete admin
pm2 save
```

## 故障排查

### 数据库连接问题

```bash
# 检查MySQL是否运行
systemctl status mysql

# 测试数据库连接
mysql -u root -p123456 -e "SELECT 1;"
```

### PM2服务问题

```bash
# 查看详细日志
pm2 logs game-bot-python --lines 100

# 重启服务
pm2 restart game-bot-python

# 查看服务状态
pm2 info game-bot-python
```

### 端口占用问题

```bash
# 查看端口占用
lsof -i :3003

# 如果需要杀掉占用进程
kill -9 <PID>
```

### Python依赖问题

```bash
# 重新安装依赖
conda activate bot_game
pip install -r requirements.txt --force-reinstall
```

## 监控和维护

### 查看服务状态

```bash
pm2 status
pm2 monit
```

### 查看日志

```bash
# 实时日志
pm2 logs game-bot-python

# 错误日志
pm2 logs game-bot-python --err

# 输出日志
pm2 logs game-bot-python --out
```

### 数据库备份

```bash
# 备份数据库
mysqldump -u root -p123456 game_bot > game_bot_backup_$(date +%Y%m%d).sql

# 恢复数据库
mysql -u root -p123456 game_bot < game_bot_backup_YYYYMMDD.sql
```

## 回滚方案

如果Python版本出现问题，需要回滚到Node.js版本：

```bash
# 停止Python服务
pm2 stop game-bot-python

# 启动Node.js服务
pm2 start yueliao-bot
pm2 start admin

# 查看状态
pm2 list
```

## 性能优化建议

1. **数据库索引**：已在表定义中添加关键字段索引
2. **Uvicorn Workers**：根据CPU核心数调整worker数量（当前2个）
3. **数据库连接池**：SQLModel已配置异步连接池
4. **日志级别**：生产环境设置LOG_LEVEL=INFO或WARNING
5. **定期清理**：定期清理旧的开奖记录和投注记录

## 安全注意事项

1. **敏感信息**：
   - 不要将`.env`文件提交到Git
   - 定期更换数据库密码
   - 定期更换BOT_API_KEY和BOT_API_SECRET

2. **数据库安全**：
   - 只允许localhost访问MySQL
   - 使用强密码
   - 定期备份数据

3. **文件权限**：
```bash
chmod 600 .env
chmod 600 config.yaml
```
