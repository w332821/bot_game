# 数据库结构修复：添加 bet_details 字段

## ✅ 已完成的修复

### 1. 更新数据库模型定义
**文件**: `biz/bet/models/db_model.py`

添加了 `bet_details` 字段：
```python
bet_details: Optional[str] = Field(
    None,
    description="投注详情JSON（包含完整的下注信息）",
    sa_column_kwargs={"type_": Text}
)
```

### 2. 更新备份 SQL 文件
**文件**: `game_bot_backup.sql`

在 `bets` 表定义中添加：
```sql
`bet_details` text COLLATE utf8mb4_unicode_ci DEFAULT NULL
COMMENT '投注详情JSON（包含完整的下注信息）',
```

### 3. 创建迁移脚本
**文件**: `migrations/add_bet_details_column.sql`

智能迁移脚本，特点：
- ✅ 自动检查字段是否已存在
- ✅ 如果已存在则跳过，不会报错
- ✅ 自动验证迁移结果

## 🚀 使用方法

### 方式 1：重新初始化数据库（推荐用于开发环境）

如果可以清空数据，最简单的方式：

```bash
# 1. 删除旧表（会丢失数据！）
python -c "from base.init_db import drop_all_tables; drop_all_tables()"

# 2. 重新创建所有表（包含新字段）
python -m base.init_db
```

### 方式 2：执行迁移脚本（推荐用于生产环境）

在服务器上执行：

```bash
# 连接到 MySQL
mysql -u root -p game_bot < migrations/add_bet_details_column.sql
```

或者直接在 MySQL 命令行中：

```sql
USE game_bot;

ALTER TABLE `bets`
ADD COLUMN `bet_details` TEXT COLLATE utf8mb4_unicode_ci DEFAULT NULL
COMMENT '投注详情JSON（包含完整的下注信息）'
AFTER `issue`;
```

### 方式 3：使用 Python 迁移脚本

```bash
cd /root/bot_game/bot_game
python migrations/run_migration.py
```

## 📋 验证

执行后验证字段是否添加成功：

```sql
SHOW COLUMNS FROM bets LIKE 'bet_details';

-- 或者查看完整表结构
DESCRIBE bets;
```

预期输出：
```
Field        | Type | Null | Key | Default | Extra
bet_details  | text | YES  |     | NULL    |
```

## 🎯 字段用途

`bet_details` 字段存储完整的投注详情 JSON，包含：

```json
{
    "type": "fan",
    "number": 2,
    "amount": 300.0,
    "odds": 3.0,
    "player": "643464",
    "raw": "2番300"
}
```

用途：
- ✅ 完整记录投注信息，便于审计
- ✅ 支持投注争议处理
- ✅ 方便后期数据分析
- ✅ 保留原始输入，可重现投注场景

## 🔄 下次初始化不会再有问题

因为已经更新了：
1. ✅ **数据库模型定义** (`db_model.py`) - SQLModel 会自动创建表
2. ✅ **备份 SQL 文件** (`game_bot_backup.sql`) - 手动创建表时包含此字段
3. ✅ **迁移脚本** - 支持现有数据库升级

无论使用哪种方式初始化数据库，都会包含 `bet_details` 字段！

## 📝 相关代码

使用 `bet_details` 的地方：

**保存投注时** (`biz/bet/repo/bet_repo.py:343`):
```python
"bet_details": safe_json_dumps(bet_data.get("bet_details"))
    if bet_data.get("bet_details") else None
```

**调用示例** (`biz/game/service/game_service.py:157`):
```python
bet_record = await self.bet_repo.create({
    'user_id': sender_id,
    'chat_id': chat_id,
    'game_type': game_type,
    'bet_type': bet['type'],
    'amount': bet['amount'],
    'odds': bet['odds'],
    'status': 'pending',
    'draw_issue': current_issue,
    'bet_details': bet  # 完整的下注详情
})
```

## ⚠️ 注意事项

1. **生产环境**：建议在低峰期执行迁移
2. **备份数据**：执行前先备份数据库
3. **测试验证**：迁移后测试投注功能是否正常

## 🎉 总结

现在：
- ✅ 数据库模型已更新
- ✅ SQL 备份文件已更新
- ✅ 迁移脚本已准备好
- ✅ 下次初始化数据库不会再缺少字段
- ✅ 现有数据库可以安全升级

执行迁移后，应用即可正常运行！
