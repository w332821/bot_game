-- 初始化赔率配置表数据

-- 澳洲幸运8赔率配置
INSERT INTO odds_config (bet_type, odds, min_bet, max_bet, period_max, game_type, description, tema_odds, status, created_at, updated_at) VALUES
('fan', 3.00, 10.00, 10000.00, 50000.00, 'lucky8', '番：单号投注', NULL, 'active', NOW(), NOW()),
('zheng', 2.00, 10.00, 10000.00, 50000.00, 'lucky8', '正：对立号投注', NULL, 'active', NOW(), NOW()),
('nian', 2.00, 10.00, 10000.00, 50000.00, 'lucky8', '念：两个番数', NULL, 'active', NOW(), NOW()),
('jiao', 1.50, 10.00, 10000.00, 50000.00, 'lucky8', '角：相邻番数', NULL, 'active', NOW(), NOW()),
('tong', 2.00, 10.00, 10000.00, 50000.00, 'lucky8', '通/借：首位赢，末位输', NULL, 'active', NOW(), NOW()),
('zheng_jin', 2.00, 10.00, 10000.00, 50000.00, 'lucky8', '正（禁号）：指定禁号', NULL, 'active', NOW(), NOW()),
('zhong', 1.33, 10.00, 10000.00, 50000.00, 'lucky8', '三码（中）：覆盖3个结果号', NULL, 'active', NOW(), NOW()),
('odd', 2.00, 10.00, 10000.00, 50000.00, 'lucky8', '单：奇数投注', NULL, 'active', NOW(), NOW()),
('even', 2.00, 10.00, 10000.00, 50000.00, 'lucky8', '双：偶数投注', NULL, 'active', NOW(), NOW()),
('tema_lucky8', 10.00, 10.00, 5000.00, 20000.00, 'lucky8', '澳8特码：1-20号', NULL, 'active', NOW(), NOW()),

-- 六合彩赔率配置
('fan', 3.00, 10.00, 10000.00, 50000.00, 'liuhecai', '番：单号投注', NULL, 'active', NOW(), NOW()),
('zheng', 2.00, 10.00, 10000.00, 50000.00, 'liuhecai', '正：对立号投注', NULL, 'active', NOW(), NOW()),
('nian', 2.00, 10.00, 10000.00, 50000.00, 'liuhecai', '念：两个番数', NULL, 'active', NOW(), NOW()),
('jiao', 1.50, 10.00, 10000.00, 50000.00, 'liuhecai', '角：相邻番数', NULL, 'active', NOW(), NOW()),
('tong', 2.00, 10.00, 10000.00, 50000.00, 'liuhecai', '通/借：首位赢，末位输', NULL, 'active', NOW(), NOW()),
('zheng_jin', 2.00, 10.00, 10000.00, 50000.00, 'liuhecai', '正（禁号）：指定禁号', NULL, 'active', NOW(), NOW()),
('zhong', 1.33, 10.00, 10000.00, 50000.00, 'liuhecai', '三码（中）：覆盖3个结果号', NULL, 'active', NOW(), NOW()),
('odd', 2.00, 10.00, 10000.00, 50000.00, 'liuhecai', '单：奇数投注', NULL, 'active', NOW(), NOW()),
('even', 2.00, 10.00, 10000.00, 50000.00, 'liuhecai', '双：偶数投注', NULL, 'active', NOW(), NOW()),
('tema_liuhecai', 40.00, 10.00, 2000.00, 10000.00, 'liuhecai', '六合彩特码：1-49号', NULL, 'active', NOW(), NOW());

-- 查询结果验证
SELECT bet_type, game_type, odds, description FROM odds_config ORDER BY game_type, bet_type;
