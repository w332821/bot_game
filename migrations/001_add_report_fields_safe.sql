-- ============================================
-- 报表模块字段补充迁移脚本（安全版本 - 可重复执行）
-- 执行方式：mysql -u root -p game_bot < migrations/001_add_report_fields_safe.sql
-- ============================================

-- 设置数据库
USE game_bot;

-- ============================================
-- 1. bet_orders 表添加字段
-- ============================================

-- 添加 valid_amount 列（如果不存在）
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'bet_orders'
  AND COLUMN_NAME = 'valid_amount';

SET @sql = IF(@col_exists = 0,
  'ALTER TABLE bet_orders ADD COLUMN valid_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT ''有效金额'' AFTER bet_amount',
  'SELECT ''✓ Column valid_amount already exists in bet_orders'' AS Info');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 gameplay 列（如果不存在）
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'bet_orders'
  AND COLUMN_NAME = 'gameplay';

SET @sql = IF(@col_exists = 0,
  'ALTER TABLE bet_orders ADD COLUMN gameplay VARCHAR(100) NULL DEFAULT NULL COMMENT ''玩法名称'' AFTER status',
  'SELECT ''✓ Column gameplay already exists in bet_orders'' AS Info');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 更新现有数据的 valid_amount
UPDATE bet_orders SET valid_amount = bet_amount WHERE valid_amount = 0.00;

-- ============================================
-- 2. member_profiles 表添加字段
-- ============================================

-- 添加 name 列（如果不存在）
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'member_profiles'
  AND COLUMN_NAME = 'name';

SET @sql = IF(@col_exists = 0,
  'ALTER TABLE member_profiles ADD COLUMN name VARCHAR(100) NULL DEFAULT NULL COMMENT ''会员姓名'' AFTER account',
  'SELECT ''✓ Column name already exists in member_profiles'' AS Info');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 level 列（如果不存在）
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'member_profiles'
  AND COLUMN_NAME = 'level';

SET @sql = IF(@col_exists = 0,
  'ALTER TABLE member_profiles ADD COLUMN level INT NOT NULL DEFAULT 1 COMMENT ''会员级别'' AFTER name',
  'SELECT ''✓ Column level already exists in member_profiles'' AS Info');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 创建索引（如果不存在）
SET @index_exists = 0;
SELECT COUNT(*) INTO @index_exists
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'member_profiles'
  AND INDEX_NAME = 'idx_member_level';

SET @sql = IF(@index_exists = 0,
  'CREATE INDEX idx_member_level ON member_profiles(level)',
  'SELECT ''✓ Index idx_member_level already exists'' AS Info');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 更新现有数据的 name
UPDATE member_profiles SET name = account WHERE name IS NULL;

-- ============================================
-- 3. agent_profiles 表添加字段
-- ============================================

-- 添加 name 列（如果不存在）
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'agent_profiles'
  AND COLUMN_NAME = 'name';

SET @sql = IF(@col_exists = 0,
  'ALTER TABLE agent_profiles ADD COLUMN name VARCHAR(100) NULL DEFAULT NULL COMMENT ''代理姓名'' AFTER account',
  'SELECT ''✓ Column name already exists in agent_profiles'' AS Info');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 level 列（如果不存在）
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'agent_profiles'
  AND COLUMN_NAME = 'level';

SET @sql = IF(@col_exists = 0,
  'ALTER TABLE agent_profiles ADD COLUMN level INT NOT NULL DEFAULT 1 COMMENT ''代理级别'' AFTER name',
  'SELECT ''✓ Column level already exists in agent_profiles'' AS Info');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 创建索引（如果不存在）
SET @index_exists = 0;
SELECT COUNT(*) INTO @index_exists
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'agent_profiles'
  AND INDEX_NAME = 'idx_agent_level';

SET @sql = IF(@index_exists = 0,
  'CREATE INDEX idx_agent_level ON agent_profiles(level)',
  'SELECT ''✓ Index idx_agent_level already exists'' AS Info');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 更新现有数据的 name
UPDATE agent_profiles SET name = account WHERE name IS NULL;

-- ============================================
-- 4. 创建代理结算配置表
-- ============================================

CREATE TABLE IF NOT EXISTS agent_settlement_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_user_id VARCHAR(255) NOT NULL UNIQUE COMMENT '代理用户ID',
    share_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '占成比例 0-100',
    earn_rebate_mode VARCHAR(20) NOT NULL DEFAULT 'none' COMMENT '赚水模式: full/partial/none',
    can_collect_downline BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否可以收取下线盈利',
    settlement_cycle VARCHAR(20) NOT NULL DEFAULT 'daily' COMMENT '结算周期',
    remarks TEXT NULL COMMENT '备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_agent_user_id (agent_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='代理结算配置表';

-- 为现有代理创建默认配置（使用 INSERT IGNORE 避免重复）
INSERT IGNORE INTO agent_settlement_config (agent_user_id, share_percentage, earn_rebate_mode)
SELECT user_id, 0.00, 'none' FROM agent_profiles;

-- ============================================
-- 迁移完成验证
-- ============================================
SELECT '✅ 数据库迁移完成！' AS status;
SELECT 'bet_orders表字段' AS check_item, COUNT(*) AS affected_rows FROM bet_orders WHERE valid_amount >= 0;
SELECT 'member_profiles表字段' AS check_item, COUNT(*) AS affected_rows FROM member_profiles WHERE name IS NOT NULL;
SELECT 'agent_profiles表字段' AS check_item, COUNT(*) AS affected_rows FROM agent_profiles WHERE name IS NOT NULL;
SELECT 'agent_settlement_config表' AS check_item, COUNT(*) AS affected_rows FROM agent_settlement_config;
