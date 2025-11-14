# App端 API 端点文档

本文档详细说明了游戏机器人App端的所有API端点，包括Webhook接收和游戏类型同步。

## 目录
- [概述](#概述)
- [Webhook端点](#webhook端点)
- [同步游戏类型端点](#同步游戏类型端点)
- [环境配置](#环境配置)
- [测试指南](#测试指南)
- [错误处理](#错误处理)

---

## 概述

**基础URL**: `http://localhost:3003`

App端提供两个核心端点:
1. `/webhook` - 接收悦聊Bot的消息事件
2. `/api/sync-gametype` - 同步Admin端的游戏类型变更

**端口**: 3003 (与Node.js版本保持一致)

**兼容性**: 100%兼容Node.js版本的入参/出参格式

---

## Webhook端点

### POST /webhook

接收悦聊Bot推送的消息事件。

#### 请求头
```http
Content-Type: application/json
```

#### 事件类型

##### 1. 群聊创建事件 (`group.created`)

当机器人被邀请加入群聊时触发。

**请求体**:
```json
{
  "event": "group.created",
  "data": {
    "chat": {
      "id": "chat_12345",
      "name": "测试群聊",
      "type": "group"
    }
  }
}
```

**处理逻辑**:
1. 自动加入群聊
2. 创建群聊记录（默认游戏类型: `lucky8`）
3. 启动自动开奖定时器（5分钟间隔）
4. 同步群聊成员
5. 发送欢迎消息

**欢迎消息内容**:
```
🎰【澳洲幸运8游戏机器人】🎰

欢迎使用！初始余额: 1000

📋 玩法说明:
• 番: "番 3/200" 或 "3番200" (赔率3倍)
• 正: "正1/200" 或 "1/200" (赔率2倍)
• 单双: "单200" 或 "双150" (赔率2倍)

🔍 查询指令:
• "查" - 查询余额
• "排行" - 查看排行榜

⏰ 每5分钟自动开奖
💰 这是虚拟货币游戏，仅供娱乐！
```

##### 2. 新成员加入事件 (`member.joined`)

当新成员加入群聊时触发。

**请求体**:
```json
{
  "event": "member.joined",
  "data": {
    "member": {
      "id": "user_12345",
      "name": "张三",
      "isBot": false
    },
    "chat": {
      "id": "chat_12345",
      "name": "测试群聊"
    }
  }
}
```

**处理逻辑**:
1. 创建用户记录（初始余额: 1000）
2. 关联用户到群聊

##### 3. 消息接收事件 (`message.received`)

当群聊中有消息时触发。

**请求体**:
```json
{
  "event": "message.received",
  "data": {
    "message": {
      "id": "msg_12345",
      "content": "查",
      "chat": {
        "id": "chat_12345",
        "name": "测试群聊"
      },
      "sender": {
        "_id": "user_12345",
        "id": "user_12345",
        "name": "张三",
        "isBot": false
      }
    }
  }
}
```

**支持的消息指令**:

| 指令 | 别名 | 功能 | 响应格式 |
|------|------|------|----------|
| `查` | `查询`, `余额` | 查询余额 | 文本消息 |
| `排行` | `排行榜` | 查看排行榜 | 文本消息 |
| `流水` | `历史`, `记录` | 查看投注历史 | 文本消息 |
| `取消` | - | 取消当前期投注 | 文本消息 |
| `开奖` | `立即开奖` | 手动触发开奖 | 文本消息 + 图片 |
| `开奖历史` | - | 查看历史开奖 | 图片 |

**下注指令格式**:

澳洲幸运8:
```
番 3/200       # 3番下注200
3番200         # 同上
正1/200        # 正1下注200
1/200          # 正1下注200（简写）
单200          # 单下注200
双150          # 双下注150
```

六合彩:
```
1/200          # 号码1下注200
大200          # 大下注200
小150          # 小下注150
单200          # 单下注200
双150          # 双下注150
红波200        # 红波下注200
绿波150        # 绿波下注150
蓝波100        # 蓝波下注100
```

#### 响应

**成功响应** (200 OK):
```json
{
  "status": "ok"
}
```

**错误响应** (200 OK with error):
```json
{
  "status": "error",
  "error": "错误描述"
}
```

**注意**: Webhook端点始终返回200状态码，具体成功/失败通过`status`字段判断。

---

## 同步游戏类型端点

### POST /api/sync-gametype

当Admin端修改群聊的游戏类型时调用此端点。

#### 请求头
```http
Content-Type: application/json
```

#### 请求体
```json
{
  "chatId": "chat_12345",
  "gameType": "liuhecai",
  "oldGameType": "lucky8"
}
```

**字段说明**:
- `chatId` (string, required): 群聊ID
- `gameType` (string, required): 新游戏类型，可选值: `lucky8` | `liuhecai`
- `oldGameType` (string, optional): 旧游戏类型

#### 处理逻辑
1. 更新群聊的游戏类型
2. 停止旧游戏类型的定时器
3. 启动新游戏类型的定时器
   - `lucky8`: 5分钟间隔
   - `liuhecai`: 24小时间隔

#### 响应

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "游戏彩种已同步"
}
```

**失败响应** (200 OK with error):
```json
{
  "success": false,
  "error": "错误描述"
}
```

---

## 环境配置

### 1. 配置文件 (config.yaml)

```yaml
# 数据库配置
database_uri: "mysql+asyncmy://user:password@localhost:3306/game_bot"
sync_database_uri: "mysql+pymysql://user:password@localhost:3306/game_bot"
echo: false

# Bot API配置（环境变量）
BOT_API_BASE_URL: "https://bot-api.yueliao.com"
BOT_API_KEY: "your_bot_api_key"
BOT_API_SECRET: "your_bot_api_secret"
```

### 2. 环境变量

创建 `.env` 文件:
```bash
# Bot API 配置
BOT_API_BASE_URL=https://bot-api.yueliao.com
BOT_API_KEY=your_bot_api_key_here
BOT_API_SECRET=your_bot_api_secret_here

# 第三方开奖API配置（可选）
LUCKY8_API_BASE=https://api.example.com/lucky8
LIUHECAI_API_BASE=https://api.example.com/liuhecai
```

---

## 测试指南

### 1. 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -m base.init_db

# 启动服务
python biz/application.py
```

服务将在 `http://localhost:3003` 启动。

### 2. 测试Webhook - 群聊创建

使用curl测试:
```bash
curl -X POST http://localhost:3003/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "group.created",
    "data": {
      "chat": {
        "id": "test_chat_001",
        "name": "测试群聊",
        "type": "group"
      }
    }
  }'
```

**预期结果**:
- 返回 `{"status": "ok"}`
- 日志显示群聊创建成功
- 自动开奖定时器启动

### 3. 测试Webhook - 新成员加入

```bash
curl -X POST http://localhost:3003/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "member.joined",
    "data": {
      "member": {
        "id": "test_user_001",
        "name": "测试用户",
        "isBot": false
      },
      "chat": {
        "id": "test_chat_001",
        "name": "测试群聊"
      }
    }
  }'
```

**预期结果**:
- 返回 `{"status": "ok"}`
- 用户记录创建成功（余额1000）

### 4. 测试Webhook - 查询余额

```bash
curl -X POST http://localhost:3003/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message.received",
    "data": {
      "message": {
        "id": "msg_001",
        "content": "查",
        "chat": {
          "id": "test_chat_001",
          "name": "测试群聊"
        },
        "sender": {
          "_id": "test_user_001",
          "id": "test_user_001",
          "name": "测试用户",
          "isBot": false
        }
      }
    }
  }'
```

**预期结果**:
- 返回 `{"status": "ok"}`
- 调用Bot API发送余额消息

### 5. 测试Webhook - 下注

```bash
curl -X POST http://localhost:3003/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message.received",
    "data": {
      "message": {
        "id": "msg_002",
        "content": "番 3/200",
        "chat": {
          "id": "test_chat_001",
          "name": "测试群聊"
        },
        "sender": {
          "_id": "test_user_001",
          "id": "test_user_001",
          "name": "测试用户",
          "isBot": false
        }
      }
    }
  }'
```

**预期结果**:
- 返回 `{"status": "ok"}`
- 扣除余额200
- 创建下注记录
- 发送下注确认消息

### 6. 测试同步游戏类型

```bash
curl -X POST http://localhost:3003/api/sync-gametype \
  -H "Content-Type: application/json" \
  -d '{
    "chatId": "test_chat_001",
    "gameType": "liuhecai",
    "oldGameType": "lucky8"
  }'
```

**预期结果**:
- 返回 `{"success": true, "message": "游戏彩种已同步"}`
- 定时器从5分钟切换到24小时

### 7. 测试自动开奖

等待5分钟后，检查日志:
```bash
# 应该看到类似日志
🎲 定时开奖触发: 群=test_chat_001
📊 开奖结算开始: 群=test_chat_001
✅ 定时开奖完成: 群=test_chat_001
```

**预期结果**:
- 定时器触发开奖
- 结算所有待处理下注
- 发送开奖公告

### 8. 测试开奖历史

```bash
curl -X POST http://localhost:3003/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message.received",
    "data": {
      "message": {
        "id": "msg_003",
        "content": "开奖历史",
        "chat": {
          "id": "test_chat_001",
          "name": "测试群聊"
        },
        "sender": {
          "_id": "test_user_001",
          "id": "test_user_001",
          "name": "测试用户",
          "isBot": false
        }
      }
    }
  }'
```

**预期结果**:
- 返回 `{"status": "ok"}`
- 生成开奖历史图片
- 调用Bot API发送图片

---

## 错误处理

### 常见错误

#### 1. Bot API调用失败
```
❌ 发送消息失败: chat=test_chat_001, 错误=401 Unauthorized
```
**解决方案**: 检查 `.env` 文件中的 `BOT_API_KEY` 和 `BOT_API_SECRET`

#### 2. 数据库连接失败
```
❌ 数据库错误: Can't connect to MySQL server
```
**解决方案**: 检查 `config.yaml` 中的数据库连接字符串

#### 3. 余额不足
```
❌ 余额不足: 用户=test_user_001, 当前余额=500, 需要=800
```
**解决方案**: 这是正常的业务逻辑，用户需要等待盈利或管理员充值

#### 4. 图片生成失败
```
❌ 生成开奖历史图片失败: No module named 'PIL'
```
**解决方案**: 确保已安装Pillow: `pip install Pillow>=10.0.0`

#### 5. 定时器异常
```
❌ 定时开奖失败: 群=test_chat_001, 错误=...
```
**解决方案**: 检查日志中的详细错误信息，定时器会继续运行

---

## 开奖规则

### 澳洲幸运8

**开奖数据**:
- 期号格式: `YYYYMMDD` + 三位序号 (例: `20250113001`)
- 开奖号码: 20个号码（1-80）
- 特码: 第8位号码映射到1-20范围
- 番数: 1-4（根据特码计算）

**结算规则**:
- 番: 下注番数与开奖番数一致，赔率3倍
- 正: 下注号码与特码一致，赔率2倍
- 单双: 特码的单双匹配，赔率2倍

### 六合彩

**开奖数据**:
- 期号格式: `YYYYMMDD` (例: `20250113`)
- 开奖号码: 7个号码（1-49）
- 特码: 最后一个号码

**结算规则**:
- 号码: 下注号码与特码一致，赔率40倍
- 大小: 特码25-49为大，1-24为小，赔率2倍
- 单双: 特码的单双匹配，赔率2倍
- 波色: 赔率3倍
  - 红波: 1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46
  - 蓝波: 3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48
  - 绿波: 5,6,11,16,17,21,22,27,28,32,33,38,39,43,44,49

---

## 性能优化

### 1. 数据库索引
确保以下字段有索引:
- `bet.user_id`
- `bet.chat_id`
- `bet.issue`
- `bet.status`
- `draw.chat_id`
- `draw.game_type`

### 2. 定时器管理
- 每个群聊独立定时器
- 应用关闭时自动清理所有定时器
- 支持热重启（切换游戏类型）

### 3. API缓存
- Bot API客户端使用单例模式
- 第三方开奖API可添加结果缓存

---

## 监控和日志

### 日志级别
- `INFO`: 正常操作（启动、开奖、下注）
- `WARNING`: 非关键错误（API请求失败、余额不足）
- `ERROR`: 关键错误（数据库错误、系统异常）

### 关键日志
```
# 应用启动
🚀 应用启动中...
✅ 开奖调度器已初始化

# 群聊事件
✅ 已加入群聊: 测试群聊
⏰ 已启动自动开奖定时器: test_chat_001

# 下注处理
💰 下注成功: 用户=张三, 下注类型=番, 金额=200

# 开奖结算
🎲 定时开奖触发: 群=test_chat_001
📊 开奖结算开始: 群=test_chat_001, 期号=20250113001
✅ 定时开奖完成: 群=test_chat_001

# 应用关闭
🔴 应用关闭中...
⏹️ 停止所有定时器，共 3 个
✅ 应用已关闭
```

---

## 与Node.js版本的差异

### 完全兼容
- ✅ Webhook入参/出参格式
- ✅ 同步游戏类型接口
- ✅ 所有消息指令
- ✅ 开奖规则和赔率
- ✅ 定时器间隔时间
- ✅ 端口号(3003)

### 实现差异（不影响兼容性）
- 使用AsyncIO替代Node.js的EventLoop
- 使用SQLAlchemy替代Sequelize ORM
- 使用Pillow替代Node.js的canvas库
- 使用aiohttp替代axios

---

## 下一步

App端核心功能已完成，接下来可以:

1. **集成真实的第三方开奖API**
   - 编辑 `external/draw_api_client.py`
   - 取消注释真实API调用
   - 配置API地址和认证信息

2. **优化图片生成**
   - 美化开奖历史图片样式
   - 添加群聊logo和标题
   - 支持自定义字体

3. **增加管理功能**
   - 用户余额充值
   - 批量查询群聊状态
   - 开奖记录导出

4. **性能监控**
   - 添加Prometheus指标
   - 接入日志聚合系统
   - 设置告警规则

5. **部署上线**
   - 配置生产环境数据库
   - 使用Gunicorn/Uvicorn多进程部署
   - 配置Nginx反向代理
   - 设置HTTPS证书
