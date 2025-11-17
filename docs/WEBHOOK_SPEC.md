# Webhook接口规范文档

## 核心要求
**App端代码不能改动，必须保证入参/出参格式100%兼容Node.js版本**

---

## 1. POST /webhook

### 请求格式
```json
{
  "event": "message.received | group.created | member.joined",
  "data": {
    // 根据event类型不同，data结构不同
  }
}
```

### 响应格式
```json
{
  "status": "ok"
}
```

### 错误响应
```json
{
  "status": "error",
  "error": "错误信息"
}
```

---

## 2. 事件类型详解

### 2.1 group.created（群聊创建）

**请求数据结构**:
```json
{
  "event": "group.created",
  "data": {
    "chat": {
      "id": "chat_123",
      "name": "测试群"
    }
  }
}
```

**处理逻辑**:
1. 调用悦聊Bot API加入群聊: `POST /api/bot/join/{chatId}`
2. 创建群聊记录（初始游戏类型: lucky8）
3. 启动自动开奖定时器
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

---

### 2.2 member.joined（新成员加入）

**请求数据结构**:
```json
{
  "event": "member.joined",
  "data": {
    "chat": {
      "id": "chat_123"
    },
    "member": {
      "id": "user_456",
      "name": "张三"
    }
  }
}
```

**处理逻辑**:
1. 检查用户是否已存在
2. 如果不存在，创建新用户（初始余额: 1000）

---

### 2.3 message.received（接收到消息）

**请求数据结构**:
```json
{
  "event": "message.received",
  "data": {
    "message": {
      "content": "查",
      "chat": {
        "id": "chat_123",
        "name": "测试群"
      },
      "sender": {
        "_id": "user_456",  // 或 "id"
        "id": "user_456",
        "name": "张三",
        "isBot": false
      }
    }
  }
}
```

**处理逻辑**:

#### 1. 忽略机器人消息
```javascript
if (message.sender.isBot) {
  return { status: 'ok' };
}
```

#### 2. 确保群聊存在
如果群聊不存在，创建群聊并启动定时器

#### 3. 确保用户存在
如果用户不存在，创建用户（初始余额: 1000）

#### 4. 根据消息内容分发处理

| 指令 | 触发条件 | 处理函数 |
|------|---------|---------|
| 查询余额 | `查` / `查询` / `余额` | handleQueryBalance |
| 排行榜 | `排行` / `排行榜` | handleLeaderboard |
| 流水记录 | `流水` / `历史` / `记录` | handleBetHistory |
| 取消下注 | `取消` | handleCancelBet |
| 立即开奖 | `开奖` / `立即开奖` | executeDraw |
| 开奖历史 | `开奖历史` | handleDrawHistory |
| 下注 | 包含下注格式 | handleBetMessage |
| 无效输入 | 其他 | 回复"@用户名 输入无效" |

---

## 3. 处理函数详细规范

### 3.1 handleQueryBalance（查询余额）

**响应消息格式**:
```
@张三 余额: 1250.00
```

---

### 3.2 handleLeaderboard（排行榜）

**响应消息格式**:
```
【排行榜】
1. 张三 - 1250.00 (+250.00)
2. 李四 - 980.00 (-20.00)
3. 王五 - 850.00 (-150.00)
```

**数据获取**:
- 获取群内所有用户
- 按余额降序排序
- 显示余额和盈亏（初始余额1000）

---

### 3.3 handleBetHistory（流水记录）

**响应消息格式**:
```
@张三
今日流水：500.00，今日盈亏：+150.00
```

**统计规则**:
- 今日流水 = sum(今日所有下注金额)
- 今日盈亏 = sum(今日所有bet.profit)
- 时间范围: 当天00:00:00 开始

---

### 3.4 handleBetMessage（下注处理）

**处理流程**:

1. **解析下注指令**
   ```javascript
   const bets = gameLogic.parseBets(content, sender.name);
   ```

2. **验证每个下注**
   - 检查余额是否足够
   - 验证玩法是否匹配游戏类型（六合彩只支持特码）
   - 检查金额、号码范围

3. **扣除余额**
   ```javascript
   totalAmount = sum(bets[].amount)
   user.balance -= totalAmount
   ```

4. **保存下注记录**
   - 存入 bets 表
   - 状态: pending
   - 保存当前期号

5. **发送确认消息**
   ```
   📝 下注成功！

   1. 番 3 - 200元 (赔率3.0)
   2. 正 1 - 100元 (赔率2.0)

   总金额: 300元
   余额: 700.00
   期号: 20250113001
   ```

**失败响应**:
```
❌ 下注失败: 余额不足（当前余额: 150.00，需要: 300.00）
```

---

### 3.5 executeDraw（开奖）

...（内容同原文）