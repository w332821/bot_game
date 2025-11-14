# 测试文档

## 📋 测试概览

本项目使用 **pytest** 作为测试框架，提供完整的单元测试和集成测试覆盖。

### 测试结构

```
tests/
├── conftest.py                    # pytest全局配置和fixtures
├── unit/                          # 单元测试
│   ├── test_user_repository.py    # UserRepository测试
│   └── test_game_service.py       # GameService测试 (新增)
└── integration/                   # 集成测试
    └── test_webhook_api.py        # Webhook API测试 (新增)
```

---

## 🚀 快速开始

### 1. 安装测试依赖

```bash
# 使用bot_game环境
/opt/anaconda3/envs/bot_game/bin/pip install -r requirements-test.txt
```

### 2. 运行测试

**使用测试脚本（推荐）**:
```bash
./run_tests.sh
```

**直接使用pytest**:
```bash
# 运行所有测试
/opt/anaconda3/envs/bot_game/bin/python -m pytest tests/ -v

# 运行单元测试
/opt/anaconda3/envs/bot_game/bin/python -m pytest tests/unit/ -v

# 运行集成测试
/opt/anaconda3/envs/bot_game/bin/python -m pytest tests/integration/ -v

# 运行特定文件
/opt/anaconda3/envs/bot_game/bin/python -m pytest tests/unit/test_game_service.py -v

# 带覆盖率报告
/opt/anaconda3/envs/bot_game/bin/python -m pytest tests/ --cov=biz/game --cov-report=html
```

---

## 📦 测试依赖

| 包 | 版本 | 用途 |
|------|------|------|
| pytest | 7.4.3 | 测试框架 |
| pytest-asyncio | 0.21.1 | 异步测试支持 |
| pytest-cov | 4.1.0 | 代码覆盖率 |
| pytest-mock | 3.12.0 | Mock工具 |
| aioresponses | 0.7.6 | HTTP Mock |
| faker | 20.1.0 | 测试数据生成 |
| freezegun | 1.4.0 | 时间Mock |

---

## 🧪 单元测试

### GameService测试 (`test_game_service.py`)

测试GameService的核心业务逻辑，包括：

#### 1. 下注指令解析测试
```python
class TestBetParsing:
    - test_parse_lucky8_fan_bet()      # 澳洲幸运8番下注
    - test_parse_lucky8_zheng_bet()    # 澳洲幸运8正下注
    - test_parse_lucky8_dan_shuang()   # 澳洲幸运8单双
    - test_parse_liuhecai_number_bet() # 六合彩号码
    - test_parse_liuhecai_bose_bet()   # 六合彩波色
```

**测试的格式**:
- `"番 3/200"` - 3番下注200
- `"3番200"` - 简写格式
- `"正1/200"` - 正1下注200
- `"单200"` - 单下注200
- `"红波200"` - 红波下注200

#### 2. 余额查询测试
```python
class TestHandleQueryBalance:
    - test_query_balance_success()      # 成功查询
    - test_query_balance_user_not_found() # 用户不存在
```

#### 3. 下注处理测试
```python
class TestHandleBetMessage:
    - test_bet_success()                # 成功下注
    - test_bet_insufficient_balance()   # 余额不足
```

**测试场景**:
- ✅ 验证余额扣除
- ✅ 验证下注记录创建
- ✅ 验证确认消息发送
- ✅ 验证余额不足处理

#### 4. 取消下注测试
```python
class TestHandleCancelBet:
    - test_cancel_bet_success()         # 成功取消
    - test_cancel_bet_no_pending()      # 无待取消下注
```

#### 5. 开奖结算测试
```python
class TestExecuteDraw:
    - test_execute_draw_success()       # 成功开奖
```

**测试流程**:
- ✅ 获取开奖结果
- ✅ 结算所有pending下注
- ✅ 更新用户余额
- ✅ 发送开奖公告

#### 6. 排行榜测试
```python
class TestHandleLeaderboard:
    - test_leaderboard_display()        # 排行榜展示
```

#### 7. 期号生成测试
```python
class TestIssueNumberGeneration:
    - test_generate_lucky8_issue()      # 澳洲幸运8期号
    - test_generate_lucky8_first_issue() # 第一期
    - test_generate_liuhecai_issue()    # 六合彩期号
```

**期号格式**:
- 澳洲幸运8: `YYYYMMDD` + 三位序号 (例: `20250113001`)
- 六合彩: `YYYYMMDD` (例: `20250113`)

