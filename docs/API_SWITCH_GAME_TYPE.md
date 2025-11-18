# 群聊游戏类型切换API

## 📌 接口说明

**功能：** 切换指定群聊的游戏类型（澳洲幸运8 ↔ 六合彩）

**接口地址：** `POST /api/chat/{chatId}/gametype`

---

## 📤 请求

### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| chatId | string | 是 | 群聊ID |

### 请求体

| 参数名 | 类型 | 必填 | 可选值 | 说明 |
|--------|------|------|--------|------|
| gameType | string | 是 | `lucky8` 或 `liuhecai` | 游戏类型 |

### 请求示例

```json
{
  "gameType": "liuhecai"
}
```

---

## 📥 响应

### 成功响应

```json
{
  "success": true,
  "chat": {
    "id": "123456",
    "name": "测试群聊",
    "game_type": "liuhecai",
    "status": "active",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
}
```

### 失败响应

```json
{
  "success": false,
  "error": "群聊不存在"
}
```

或

```json
{
  "success": false,
  "error": "游戏类型必须是lucky8或liuhecai"
}
```

---

## 💻 代码示例

### 使用 axios

```javascript
// 切换到六合彩
async function switchToLiuhecai(chatId) {
  try {
    const response = await axios.post(
      `/api/chat/${chatId}/gametype`,
      { gameType: 'liuhecai' }
    );

    if (response.data.success) {
      console.log('切换成功！', response.data.chat);
      // 更新UI或显示成功提示
    } else {
      console.error('切换失败：', response.data.error);
    }
  } catch (error) {
    console.error('请求失败：', error);
  }
}

// 切换到澳洲幸运8
async function switchToLucky8(chatId) {
  try {
    const response = await axios.post(
      `/api/chat/${chatId}/gametype`,
      { gameType: 'lucky8' }
    );

    if (response.data.success) {
      console.log('切换成功！', response.data.chat);
    }
  } catch (error) {
    console.error('请求失败：', error);
  }
}
```

### 使用 fetch

```javascript
async function switchGameType(chatId, gameType) {
  try {
    const response = await fetch(`/api/chat/${chatId}/gametype`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ gameType })
    });

    const data = await response.json();

    if (data.success) {
      console.log('切换成功！', data.chat);
      return data.chat;
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('切换失败：', error.message);
    throw error;
  }
}

// 使用示例
switchGameType('123456', 'liuhecai');  // 切换到六合彩
switchGameType('123456', 'lucky8');     // 切换到澳洲幸运8
```

---

## ✨ 自动切换效果

调用此接口后，系统会**自动**完成以下操作：

1. ✅ **更新数据库** - 群聊的 `game_type` 字段立即更新
2. ✅ **切换定时器** - 自动从旧游戏类型迁移到新游戏类型
3. ✅ **调整开奖间隔**
   - `lucky8`：5分钟一次
   - `liuhecai`：24小时一次
4. ✅ **切换机器人话术** - 欢迎消息、倒计时提示、开奖消息都会使用新游戏类型的文案
5. ✅ **切换游戏规则** - 下注玩法、赔率等自动切换
6. ✅ **无需重启** - 切换立即生效，无需重启应用

---

## ⚠️ 注意事项

1. **无需额外操作** - 调用接口后，所有相关功能会自动切换，无需手动干预
2. **立即生效** - 切换后立即生效，下一次开奖就会使用新的游戏类型
3. **游戏类型值** - 只支持 `lucky8`（澳洲幸运8）和 `liuhecai`（六合彩）两个值

---

## 🎮 游戏类型对照表

| gameType 值 | 游戏名称 | 开奖间隔 | 主要玩法 |
|-------------|----------|----------|----------|
| `lucky8` | 澳洲幸运8 | 5分钟 | 番、正、念、角、通 |
| `liuhecai` | 六合彩 | 24小时 | 特码 |
