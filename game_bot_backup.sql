-- MySQL dump 10.13  Distrib 8.0.44, for macos15.4 (arm64)
--
-- Host: localhost    Database: game_bot
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account_changes`
--

DROP TABLE IF EXISTS `account_changes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_changes` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `user_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户ID',
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `chat_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '群聊ID',
  `amount` decimal(10,2) NOT NULL COMMENT '变动金额（正数为增加，负数为减少）',
  `balance_before` decimal(12,2) NOT NULL COMMENT '变动前余额',
  `balance_after` decimal(12,2) NOT NULL COMMENT '变动后余额',
  `type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '变动类型：bet、win、loss、deposit、withdraw、rebate等',
  `ref_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '关联ID（如投注ID、充值记录ID）',
  `note` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_chat` (`user_id`,`chat_id`),
  KEY `idx_type` (`type`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_ref_id` (`ref_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='账变记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_changes`
--

LOCK TABLES `account_changes` WRITE;
/*!40000 ALTER TABLE `account_changes` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_changes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_accounts`
--

DROP TABLE IF EXISTS `admin_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_accounts` (
  `id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '管理员ID',
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名（登录用）',
  `password` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码（bcrypt加密）',
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'distributor' COMMENT '角色：super_admin、distributor',
  `managed_chat_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '管理的群聊ID（分销商专用）',
  `balance` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT '钱包余额',
  `total_rebate_collected` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT '累计收取回水金额',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active' COMMENT '状态：active、suspended',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '描述',
  `created_date` date NOT NULL COMMENT '创建日期',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_role` (`role`),
  KEY `idx_managed_chat_id` (`managed_chat_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员账户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_accounts`
--

LOCK TABLES `admin_accounts` WRITE;
/*!40000 ALTER TABLE `admin_accounts` DISABLE KEYS */;
INSERT INTO `admin_accounts` VALUES ('admin','admin','$2a$10$3zjq1DfSixKeuMYlAWsNKOz1xj/KpVU9euFQVNm1K192XkOqYSaDG','super_admin',NULL,0.00,0.00,'active','系统超级管理员','2025-11-13','2025-11-13 13:51:42','2025-11-13 13:51:42');
/*!40000 ALTER TABLE `admin_accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bets`
--

DROP TABLE IF EXISTS `bets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bets` (
  `id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '投注ID',
  `user_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户ID',
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名（冗余字段，方便查询）',
  `chat_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '群聊ID',
  `game_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'lucky8' COMMENT '游戏类型：lucky8、liuhecai',
  `lottery_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '玩法类型：fan、zheng、nian、jiao、tong、tema等',
  `bet_number` int DEFAULT NULL COMMENT '下注号码（如番数1-4，特码1-49）',
  `bet_amount` decimal(10,2) NOT NULL COMMENT '下注金额',
  `odds` decimal(10,2) NOT NULL COMMENT '赔率',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active' COMMENT '状态：active、settled、cancelled',
  `result` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending' COMMENT '结果：pending、win、loss、tie',
  `pnl` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '盈亏金额（正数为赢，负数为输）',
  `issue` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '期号',
  `bet_details` text COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '投注详情JSON（包含完整的下注信息）',
  `draw_number` int DEFAULT NULL COMMENT '开奖号码（番数）',
  `draw_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '开奖号码串（如"3,15,7,19,12,8,4,20"）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `settled_at` datetime DEFAULT NULL COMMENT '结算时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_chat` (`user_id`,`chat_id`),
  KEY `idx_chat_id` (`chat_id`),
  KEY `idx_status` (`status`),
  KEY `idx_result` (`result`),
  KEY `idx_issue` (`issue`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_settled_at` (`settled_at`),
  KEY `idx_game_type` (`game_type`),
  KEY `idx_lottery_type` (`lottery_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='投注表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bets`
--

LOCK TABLES `bets` WRITE;
/*!40000 ALTER TABLE `bets` DISABLE KEYS */;
INSERT INTO `bets` VALUES ('bet_1760682083440_gv8exmqjo','68f0c91799d7631e57fa9376','银色','68f1e04bc3f5304719246c1c','lucky8','odd',0,100.00,3.20,'settled','win',215.60,'31296732',3,'02,07,04,01,10,08,12,19','2025-11-15 09:21:10',NULL),('bet_1760685258402_zfjqafdiu','68f0bfe9d71d39757fc49bea','三七','68f1e6d0d887af8dad0131a4','lucky8','even',2,3.00,10.00,'settled','lose',-3.00,'2025289',3,'35,04,23,10,44,24,42','2025-11-15 09:21:10',NULL),('bet_1760685258406_nfcqgfjqb','68f0bfe9d71d39757fc49bea','三七','68f1e6d0d887af8dad0131a4','lucky8','even',4,5.00,10.00,'settled','lose',-5.00,'2025289',3,'35,04,23,10,44,24,42','2025-11-15 09:21:10',NULL),('bet_1760685258412_m6zfncjyq','68f0bfe9d71d39757fc49bea','三七','68f1e6d0d887af8dad0131a4','lucky8','even',6,7.00,10.00,'settled','lose',-7.00,'2025289',3,'35,04,23,10,44,24,42','2025-11-15 09:21:10',NULL),('bet_1760686181556_6fqwkhrz6','68f0be98d71d39757fc49b0c','1','68f1e6d0d887af8dad0131a4','lucky8','zheng',1,100.00,2.00,'settled','push',0.00,'31296748',2,'07,12,17,11,20,02,10,14','2025-11-15 09:21:10',NULL),('bet_1760690330411_vipeujlt2','68f0bfe9d71d39757fc49bea','三七','68f1e6d0d887af8dad0131a4','lucky8','even',0,20.00,1.80,'settled','lose',-20.00,'31296762',4,'03,01,14,16,02,18,19,08','2025-11-15 09:21:10',NULL),('bet_1760690366093_1kniyq8aj','68f0be98d71d39757fc49b0c','1','68f1e6d0d887af8dad0131a4','lucky8','zheng',1,100.00,2.00,'settled','push',0.00,'31296762',4,'03,01,14,16,02,18,19,08','2025-11-15 09:21:10',NULL),('bet_1760700442312_8rilirg8e','68ef83c98322e080eeab28a5','你儿','68f1f032d887af8dad014658','lucky8','odd',0,100.00,3.20,'settled','lose',-100.00,'31296794',4,'02,13,10,11,19,07,09,08','2025-11-15 09:21:10',NULL),('bet_1760700445704_fwz8shf5k','68ef83c98322e080eeab28a5','你儿','68f1f032d887af8dad014658','lucky8','even',0,100.00,3.50,'settled','win',245.00,'31296794',4,'02,13,10,11,19,07,09,08','2025-11-15 09:21:10',NULL),('bet_1760700479040_zmqevs3ne','68ef83c98322e080eeab28a5','你儿','68f1f032d887af8dad014658','lucky8','even',8,100.00,10.00,'settled','lose',-100.00,'2025289',3,'35,04,23,10,44,24,42','2025-11-15 09:21:10',NULL),('bet_1760700484873_9lgen8qp4','68ef83c98322e080eeab28a5','你儿','68f1f032d887af8dad014658','lucky8','even',9,200.00,10.00,'settled','lose',-200.00,'2025289',3,'35,04,23,10,44,24,42','2025-11-15 09:21:10',NULL),('bet_1760700508183_v8c9rf468','68ef83c98322e080eeab28a5','你儿','68f1f032d887af8dad014658','lucky8','even',9,100.00,10.00,'settled','lose',-100.00,'2025289',3,'35,04,23,10,44,24,42','2025-11-15 09:21:10',NULL),('bet_1760700512572_t4e6xmqwn','68ef83c98322e080eeab28a5','你儿','68f1f032d887af8dad014658','lucky8','even',10,300.00,10.00,'settled','lose',-300.00,'2025289',3,'35,04,23,10,44,24,42','2025-11-15 09:21:10',NULL),('bet_1760700520469_ufz9zd6hc','68ef83c98322e080eeab28a5','你儿','68f1f032d887af8dad014658','lucky8','even',42,500.00,10.00,'settled','lose',-500.00,'2025289',3,'35,04,23,10,44,24,42','2025-11-15 09:21:10',NULL),('bet_1760700529525_69evjfhka','68ef83c98322e080eeab28a5','你儿','68f1f032d887af8dad014658','lucky8','even',9,300.00,10.00,'settled','lose',-300.00,'2025289',3,'35,04,23,10,44,24,42','2025-11-15 09:21:10',NULL),('bet_1760703978204_j0jnc0rhp','68f0be98d71d39757fc49b0c','1','68f1e6d0d887af8dad0131a4','lucky8','zheng',1,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1760704212798_cbwsvn6q7','68f0be98d71d39757fc49b0c','1','68f236c046d1a9b69b0f1d5b','lucky8','zheng',1,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1760770229591_v5rouijgx','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','even',0,10.00,1.80,'settled','lose',-10.00,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770229595_i371hy51x','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','even',0,10.00,1.30,'settled','lose',-10.00,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770264563_29qu5ea3m','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','even',0,10.00,1.80,'settled','lose',-10.00,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770274187_wi9chtu8r','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','even',0,10.00,1.80,'settled','win',7.84,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770292228_s48ouyx9q','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','even',0,10.00,2.00,'settled','push',0.00,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770322980_8lqvzm2d2','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','even',0,10.00,1.80,'settled','win',7.84,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770322985_p7jaff6qp','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','even',0,10.00,1.30,'settled','win',2.94,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770348768_69s5cxfu0','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','even',0,10.00,1.80,'settled','win',7.84,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770380258_bfyn4zi11','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','fan',3,10.00,3.00,'settled','lose',-10.00,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770385206_v8952y6xt','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','zheng',3,10.00,2.00,'settled','push',0.00,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770411576_b4rzkt5o7','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','even',3,10.00,3.00,'settled','push',0.00,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1760770428134_z00jvs91i','68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b','lucky8','even',3,10.00,3.00,'settled','push',0.00,'31297028',4,'04,12,18,11,02,15,10,16','2025-11-15 09:21:10',NULL),('bet_1761017314285_kbztdiicm','68ef83c98322e080eeab28a5','你儿','68f31b223d013a794a528738','lucky8','even',1,2.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761017314292_13ezgjniw','68ef83c98322e080eeab28a5','你儿','68f31b223d013a794a528738','lucky8','even',1,100.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761017327472_sh4lqbqu8','68ef83c98322e080eeab28a5','你儿','68f31b223d013a794a528738','lucky8','even',1,2.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761017327477_kwlck0uro','68ef83c98322e080eeab28a5','你儿','68f31b223d013a794a528738','lucky8','even',3,100.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761392041324_wuosmu8ly','68fca507a4c538034fc34246','您是要','68fca554732d28c9499e9d01','lucky8','even',NULL,123.00,3.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761392071978_oinhvrlmn','68fca507a4c538034fc34246','您是要','68fca554732d28c9499e9d01','lucky8','even',NULL,234.00,3.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761406781356_4hougeyy8','68fce96b3f940333ff625b00','我陪着','68fcea42e5fbf0e082b12846','lucky8','odd',NULL,56.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761409041134_fnyqhjzwr','68fce96b3f940333ff625b00','我陪着','68fcf80407f36c3d0b8ae884','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562522721_pwvqns79k','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','zheng',1,10.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562532544_rsqz0cjl8','68ff3b0092487261731252a3','222','68ff4f92d47e78bd83c3ea0e','lucky8','zheng',1,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562657316_7xcpyibnx','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','zheng',2,10.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562661266_yfpqg9z44','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','zheng',3,10.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562664690_uujlow9k3','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','zheng',4,10.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562669308_qjw6n74az','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','jiao',NULL,10.00,1.80,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562673364_1tctff2rd','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','jiao',NULL,10.00,1.80,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562678648_l84v3eaqv','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','jiao',NULL,10.00,1.80,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562682981_1ucj7gjdb','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','jiao',NULL,10.00,1.80,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562691052_w2wwhuh58','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','tong',14,10.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562701242_qd2y67ysa','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','tong',21,10.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562721921_bppaxecqa','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','nian',12,10.00,1.80,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562730477_cn7vr8q6j','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','nian',23,10.00,1.80,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562739043_ske9nnr3j','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','nian',34,10.00,1.80,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562749294_r28315igo','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','nian',41,10.00,1.80,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562808057_ccz1ka5mt','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','zhong',NULL,10.00,1.30,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562812292_3um1ov9wt','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','zhong',NULL,10.00,1.30,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761562816851_89p7zfio6','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','zhong',NULL,10.00,1.30,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761563374728_nv81p7bxu','68ff3b0092487261731252a3','222','68ff4f92d47e78bd83c3ea0e','lucky8','zheng',1,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761563382603_0tq8x8h1s','68ff3b0092487261731252a3','222','68ff4f92d47e78bd83c3ea0e','lucky8','odd',NULL,200.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761563389651_p1b5mww2c','68ff3b0092487261731252a3','222','68ff4f92d47e78bd83c3ea0e','lucky8','tema',5,10.00,15.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761563389656_xciy0jho8','68ff3b0092487261731252a3','222','68ff4f92d47e78bd83c3ea0e','lucky8','tema',6,10.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761563713837_ffta6neqr','68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e','lucky8','fan',4,300.00,3.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761566003931_ov5hc8492','68ff4db3d47e78bd83c3e7a4','nxidj','68ff5aa07e94d66aaa07762f','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761566052166_kl7wtpath','68ff4db3d47e78bd83c3e7a4','nxidj','68ff5aa07e94d66aaa07762f','lucky8','tema',49,100.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761566540788_b1d9gmuzq','68ff4db3d47e78bd83c3e7a4','nxidj','68ff5aa07e94d66aaa07762f','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761567044145_ejelh48a4','68ff4db3d47e78bd83c3e7a4','nxidj','68ff5aa07e94d66aaa07762f','lucky8','tema',49,100.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761567464176_o4l2ex9x4','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','zheng',1,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761567523985_pybf8yiuy','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','zheng',2,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761568165682_pr7f2qtd2','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','zheng',1,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761568178549_96ia1c875','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','zheng',3,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761568205731_0rkm2twug','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','zheng',3,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761568228594_ggbrvpita','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','zheng',3,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761568240206_jp5fxve68','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','zheng',1,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761568701467_5o3vsdhyc','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761568710139_e6hyxhchy','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','even',NULL,100.00,3.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761569932773_g8zvgpscp','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761569941490_4276r3v62','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','even',NULL,200.00,3.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761569953366_wewnc0iel','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','even',NULL,100.00,3.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761569974542_wj8wegn0a','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','zheng',2,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761570173765_8q960z775','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','even',NULL,100.00,3.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761570187730_mg3rqdaky','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','zheng',2,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761570748703_qr7yy67sx','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','tema',49,100.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761570765552_bqphuvsuo','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','tema',49,100.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761570782301_6bbakzjm4','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','tema',49,100.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761571501271_ta8pdgp2u','68ff3b0092487261731252a3','222','68ff4f92d47e78bd83c3ea0e','lucky8','zhong',NULL,100.00,1.30,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761571536535_00h4vjr58','68ff3b0092487261731252a3','222','68ff4f92d47e78bd83c3ea0e','lucky8','jiao',NULL,50.00,1.80,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761572333943_lpcocqjpn','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','tema',49,100.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761572348523_lpimuipah','68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e','lucky8','tema',40,100.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761707063249_emdctzspy','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761707073523_w5k6ptl8b','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','even',NULL,200.00,3.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761707595622_05h7hlr3f','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761708214329_8d9demm4c','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761714952934_mdak75ux7','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','even',NULL,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761715332902_lg9exe8uf','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','even',NULL,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761715355558_i6d59ptc3','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761715362672_9sx4nggo9','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','even',NULL,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761715370529_arb7er0ze','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','even',NULL,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761715463049_wuixxa7uz','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761825619386_zu3oo4cxk','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761825639282_gdqnw5vqi','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','odd',NULL,100.00,3.20,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761875687815_u645vc3of','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','tema',2,20.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761875709595_5jsprhgjh','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','tema',15,10.00,10.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761875914469_xhx303jrt','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','tema',15,10.00,20.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761913536750_9hlzuh30u','69047cdd2443a3e5f5a83fd0','00','6904a9fd2443a3e5f5a8d9a1','lucky8','zheng',2,100.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761913669707_jpomkkavr','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','tema',1,100.00,10.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1761913704211_ohzotkjjo','6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e','lucky8','tema',1,100.00,10.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1762235664603_g04jzel8u','6904adbc2443a3e5f5a8f05e','22','6904adfd2443a3e5f5a8f26d','lucky8','zheng',1,200.00,2.00,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1762235794307_2vgoymwc9','6904adbc2443a3e5f5a8f05e','22','6904adfd2443a3e5f5a8f26d','lucky8','tema',1,10.00,10.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL),('bet_1762246979220_jimg56elv','6904adbc2443a3e5f5a8f05e','22','6909978c2443a3e5f5c61cd8','lucky8','tema',1,10.00,10.50,'active','pending',0.00,NULL,NULL,'','2025-11-15 09:21:10',NULL);
/*!40000 ALTER TABLE `bets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chats`
--

DROP TABLE IF EXISTS `chats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chats` (
  `id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '群聊ID',
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '群聊名称',
  `game_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'lucky8' COMMENT '游戏类型：lucky8、liuhecai',
  `owner_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属分销商ID（外键关联admin_accounts）',
  `auto_draw` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否自动开奖',
  `bet_lock_time` int NOT NULL DEFAULT '60' COMMENT '开奖前锁定时间（秒）',
  `member_count` int NOT NULL DEFAULT '0' COMMENT '成员数量',
  `total_bets` int NOT NULL DEFAULT '0' COMMENT '累计投注次数',
  `total_volume` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT '累计投注金额',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active' COMMENT '状态：active、suspended、deleted',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_owner_id` (`owner_id`),
  KEY `idx_game_type` (`game_type`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群聊表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chats`
--

LOCK TABLES `chats` WRITE;
/*!40000 ALTER TABLE `chats` DISABLE KEYS */;
INSERT INTO `chats` VALUES ('-123456789','群聊--1234567','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68efa9d68322e080eeab2b95','没事儿','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f1d7c3c3f530471924561b','群聊-68f1d7c3','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f1e04bc3f5304719246c1c','N多','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f1e3c3d887af8dad0120a6','群聊-68f1e3c3','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f1e420d887af8dad012428','偷摸','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f1e490d887af8dad0127c8','模仿者','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f1e6d0d887af8dad0131a4','111111111','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f1f032d887af8dad014658','群聊-68f1f032','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f236c046d1a9b69b0f1d5b','2222','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f24e2f46d1a9b69b0f2ade','hdidndn','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f31b223d013a794a528738','你儿子','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f8bed7a951ba0f6528acab','儿子','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f8c1c5544254a1e99c2684','额我的','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f8c2d5544254a1e99c2787','打游戏','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f8c54a544254a1e99c2971','嗯她','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f8c738544254a1e99c2b9a','动漫','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f99c98544254a1e99c2e59','佛山','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f9b986544254a1e99c3a4e','模型','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68f9e460303d3635f0f22e53','123','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68fb7561a4c538034fc313d6','捏你','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68fb7ee9a4c538034fc318b7','0000','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68fca554732d28c9499e9d01','颜色','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68fca58f732d28c9499e9f54','111','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68fcb431732d28c9499ec4e1','333','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68fcea42e5fbf0e082b12846','也行','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68fcf80407f36c3d0b8ae884','折叠椅','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68fcfc511ee0879eb0da7272','大致','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68ff4f92d47e78bd83c3ea0e','333','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68ff527fd47e78bd83c3f46f','小朋友','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68ff5a5a7e94d66aaa0773eb','增高','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68ff5aa07e94d66aaa07762f','你欺负我','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('68ff61de294874932930018e','某家','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('69018376e33e61ea35a0f48e','hbb','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('6904a9fd2443a3e5f5a8d9a1','111','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('6904adfd2443a3e5f5a8f26d','00','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('6909978c2443a3e5f5c61cd8','44','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('69114d5e2443a3e5f5fddc30','镊子','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('test_chat_001','游戏彩种切换测试群','liuhecai',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18'),('test_chat_123','群聊-test_cha','lucky8',NULL,1,60,0,0,0.00,'active','2025-11-15 09:06:18','2025-11-15 09:06:18');
/*!40000 ALTER TABLE `chats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deposit_records`
--

DROP TABLE IF EXISTS `deposit_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deposit_records` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `user_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户ID',
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `chat_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '群聊ID',
  `amount` decimal(10,2) NOT NULL COMMENT '金额（正数为充值，负数为扣款）',
  `balance_before` decimal(12,2) NOT NULL COMMENT '操作前余额',
  `balance_after` decimal(12,2) NOT NULL COMMENT '操作后余额',
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '类型：deposit、withdraw、admin_add、admin_remove',
  `admin_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '操作管理员ID',
  `note` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_chat` (`user_id`,`chat_id`),
  KEY `idx_admin_id` (`admin_id`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='充值记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deposit_records`
--

LOCK TABLES `deposit_records` WRITE;
/*!40000 ALTER TABLE `deposit_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `deposit_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `draw_history`
--

DROP TABLE IF EXISTS `draw_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `draw_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `draw_number` int NOT NULL,
  `issue` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `draw_code` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `game_type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_random` tinyint(1) NOT NULL,
  `chat_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `bet_count` int NOT NULL,
  `timestamp` datetime NOT NULL,
  `special_number` int DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_draw_history_game_type` (`game_type`),
  KEY `ix_draw_history_timestamp` (`timestamp`),
  KEY `ix_draw_history_issue` (`issue`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `draw_history`
--

LOCK TABLES `draw_history` WRITE;
/*!40000 ALTER TABLE `draw_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `draw_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `odds_config`
--

DROP TABLE IF EXISTS `odds_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `odds_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bet_type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `odds` decimal(10,2) NOT NULL,
  `min_bet` decimal(15,2) NOT NULL,
  `max_bet` decimal(15,2) NOT NULL,
  `period_max` decimal(15,2) NOT NULL,
  `game_type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tema_odds` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_odds_config_game_type` (`game_type`),
  KEY `ix_odds_config_bet_type` (`bet_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `odds_config`
--

LOCK TABLES `odds_config` WRITE;
/*!40000 ALTER TABLE `odds_config` DISABLE KEYS */;
/*!40000 ALTER TABLE `odds_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `operation_logs`
--

DROP TABLE IF EXISTS `operation_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `operation_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `admin_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '管理员ID',
  `admin_username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '管理员用户名',
  `action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '操作类型：login、add_credit、update_odds等',
  `target_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '操作对象类型：user、bet、odds、chat等',
  `target_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '操作对象ID',
  `details` json DEFAULT NULL COMMENT '操作详情（JSON格式）',
  `ip_address` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'IP地址',
  `user_agent` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '浏览器信息',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'success' COMMENT '操作状态：success、failed',
  `error_message` text COLLATE utf8mb4_unicode_ci COMMENT '错误信息（如果失败）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`),
  KEY `idx_admin_id` (`admin_id`),
  KEY `idx_action` (`action`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_target` (`target_type`,`target_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `operation_logs`
--

LOCK TABLES `operation_logs` WRITE;
/*!40000 ALTER TABLE `operation_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `operation_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rebate_records`
--

DROP TABLE IF EXISTS `rebate_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rebate_records` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `user_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户ID',
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `chat_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '群聊ID',
  `admin_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '收取回水的管理员ID',
  `bet_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '关联的投注ID',
  `amount` decimal(10,2) NOT NULL COMMENT '回水金额',
  `rebate_ratio` decimal(5,4) NOT NULL COMMENT '回水比例',
  `original_loss` decimal(10,2) NOT NULL COMMENT '原始亏损金额',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_admin_id` (`admin_id`),
  KEY `idx_chat_id` (`chat_id`),
  KEY `idx_bet_id` (`bet_id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='回水记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rebate_records`
--

LOCK TABLES `rebate_records` WRITE;
/*!40000 ALTER TABLE `rebate_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `rebate_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_stats`
--

DROP TABLE IF EXISTS `user_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_stats` (
  `user_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户ID',
  `chat_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '群聊ID',
  `total_bets` int NOT NULL DEFAULT '0' COMMENT '总投注次数',
  `total_bet_amount` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT '总投注金额',
  `total_win_amount` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT '总赢取金额',
  `total_loss_amount` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT '总输掉金额',
  `net_profit` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT '净盈亏',
  `win_rate` decimal(5,2) NOT NULL DEFAULT '0.00' COMMENT '胜率（百分比）',
  `last_bet_at` datetime DEFAULT NULL COMMENT '最后下注时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_id`,`chat_id`),
  KEY `idx_total_bets` (`total_bets`),
  KEY `idx_net_profit` (`net_profit`),
  KEY `idx_last_bet_at` (`last_bet_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户统计表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_stats`
--

LOCK TABLES `user_stats` WRITE;
/*!40000 ALTER TABLE `user_stats` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_stats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户ID（来自悦聊平台）',
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `chat_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '群聊ID',
  `balance` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT '账户余额（精确到分）',
  `score` int NOT NULL DEFAULT '0' COMMENT '积分（预留字段）',
  `rebate_ratio` decimal(5,4) NOT NULL DEFAULT '0.0200' COMMENT '回水比例（0.02=2%）',
  `join_date` date NOT NULL COMMENT '加入日期',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '活跃' COMMENT '状态：活跃、冻结、注销',
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'normal' COMMENT '角色：normal、vip、test',
  `created_by` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'admin' COMMENT '创建者（管理员ID）',
  `is_bot` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否为机器人用户',
  `bot_config` json DEFAULT NULL COMMENT '机器人配置（JSON格式）',
  `is_new` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否新用户',
  `marked_read_at` datetime DEFAULT NULL COMMENT '标记已读时间',
  `red_packet_settings` json DEFAULT NULL COMMENT '红包设置（JSON格式）',
  `avatar` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像路径',
  `last_seen` datetime DEFAULT NULL COMMENT '最后活跃时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`,`chat_id`),
  KEY `idx_chat_id` (`chat_id`),
  KEY `idx_status` (`status`),
  KEY `idx_balance` (`balance`),
  KEY `idx_join_date` (`join_date`),
  KEY `idx_last_seen` (`last_seen`),
  KEY `idx_created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('68ef83c98322e080eeab28a5','你儿','68efa9d68322e080eeab2b95',1060.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef83c98322e080eeab28a5','你儿','68f1d7c3c3f530471924561b',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef83c98322e080eeab28a5','你儿','68f1e04bc3f5304719246c1c',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef83c98322e080eeab28a5','你儿','68f1e3c3d887af8dad0120a6',3940.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef83c98322e080eeab28a5','你儿','68f1e420d887af8dad012428',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef83c98322e080eeab28a5','你儿','68f1e490d887af8dad0127c8',1100.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef83c98322e080eeab28a5','你儿','68f1f032d887af8dad014658',975.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef83c98322e080eeab28a5','你儿','68f24e2f46d1a9b69b0f2ade',1060.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef83c98322e080eeab28a5','你儿','68f31b223d013a794a528738',856.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef840b8322e080eeab28b3','Jdsklj','68efa9d68322e080eeab2b95',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef840b8322e080eeab28b3','Jdsklj','68f1e420d887af8dad012428',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ef843a8322e080eeab290d','jskadl','68f24e2f46d1a9b69b0f2ade',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f0be98d71d39757fc49b0c','1','68f1e6d0d887af8dad0131a4',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f0be98d71d39757fc49b0c','1','68f236c046d1a9b69b0f1d5b',900.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f0bfe9d71d39757fc49bea','三七','68f1e6d0d887af8dad0131a4',1065.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f0bfe9d71d39757fc49bea','三七','68f236c046d1a9b69b0f1d5b',986.46,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f0c91799d7631e57fa9376','银色','68f1d7c3c3f530471924561b',0.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f0c91799d7631e57fa9376','银色','68f1e04bc3f5304719246c1c',1215.60,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f0c91799d7631e57fa9376','银色','68f1e3c3d887af8dad0120a6',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f0c91799d7631e57fa9376','银色','68f1f032d887af8dad014658',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f0ebc8e91398aa8520d0d2','1234fdfg','68f1e490d887af8dad0127c8',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f0ebc8e91398aa8520d0d2','1234fdfg','68f31b223d013a794a528738',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f8b95e5e056abbe201ab06','你爹','68f8c2d5544254a1e99c2787',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f8b95e5e056abbe201ab06','你爹','68f8c54a544254a1e99c2971',897.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f8b95e5e056abbe201ab06','你爹','68f8c738544254a1e99c2b9a',1118.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f8b9e75e056abbe201ab2c','jaskldj','68f8c2d5544254a1e99c2787',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f8b9e75e056abbe201ab2c','jaskldj','68f8c54a544254a1e99c2971',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f8b9e75e056abbe201ab2c','jaskldj','68f8c738544254a1e99c2b9a',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f99c29544254a1e99c2dbd','我陪着','68f99c98544254a1e99c2e59',1440.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f9b913544254a1e99c3994','镊子','68f9b986544254a1e99c3a4e',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f9e3ae303d3635f0f22d85','111','68f9e460303d3635f0f22e53',1168.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68f9e42c303d3635f0f22df2','三七','68f9e460303d3635f0f22e53',500.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fb7490303d3635f0f24bde','hdijdk','68fb7561a4c538034fc313d6',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fb7e98a4c538034fc31857','三七','68fb7ee9a4c538034fc318b7',1096.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fb7eb4a4c538034fc3186e','11','68fb7ee9a4c538034fc318b7',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fca469a4c538034fc34199','12','68fca58f732d28c9499e9f54',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fca469a4c538034fc34199','12','68fcb431732d28c9499ec4e1',700.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fca4b9a4c538034fc341be','三七','68fca58f732d28c9499e9f54',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fca4b9a4c538034fc341be','三七','68fcb431732d28c9499ec4e1',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fca507a4c538034fc34246','您是要','68fca554732d28c9499e9d01',900.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fce9593f940333ff625af7','asdasf','68fcf80407f36c3d0b8ae884',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fce9593f940333ff625af7','asdasf','68fcfc511ee0879eb0da7272',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fce96b3f940333ff625b00','我陪着','68fcea42e5fbf0e082b12846',1310.20,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fce96b3f940333ff625b00','我陪着','68fcf80407f36c3d0b8ae884',1220.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68fce96b3f940333ff625b00','我陪着','68fcfc511ee0879eb0da7272',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ff3b0092487261731252a3','222','68ff4f92d47e78bd83c3ea0e',1400.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ff3b2192487261731252af','三七','68ff4f92d47e78bd83c3ea0e',680.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ff4da2d47e78bd83c3e799','asd','68ff5a5a7e94d66aaa0773eb',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ff4da2d47e78bd83c3e799','asd','68ff5aa07e94d66aaa07762f',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ff4db3d47e78bd83c3e7a4','nxidj','68ff527fd47e78bd83c3f46f',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ff4db3d47e78bd83c3e7a4','nxidj','68ff5a5a7e94d66aaa0773eb',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ff4db3d47e78bd83c3e7a4','nxidj','68ff5aa07e94d66aaa07762f',700.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('68ff4db3d47e78bd83c3e7a4','nxidj','68ff61de294874932930018e',2650.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('6901828df4a14ff40ad40b96','nxkdn','69018376e33e61ea35a0f48e',775.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('690182acf4a14ff40ad40ba1','asdjaklj','69018376e33e61ea35a0f48e',1020.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('69045eab2443a3e5f5a7d9e2','三七','6904a9fd2443a3e5f5a8d9a1',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('69045eab2443a3e5f5a7d9e2','三七','6909978c2443a3e5f5c61cd8',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('69047cdd2443a3e5f5a83fd0','00','6904a9fd2443a3e5f5a8d9a1',10900.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('6904adbc2443a3e5f5a8f05e','22','6904adfd2443a3e5f5a8f26d',951.52,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('6904adbc2443a3e5f5a8f05e','22','6909978c2443a3e5f5c61cd8',990.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('6909970d2443a3e5f5c6195e','三七','6909978c2443a3e5f5c61cd8',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('69114c782443a3e5f5fdd975','643464','69114d5e2443a3e5f5fddc30',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('69114d3e2443a3e5f5fddb1f','dsfewr','69114d5e2443a3e5f5fddc30',1000.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('test_bot_1761392590327','测试机器人','-123456789',1200.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10'),('test_user_456','TestPlayer','test_chat_123',800.00,0,0.0200,'2025-11-15','活跃','normal','admin',0,NULL,1,NULL,NULL,NULL,NULL,'2025-11-15 09:21:10','2025-11-15 09:21:10');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_admin_earnings`
--

DROP TABLE IF EXISTS `v_admin_earnings`;
/*!50001 DROP VIEW IF EXISTS `v_admin_earnings`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_admin_earnings` AS SELECT 
 1 AS `id`,
 1 AS `username`,
 1 AS `role`,
 1 AS `balance`,
 1 AS `total_rebate_collected`,
 1 AS `recent_rebate_30days`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_daily_bet_stats`
--

DROP TABLE IF EXISTS `v_daily_bet_stats`;
/*!50001 DROP VIEW IF EXISTS `v_daily_bet_stats`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_daily_bet_stats` AS SELECT 
 1 AS `bet_date`,
 1 AS `chat_id`,
 1 AS `game_type`,
 1 AS `total_bets`,
 1 AS `total_amount`,
 1 AS `total_win`,
 1 AS `total_loss`,
 1 AS `net_profit`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_user_details`
--

DROP TABLE IF EXISTS `v_user_details`;
/*!50001 DROP VIEW IF EXISTS `v_user_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_user_details` AS SELECT 
 1 AS `id`,
 1 AS `username`,
 1 AS `chat_id`,
 1 AS `balance`,
 1 AS `rebate_ratio`,
 1 AS `status`,
 1 AS `join_date`,
 1 AS `last_seen`,
 1 AS `chat_name`,
 1 AS `game_type`,
 1 AS `total_bets`,
 1 AS `total_bet_amount`,
 1 AS `net_profit`,
 1 AS `win_rate`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `wallet_transfers`
--

DROP TABLE IF EXISTS `wallet_transfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wallet_transfers` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `from_admin_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '转出管理员ID',
  `to_admin_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '转入管理员ID',
  `amount` decimal(10,2) NOT NULL COMMENT '转账金额',
  `balance_before_from` decimal(12,2) NOT NULL COMMENT '转出方操作前余额',
  `balance_after_from` decimal(12,2) NOT NULL COMMENT '转出方操作后余额',
  `balance_before_to` decimal(12,2) NOT NULL COMMENT '转入方操作前余额',
  `balance_after_to` decimal(12,2) NOT NULL COMMENT '转入方操作后余额',
  `note` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'completed' COMMENT '状态：completed、failed',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_from_admin` (`from_admin_id`),
  KEY `idx_to_admin` (`to_admin_id`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='钱包转账记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wallet_transfers`
--

LOCK TABLES `wallet_transfers` WRITE;
/*!40000 ALTER TABLE `wallet_transfers` DISABLE KEYS */;
/*!40000 ALTER TABLE `wallet_transfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `v_admin_earnings`
--

/*!50001 DROP VIEW IF EXISTS `v_admin_earnings`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_admin_earnings` AS select `a`.`id` AS `id`,`a`.`username` AS `username`,`a`.`role` AS `role`,`a`.`balance` AS `balance`,`a`.`total_rebate_collected` AS `total_rebate_collected`,coalesce(sum(`r`.`amount`),0) AS `recent_rebate_30days` from (`admin_accounts` `a` left join `rebate_records` `r` on(((`a`.`id` = `r`.`admin_id`) and (`r`.`created_at` >= (now() - interval 30 day))))) group by `a`.`id`,`a`.`username`,`a`.`role`,`a`.`balance`,`a`.`total_rebate_collected` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_daily_bet_stats`
--

/*!50001 DROP VIEW IF EXISTS `v_daily_bet_stats`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_daily_bet_stats` AS select cast(`bets`.`created_at` as date) AS `bet_date`,`bets`.`chat_id` AS `chat_id`,`bets`.`game_type` AS `game_type`,count(0) AS `total_bets`,sum(`bets`.`bet_amount`) AS `total_amount`,sum((case when (`bets`.`result` = 'win') then `bets`.`pnl` else 0 end)) AS `total_win`,sum((case when (`bets`.`result` = 'loss') then abs(`bets`.`pnl`) else 0 end)) AS `total_loss`,sum(`bets`.`pnl`) AS `net_profit` from `bets` where (`bets`.`status` = 'settled') group by cast(`bets`.`created_at` as date),`bets`.`chat_id`,`bets`.`game_type` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_user_details`
--

/*!50001 DROP VIEW IF EXISTS `v_user_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_user_details` AS select `u`.`id` AS `id`,`u`.`username` AS `username`,`u`.`chat_id` AS `chat_id`,`u`.`balance` AS `balance`,`u`.`rebate_ratio` AS `rebate_ratio`,`u`.`status` AS `status`,`u`.`join_date` AS `join_date`,`u`.`last_seen` AS `last_seen`,`c`.`name` AS `chat_name`,`c`.`game_type` AS `game_type`,coalesce(`s`.`total_bets`,0) AS `total_bets`,coalesce(`s`.`total_bet_amount`,0) AS `total_bet_amount`,coalesce(`s`.`net_profit`,0) AS `net_profit`,coalesce(`s`.`win_rate`,0) AS `win_rate` from ((`users` `u` left join `chats` `c` on((`u`.`chat_id` = `c`.`id`))) left join `user_stats` `s` on(((`u`.`id` = `s`.`user_id`) and (`u`.`chat_id` = `s`.`chat_id`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-15  9:30:30