### 运行单元测试

```bash
# 运行GameService测试
/opt/anaconda3/envs/bot_game/bin/python -m pytest tests/unit/test_game_service.py -v

# 运行特定测试类
/opt/anaconda3/envs/bot_game/bin/python -m pytest tests/unit/test_game_service.py::TestBetParsing -v

# 运行特定测试函数
/opt/anaconda3/envs/bot_game/bin/python -m pytest \
  tests/unit/test_game_service.py::TestBetParsing::test_parse_lucky8_fan_bet -v
```

---

## 🔗 集成测试

### Webhook API测试 (`test_webhook_api.py`)

测试Webhook端点的完整请求-响应流程。

#### 1. 群聊创建测试
```python
class TestWebhookGroupCreated:
    - test_group_created_success()      # 成功处理
    - test_group_created_missing_data() # 缺少数据
```

**测试请求**:
```json
{
  "event": "group.created",
  "data": {
    "chat": {
      "id": "test_chat_001",
      "name": "测试群聊",
      "type": "group"
    }
  }
}
```

**预期响应**:
```json
{"status": "ok"}
```

#### 2. 成员加入测试
```python
class TestWebhookMemberJoined:
    - test_member_joined_success()      # 成功处理
```

#### 3. 消息接收测试
```python
class TestWebhookMessageReceived:
    - test_message_query_balance()      # 查询余额消息
    - test_message_bet()                # 下注消息
    - test_message_from_bot_ignored()   # 忽略机器人消息
```

**测试场景**:
- ✅ 处理"查"指令
- ✅ 处理"番 3/200"下注
- ✅ 忽略机器人消息

#### 4. 游戏类型同步测试
```python
class TestSyncGameType:
    - test_sync_gametype_success()      # 成功同步
    - test_sync_gametype_missing_fields() # 缺少字段
```

**测试请求**:
```json
{
  "chatId": "chat_001",
  "gameType": "liuhecai",
  "oldGameType": "lucky8"
}
```

#### 5. 健康检查测试
```python
class TestHealthCheck:
    - test_health_check()               # 健康检查
```

### 运行集成测试

```bash
# 运行所有集成测试
/opt/anaconda3/envs/bot_game/bin/python -m pytest tests/integration/ -v

# 运行Webhook测试
/opt/anaconda3/envs/bot_game/bin/python -m pytest tests/integration/test_webhook_api.py -v

# 运行特定测试类
/opt/anaconda3/envs/bot_game/bin/python -m pytest \
  tests/integration/test_webhook_api.py::TestWebhookGroupCreated -v
```

---

## 📊 代码覆盖率

### 生成覆盖率报告

```bash
# HTML报告（推荐）
/opt/anaconda3/envs/bot_game/bin/python -m pytest tests/ \
  --cov=biz/game \
  --cov=external \
  --cov=utils \
  --cov-report=html \
  --cov-report=term-missing

# 查看HTML报告
open htmlcov/index.html
```

### 覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|---------|
| GameService | 80%+ | ⏳ 待测试 |
| Webhook API | 70%+ | ⏳ 待测试 |
| DrawScheduler | 60%+ | ⚠️ 未测试 |
| 图片生成器 | 50%+ | ⚠️ 未测试 |
| Bot API客户端 | 60%+ | ⚠️ 未测试 |

---

## 🧰 Fixtures说明

### 全局Fixtures (`conftest.py`)

#### 数据库Fixtures
```python
@pytest.fixture(scope="session")
async def db_engine():
    """测试数据库引擎"""
    # 创建测试数据库: game_bot_test
    pass

@pytest.fixture(scope="function")
async def db_session(db_engine):
    """测试数据库会话"""
    # 每个测试函数独立会话
    pass

@pytest.fixture(scope="function")
async def session_factory(db_engine):
    """Session工厂"""
    pass
```

#### 测试数据Fixtures
```python
@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "id": "test_user_001",
        "username": "测试用户",
        "balance": Decimal("1000.00"),
        ...
    }

@pytest.fixture
def sample_bet_data():
    """示例投注数据"""
    pass

@pytest.fixture
def sample_chat_data():
    """示例群聊数据"""
    pass
```

### 测试专用Fixtures

在测试文件中定义：

