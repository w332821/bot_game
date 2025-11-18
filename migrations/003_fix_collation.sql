-- 修复字符集collation不一致问题
-- 将所有account相关字段统一为 utf8mb4_unicode_ci
-- 执行时间: 2025-11-18

-- 修复 agent_profiles 表
ALTER TABLE agent_profiles
MODIFY COLUMN account VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '代理账号',
MODIFY COLUMN superior_account VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '上级代理账号',
MODIFY COLUMN invite_code VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '邀请码';

-- 修复 member_profiles 表
ALTER TABLE member_profiles
MODIFY COLUMN account VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '会员账号',
MODIFY COLUMN superior_account VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '上级代理账号';

-- 修复 login_logs 表
ALTER TABLE login_logs
MODIFY COLUMN account VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '登录账号';

-- 修复 sub_accounts 表
ALTER TABLE sub_accounts
MODIFY COLUMN account VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '子账号';

-- 验证修改结果
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    COLLATION_NAME
FROM
    information_schema.COLUMNS
WHERE
    TABLE_SCHEMA = DATABASE()
    AND COLUMN_NAME LIKE '%account%'
    AND TABLE_NAME IN ('agent_profiles', 'member_profiles', 'login_logs', 'sub_accounts')
ORDER BY
    TABLE_NAME, COLUMN_NAME;
