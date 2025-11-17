# App端 API 端点文档

本文档详细说明了游戏机器人App端的所有API端点，包括Webhook接收和游戏类型同步。

## 目录
- 概述
- Webhook端点
- 同步游戏类型端点
- 环境配置
- 测试指南
- 错误处理

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
| 下注指令 | 下注 | 番、正、单双、号码等 |

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

#### 响应

```json
{
  "success": true,
  "message": "游戏彩种已同步"
}
```

---

## 环境配置

详见项目根目录 `.env` 与 `config.yaml`。

---

## 测试指南

使用 curl 或 Postman 按上述请求体进行验证。

---

## 错误处理

Webhook端点始终返回 200 状态码；具体成功或错误由响应体中的 `status` 字段决定。