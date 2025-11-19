# 字符集Collation问题修复总结

## 问题描述

项目repo层存在大量500错误,错误日志显示:

```
(asyncmy.errors.OperationalError) (1267, "Illegal mix of collations (utf8mb4_unicode_ci,IMPLICIT) and (utf8mb4_0900_ai_ci,IMPLICIT) for operation '='")
```

**根本原因**: 数据库中不同表的字段(如`account`和`user_id`)使用了不同的字符集排序规则(collation),当在SQL查询中跨表比较这些字段时,MySQL无法自动转换,导致报错。

### 具体场景

1. **account字段**: `agent_profiles`、`member_profiles`等表的account字段collation不一致
2. **user_id字段**: `users`表的id字段与`member_profiles`、`rebate_settings`等表的user_id字段collation不一致

## 修复方案

### 方案1: 在SQL查询中显式指定COLLATE (已实施)

在所有涉及跨表account字段比较的SQL查询中添加`COLLATE utf8mb4_unicode_ci`,确保比较时使用一致的排序规则。

**优点**:
- 不需要修改数据库结构
- 立即生效
- 不影响现有数据

**修改文件列表**:

1. **biz/users/repo/personal_repo.py**
   - `get_basic_info()` - 修复account查询
   - `update_basic_info()` - 修复account查询
   - `get_lottery_rebate_config()` - 修复account查询
   - `save_lottery_rebate_config()` - 修复account查询

2. **biz/users/repo/agent_repo.py**
   - `get_agent_detail()` - 修复account查询

3. **biz/users/repo/member_repo.py**
   - `get_member_detail()` - 修复account查询

4. **biz/users/repo/rebate_repo.py**
   - `get_rebate_settings()` - 修复account查询
   - `update_rebate_settings()` - 修复account查询

5. **biz/roles/repo/subaccount_repo.py**
   - `generate_account()` - 修复account查询
   - `get_parent_user_id_by_agent_account()` - 修复account查询

6. **biz/auth/api/auth_api.py**
   - `login()` - 修复代理和会员登录的account查询

7. **biz/user/repo/user_repo.py** (新增 2025-11-19)
   - `get_user_in_chat()` - 修复user_id JOIN查询

8. **biz/users/service/bot_user_service.py** (新增 2025-11-19)
   - `list_bot_users()` - 修复user_id JOIN查询

### 方案2: 统一数据库字段的Collation (可选,推荐执行)

创建了migration脚本 `migrations/003_fix_collation.sql`,将所有相关表的account字段统一修改为`utf8mb4_unicode_ci`。

**执行方式**:
```bash
# 方式1: 直接执行SQL
mysql -u your_user -p game_bot < migrations/003_fix_collation.sql

# 方式2: 使用Python脚本
python migrations/run_migration.py
```

**涉及表**:
- `agent_profiles` (account, superior_account, invite_code)
- `member_profiles` (account, superior_account)
- `login_logs` (account)
- `sub_accounts` (account)

## 修改详情

### 典型修改示例

#### 示例1: account字段修复

**修改前**:
```python
query = text("""
    SELECT u.id
    FROM users u
    LEFT JOIN agent_profiles ap ON u.id = ap.user_id
    LEFT JOIN member_profiles mp ON u.id = mp.user_id
    WHERE ap.account = :account OR mp.account = :account
    LIMIT 1
""")
```

**修改后**:
```python
query = text("""
    SELECT u.id
    FROM users u
    LEFT JOIN agent_profiles ap ON u.id = ap.user_id
    LEFT JOIN member_profiles mp ON u.id = mp.user_id
    WHERE ap.account COLLATE utf8mb4_unicode_ci = :account
       OR mp.account COLLATE utf8mb4_unicode_ci = :account
    LIMIT 1
""")
```

#### 示例2: user_id JOIN修复 (新增 2025-11-19)

**修改前**:
```python
query = text("""
    SELECT u.*, mp.plate
    FROM users u
    LEFT JOIN member_profiles mp ON mp.user_id = u.id
    LEFT JOIN rebate_settings rs ON rs.user_id = u.id
    WHERE u.id = :user_id AND u.chat_id = :chat_id
""")
```

**修改后**:
```python
query = text("""
    SELECT u.*, mp.plate
    FROM users u
    LEFT JOIN member_profiles mp ON mp.user_id COLLATE utf8mb4_unicode_ci = u.id COLLATE utf8mb4_unicode_ci
    LEFT JOIN rebate_settings rs ON rs.user_id COLLATE utf8mb4_unicode_ci = u.id COLLATE utf8mb4_unicode_ci
    WHERE u.id = :user_id AND u.chat_id = :chat_id
""")
```

## 测试建议

修复后应该测试以下接口:

1. **登录接口** - `/api/auth/login`
   - 代理登录
   - 会员登录

2. **个人中心接口** - `/api/personal/*`
   - 获取基本信息
   - 获取彩票退水配置
   - 获取登录日志

3. **用户管理接口**
   - 代理详情查询
   - 会员详情查询
   - 子账号管理

## 注意事项

1. **单表查询无需修改**: 只在同一个表内查询account的SQL不需要添加COLLATE
2. **JOIN查询需要修改**: 涉及多表JOIN并比较account字段的查询必须添加COLLATE
3. **建议执行方案2**: 虽然方案1已经解决了问题,但执行方案2可以永久解决,避免未来新增代码时忘记添加COLLATE

## 验证方法

执行以下SQL验证数据库字符集是否统一:

```sql
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    COLLATION_NAME
FROM
    information_schema.COLUMNS
WHERE
    TABLE_SCHEMA = 'game_bot'
    AND COLUMN_NAME LIKE '%account%'
ORDER BY
    TABLE_NAME, COLUMN_NAME;
```

所有account相关字段的`COLLATION_NAME`应该都是`utf8mb4_unicode_ci`。

## 修复时间

- **account字段修复**: 2025-11-18
- **user_id字段修复**: 2025-11-19

## 修复人员

Claude Code
