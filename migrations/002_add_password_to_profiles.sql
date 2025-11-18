-- 为 agent_profiles 和 member_profiles 添加 password 列
-- 用于代理和会员登录认证

-- 添加 agent_profiles.password
ALTER TABLE agent_profiles
ADD COLUMN password VARCHAR(100) DEFAULT NULL COMMENT '登录密码（bcrypt加密）' AFTER account;

-- 添加 member_profiles.password
ALTER TABLE member_profiles
ADD COLUMN password VARCHAR(100) DEFAULT NULL COMMENT '登录密码（bcrypt加密）' AFTER account;
