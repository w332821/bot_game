-- ============================================
-- 报表模块字段补充迁移脚本
-- 执行方式：mysql -u用户名 -p 数据库名 < migrations/001_add_report_fields.sql
-- 或在MySQL客户端中直接执行
-- ============================================

-- 1. bet_orders 表添加字段
ALTER TABLE bet_orders
ADD COLUMN valid_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '有效金额' AFTER bet_amount;

ALTER TABLE bet_orders
ADD COLUMN gameplay VARCHAR(100) NULL DEFAULT NULL COMMENT '玩法名称' AFTER status;

-- 2. 将现有数据的 valid_amount 设置为 bet_amount
UPDATE bet_orders SET valid_amount = bet_amount WHERE valid_amount = 0.00;

-- 3. member_profiles 表添加字段
ALTER TABLE member_profiles
ADD COLUMN name VARCHAR(100) NULL DEFAULT NULL COMMENT '会员姓名' AFTER account;

ALTER TABLE member_profiles
ADD COLUMN level INT NOT NULL DEFAULT 1 COMMENT '会员级别' AFTER name;

CREATE INDEX idx_member_level ON member_profiles(level);

-- 4. 将现有数据的 name 设置为 account
UPDATE member_profiles SET name = account WHERE name IS NULL;

-- 5. agent_profiles 表添加字段
ALTER TABLE agent_profiles
ADD COLUMN name VARCHAR(100) NULL DEFAULT NULL COMMENT '代理姓名' AFTER account;

ALTER TABLE agent_profiles
ADD COLUMN level INT NOT NULL DEFAULT 1 COMMENT '代理级别' AFTER name;

CREATE INDEX idx_agent_level ON agent_profiles(level);

-- 6. 将现有数据的 name 设置为 account
UPDATE agent_profiles SET name = account WHERE name IS NULL;

-- 7. 创建代理结算配置表
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

-- 8. 为现有代理创建默认配置
INSERT INTO agent_settlement_config (agent_user_id, share_percentage, earn_rebate_mode)
SELECT user_id, 0.00, 'none' FROM agent_profiles
ON DUPLICATE KEY UPDATE agent_user_id = agent_user_id;

-- ============================================
-- 迁移完成验证
-- ============================================
SELECT '✅ 数据库迁移完成！' AS status;
SELECT 'bet_orders表字段' AS check_item, COUNT(*) AS affected_rows FROM bet_orders WHERE valid_amount >= 0;
SELECT 'member_profiles表字段' AS check_item, COUNT(*) AS affected_rows FROM member_profiles WHERE name IS NOT NULL;
SELECT 'agent_profiles表字段' AS check_item, COUNT(*) AS affected_rows FROM agent_profiles WHERE name IS NOT NULL;
SELECT 'agent_settlement_config表' AS check_item, COUNT(*) AS affected_rows FROM agent_settlement_config;