```python
@pytest.fixture
def mock_repos():
    """Mock repositories"""
    return {
        'user_repo': AsyncMock(),
        'bet_repo': AsyncMock(),
        ...
    }

@pytest.fixture
def mock_bot_client():
    """Mock Bot API客户端"""
    client = AsyncMock()
    client.send_message = AsyncMock()
    return client

@pytest.fixture
def game_service(mock_repos, mock_bot_client):
    """创建GameService实例"""
    return GameService(...)
```

---

## 🎯 编写测试的最佳实践

### 1. 测试命名规范
```python
# 好的命名
def test_parse_lucky8_fan_bet():
    """测试澳洲幸运8番下注解析"""
    pass

# 不好的命名
def test1():
    pass
```

### 2. 使用AAA模式
```python
def test_bet_success():
    # Arrange - 准备
    mock_repo.get_by_id.return_value = {...}

    # Act - 执行
    result = await service.handle_bet(...)

    # Assert - 断言
    assert result == expected
    mock_repo.create.assert_called_once()
```

### 3. 一个测试一个断言焦点
```python
# 好的做法
def test_bet_creates_record():
    """测试下注创建记录"""
    await service.handle_bet(...)
    mock_repo.create.assert_called_once()

def test_bet_deducts_balance():
    """测试下注扣除余额"""
    await service.handle_bet(...)
    mock_repo.update_balance.assert_called_with('user_001', Decimal('-200'))

# 避免
def test_bet():  # 太宽泛
    # 测试太多东西
    pass
```

### 4. 使用Mock隔离依赖
```python
# 好的做法
@pytest.fixture
def game_service(mock_repos):
    return GameService(
        user_repo=mock_repos['user_repo'],  # Mock
        bet_repo=mock_repos['bet_repo'],    # Mock
        ...
    )

# 避免
def test_with_real_db():
    # 不要在单元测试中使用真实数据库
    pass
```

### 5. 测试边界条件
```python
def test_bet_minimum_amount():
    """测试最小下注金额"""
    pass

def test_bet_maximum_amount():
    """测试最大下注金额"""
    pass

def test_bet_zero_amount():
    """测试零金额下注"""
    pass

def test_bet_negative_amount():
    """测试负数下注"""
    pass
```

---

## 🐛 调试测试

### 1. 运行特定测试并打印输出
```bash
/opt/anaconda3/envs/bot_game/bin/python -m pytest \
  tests/unit/test_game_service.py::test_parse_lucky8_fan_bet \
  -v -s  # -s 显示print输出
```

### 2. 进入调试器
```python
def test_something():
    result = some_function()

    # 进入调试器
    import pdb; pdb.set_trace()

    assert result == expected
```

### 3. 只运行失败的测试
```bash
/opt/anaconda3/envs/bot_game/bin/python -m pytest --lf  # last-failed
```

### 4. 查看详细错误信息
```bash
/opt/anaconda3/envs/bot_game/bin/python -m pytest -vv --tb=long
```

---

## 📝 CI/CD集成

### GitHub Actions示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt

      - name: Run tests
        run: |
          pytest tests/ --cov=biz/game --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

---

## ✅ 测试清单

### App端测试状态

- [x] GameService单元测试
  - [x] 下注指令解析
  - [x] 余额查询
  - [x] 下注处理
  - [x] 取消下注
  - [x] 开奖结算
  - [x] 排行榜
  - [x] 期号生成

- [x] Webhook API集成测试
  - [x] 群聊创建事件
  - [x] 成员加入事件
  - [x] 消息接收事件
  - [x] 游戏类型同步
  - [x] 健康检查

- [ ] DrawScheduler测试 (待补充)
  - [ ] 启动定时器
  - [ ] 停止定时器
  - [ ] 重启定时器
  - [ ] 定时开奖触发

- [ ] 图片生成器测试 (待补充)
  - [ ] 澳洲幸运8图片生成
  - [ ] 六合彩图片生成
  - [ ] 错误处理

- [ ] Bot API客户端测试 (待补充)
  - [ ] 发送消息
  - [ ] 发送图片
  - [ ] 认证失败处理

---

## 📚 参考资料

- [pytest官方文档](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI测试](https://fastapi.tiangolo.com/tutorial/testing/)

---

## 🎯 下一步

1. **补充DrawScheduler测试** - 测试定时器管理逻辑
2. **补充图片生成器测试** - 测试PIL图片生成
3. **提高覆盖率** - 目标80%+
4. **性能测试** - 使用locust进行压力测试
5. **端到端测试** - 完整用户流程测试

---

**最后更新**: 2025-11-13
**维护者**: Development Team
