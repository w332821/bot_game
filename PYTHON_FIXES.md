# Python Bot 修复清单

## 已修复的问题

### 1. ChatRepository.get_by_id() 方法缺失
**文件**: `biz/chat/repo/chat_repo.py`
**问题**: webhook_api.py 调用 `chat_repo.get_by_id()` 但该方法不存在
**修复**: 添加 `get_by_id()` 别名方法指向 `get_chat()`

```python
async def get_by_id(self, chat_id: str) -> Optional[Dict[str, Any]]:
    """获取群聊信息（别名方法，兼容BaseRepository接口）"""
    return await self.get_chat(chat_id)
```

### 2. ChatRepository.create() 方法名错误
**文件**: `biz/game/webhook/webhook_api.py` (两处)
**问题**: 调用 `chat_repo.create()` 但实际方法名是 `create_chat()`
**修复**:
- 行 137: `chat_repo.create()` → `chat_repo.create_chat()`
- 行 258: `chat_repo.create()` → `chat_repo.create_chat()`

### 3. Bot API 认证方式不匹配
**文件**: `external/bot_api_client.py`
**问题**: Python 使用 `Authorization: Bearer` 和 `X-Bot-Secret`，但服务器要求：
- `X-API-Key`
- `X-Signature` (HMAC-SHA256)
- `X-Timestamp`

**修复**: 重写认证逻辑以匹配 Node.js 实现

```python
def _generate_signature(self, data: Dict[str, Any], timestamp: str) -> str:
    """生成API签名（与Node.js版本完全一致）"""
    sign_data = json.dumps(data, separators=(',', ':'), ensure_ascii=False) + timestamp
    signature = hmac.new(
        self.api_secret.encode('utf-8'),
        sign_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def _get_headers(self, data: Dict[str, Any]) -> Dict[str, str]:
    """获取请求头（与Node.js版本完全一致）"""
    timestamp = str(int(time.time() * 1000))
    signature = self._generate_signature(data, timestamp)

    return {
        'Content-Type': 'application/json',
        'X-API-Key': self.api_key,
        'X-Signature': signature,
        'X-Timestamp': timestamp
    }
```

## 关键差异说明

### 数据存储
- **Node.js**: 内存 Map + JSON 文件持久化
- **Python**: MySQL 数据库 + SQLAlchemy

### Sender ID 字段
- Webhook 数据中使用 `id`（不是 `_id`）
- Python 代码已正确处理：`sender.get('_id') or sender.get('id')`

### 消息数据结构
两个版本都正确地从以下位置获取数据：
- `data.message.chat` - 群聊信息
- `data.message.sender` - 发送者信息
- `data.message.content` - 消息内容

## 部署步骤

1. **同步修复的文件到服务器**:
```bash
# 复制修复后的文件
scp biz/chat/repo/chat_repo.py root@server:/root/bot_game/biz/chat/repo/
scp biz/game/webhook/webhook_api.py root@server:/root/bot_game/biz/game/webhook/
scp external/bot_api_client.py root@server:/root/bot_game/external/
```

2. **在服务器上重启服务**:
```bash
pm2 restart game-bot-python
pm2 logs game-bot-python --lines 50
```

3. **测试功能**:
- 创建新群聊
- 发送消息触发下注
- 验证 Bot API 认证成功

## 待验证项目

- [ ] Bot API 认证成功（无 401 错误）
- [ ] 群聊创建成功
- [ ] 消息处理正常
- [ ] 下注功能正常
- [ ] 余额查询正常
- [ ] 自动开奖正常
