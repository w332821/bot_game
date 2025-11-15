# 测试脚本修复总结

## 问题诊断

pytest测试脚本一直报错，经过排查发现两个主要问题：

### 1. **langsmith与pydantic v2依赖冲突**

**错误信息**:
```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

**原因**:
- 系统中安装了`langsmith 0.4.4`包
- langsmith依赖`pydantic v1` API
- 项目使用`pydantic v2.5.0`
- 导致pytest加载langsmith插件时崩溃

**解决方案**:
```bash
pip uninstall -y langsmith
```

### 2. **测试数据库未初始化**

**错误信息**:
```
asyncmy.errors.ProgrammingError: (1146, "Table 'game_bot_test.users' doesn't exist")
```

**原因**:
- pytest运行时找不到测试数据库表
- conftest.py中的fixture只创建数据库，但不创建表

**解决方案**:
创建专用的测试数据库初始化脚本 `init_test_db.py`

### 3. **pytest fixture scope不匹配**

**错误信息**:
```
ScopeMismatch: You tried to access the function scoped fixture event_loop with a session scoped request object
```

**原因**:
- `db_engine` fixture使用了`scope="session"`
- 与pytest-asyncio的`event_loop` fixture（`scope="function"`）冲突

**解决方案**:
将`db_engine` fixture改为`scope="function"`

## 修复的文件

1. **pytest.ini** - 简化配置，移除--cov参数（需要单独指定）
2. **tests/conftest.py** - 修改`db_engine` fixture从session scope改为function scope
3. **init_test_db.py** (新建) - 测试数据库初始化脚本
4. **run_tests.sh** (新建) - 交互式测试运行脚本
5. **setup_and_run_tests.py** (新建) - 自动化测试环境设置脚本

## 如何使用

### 首次设置

```bash
# 方法1: 使用自动化脚本（推荐）
python setup_and_run_tests.py

# 方法2: 手动设置
pip uninstall -y langsmith
python init_test_db.py
```

### 运行测试

```bash
# 全部测试
python -m pytest tests/ -v

# 单元测试
python -m pytest tests/unit/ -v

# 集成测试
python -m pytest tests/integration/ -v

# 单个文件
python -m pytest tests/unit/test_user_repository.py -v

# 带覆盖率报告
python -m pytest tests/ -v --cov=biz --cov-report=html

# 交互式菜单
./run_tests.sh
```

## 测试结果

```
============================= test session starts ==============================
platform darwin -- Python 3.12.7, pytest-7.4.3, pluggy-1.6.0
rootdir: /Users/demean5/Desktop/bot_game
configfile: pytest.ini
plugins: Faker-20.1.0, cov-4.1.0, asyncio-0.21.1, mock-3.12.0, anyio-3.7.1

tests/unit/test_user_repository.py::TestUserRepository::test_create_and_get_user PASSED
tests/unit/test_user_repository.py::TestUserRepository::test_add_balance PASSED
tests/unit/test_user_repository.py::TestUserRepository::test_subtract_balance PASSED
tests/unit/test_user_repository.py::TestUserRepository::test_subtract_balance_insufficient PASSED
tests/unit/test_user_repository.py::TestUserRepository::test_update_rebate_ratio PASSED
tests/unit/test_user_repository.py::TestUserRepository::test_user_exists PASSED

============================== 6 passed in 2.13s
```

✅ **所有测试通过！**

## 相关修改

- `pytest.ini:20` - 添加`-p no:langsmith`禁用冲突插件（但实际需要卸载langsmith）
- `tests/conftest.py:18` - 修改fixture scope
- 创建`init_test_db.py` - 独立的测试数据库初始化工具
