# 数据库迁移：添加 bet_details 字段

## 问题

应用程序尝试向 `bets` 表插入数据时报错：
```
Unknown column 'bet_details' in 'field list'
```

## 解决方案

需要在数据库的 `bets` 表中添加 `bet_details` 字段。

## 执行步骤

### 方法 1：直接执行 SQL（推荐）

登录到你的 MySQL 数据库，执行以下 SQL：

```sql
USE game_bot;

-- 添加 bet_details 字段
ALTER TABLE `bets`
ADD COLUMN `bet_details` TEXT COLLATE utf8mb4_unicode_ci DEFAULT NULL
COMMENT '投注详情JSON（包含完整的下注信息）'
AFTER `issue`;

-- 验证字段是否添加成功
SHOW COLUMNS FROM `bets` LIKE 'bet_details';
```

### 方法 2：使用 Python 脚本

在服务器上执行：

```bash
cd /root/bot_game/bot_game
python migrations/run_migration.py
```

### 方法 3：使用 MySQL 命令行

```bash
# 连接到数据库
mysql -u your_username -p game_bot

# 执行 SQL 文件
source migrations/add_bet_details_column.sql

# 或者直接执行命令
mysql -u your_username -p game_bot < migrations/add_bet_details_column.sql
```

## 验证

执行完毕后，验证字段是否添加成功：

```sql
DESCRIBE bets;
```

应该能看到 `bet_details` 字段，类型为 `text`。

## 回滚（如果需要）

如果需要撤销此更改：

```sql
ALTER TABLE `bets` DROP COLUMN `bet_details`;
```

## 注意事项

1. **备份数据库**：执行任何迁移前建议先备份数据库
2. **停机时间**：这个操作通常很快，但在大表上可能需要锁表
3. **已有数据**：此字段添加为 NULL，不会影响已有数据

## 为什么需要这个字段？

`bet_details` 字段用于存储完整的投注详情 JSON 数据，包括：
- 投注类型
- 投注号码
- 投注金额
- 赔率
- 原始输入
- 等等

这样可以在需要时完整恢复投注的所有信息，用于审计、争议解决等场景。

## 故障排查

### 如果字段已存在

```sql
-- 检查字段是否已存在
SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'game_bot'
AND TABLE_NAME = 'bets'
AND COLUMN_NAME = 'bet_details';
```

如果返回结果，说明字段已存在，无需再次添加。

### 如果遇到权限问题

确保你的 MySQL 用户有 ALTER 权限：

```sql
GRANT ALTER ON game_bot.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
```
