# 数据库迁移脚本说明

## 迁移文件

### 001_add_report_fields_safe.sql ✅ 推荐使用

**安全版本** - 可以重复执行，不会因为字段已存在而报错

**特点：**
- ✅ 自动检查字段是否存在
- ✅ 只添加不存在的字段
- ✅ 可以安全地重复执行
- ✅ 使用 `INSERT IGNORE` 避免重复数据

**执行命令：**
```bash
mysql -u root -p game_bot < migrations/001_add_report_fields_safe.sql
```

**包含的变更：**
1. `bet_orders` 表
   - 添加 `valid_amount` 字段（有效金额）
   - 添加 `gameplay` 字段（玩法名称）

2. `member_profiles` 表
   - 添加 `name` 字段（会员姓名）
   - 添加 `level` 字段（会员级别）
   - 创建 `idx_member_level` 索引

3. `agent_profiles` 表
   - 添加 `name` 字段（代理姓名）
   - 添加 `level` 字段（代理级别）
   - 创建 `idx_agent_level` 索引

4. 创建 `agent_settlement_config` 表（代理结算配置）

---

### 001_add_report_fields.sql ⚠️ 原始版本

**原始版本** - 不建议使用（会因重复字段报错）

如果需要使用原始版本，请确保：
- 数据库是全新的
- 这些字段都不存在
- 只执行一次

---

## 执行步骤

### 方法 1: 命令行执行（推荐）

```bash
# 进入项目目录
cd /Users/demean5/Desktop/bot_game

# 执行迁移脚本（会提示输入密码）
mysql -u root -p game_bot < migrations/001_add_report_fields_safe.sql
```

### 方法 2: MySQL 客户端执行

```bash
# 登录 MySQL
mysql -u root -p game_bot

# 在 MySQL 客户端中执行
source migrations/001_add_report_fields_safe.sql;
```

---

## 验证迁移结果

执行完成后，脚本会自动显示验证信息：

```
✅ 数据库迁移完成！
- bet_orders表字段: X 条记录
- member_profiles表字段: X 条记录
- agent_profiles表字段: X 条记录
- agent_settlement_config表: X 条记录
```

---

## 回滚说明

如果需要回滚迁移，请手动执行：

```sql
-- 删除 bet_orders 新增字段
ALTER TABLE bet_orders DROP COLUMN valid_amount;
ALTER TABLE bet_orders DROP COLUMN gameplay;

-- 删除 member_profiles 新增字段和索引
DROP INDEX idx_member_level ON member_profiles;
ALTER TABLE member_profiles DROP COLUMN level;
ALTER TABLE member_profiles DROP COLUMN name;

-- 删除 agent_profiles 新增字段和索引
DROP INDEX idx_agent_level ON agent_profiles;
ALTER TABLE agent_profiles DROP COLUMN level;
ALTER TABLE agent_profiles DROP COLUMN name;

-- 删除代理结算配置表
DROP TABLE agent_settlement_config;
```

---

## 故障排查

### 错误: Duplicate column name

**原因：** 使用了原始版本的脚本，字段已存在

**解决：** 使用安全版本 `001_add_report_fields_safe.sql`

### 错误: Access denied

**原因：** MySQL 用户没有权限

**解决：** 使用有足够权限的用户（如 root）

### 错误: Unknown database

**原因：** 数据库 `game_bot` 不存在

**解决：** 先创建数据库或检查数据库名称

---

## 注意事项

1. **备份数据库**：执行迁移前建议备份数据库
   ```bash
   mysqldump -u root -p game_bot > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **检查应用状态**：如果应用正在运行，建议先停止应用再执行迁移

3. **测试环境优先**：建议先在测试环境验证迁移脚本

---

**最后更新**: 2025-11-18
