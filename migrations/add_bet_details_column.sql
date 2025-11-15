-- ============================================================
-- 数据库迁移：添加 bet_details 字段到 bets 表
-- ============================================================
-- 用途：存储完整的投注详情 JSON 数据
-- 日期：2025-11-15
-- 说明：如果字段已存在则跳过，不会报错
-- ============================================================

USE game_bot;

-- 检查并添加 bet_details 字段（如果不存在）
SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'bets'
    AND COLUMN_NAME = 'bet_details'
);

-- 只有当字段不存在时才添加
SET @sql = IF(@column_exists = 0,
    'ALTER TABLE `bets` ADD COLUMN `bet_details` TEXT COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT ''投注详情JSON（包含完整的下注信息）'' AFTER `issue`',
    'SELECT ''bet_details 字段已存在，跳过'' AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 验证字段
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'bets'
AND COLUMN_NAME = 'bet_details';
