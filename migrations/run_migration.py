#!/usr/bin/env python3
"""
数据库迁移脚本：添加 bet_details 字段
执行方式: python migrations/run_migration.py
"""
import sys
import os
import asyncio
import logging

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from base.init_db import get_sync_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """执行数据库迁移"""
    logger.info("🔄 开始数据库迁移：添加 bet_details 字段")

    # 获取同步数据库引擎
    engine = get_sync_engine()

    try:
        with engine.connect() as conn:
            # 检查字段是否已存在
            check_sql = text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'bets'
                AND COLUMN_NAME = 'bet_details'
            """)

            result = conn.execute(check_sql)
            row = result.fetchone()

            if row and row[0] > 0:
                logger.info("✅ bet_details 字段已存在，跳过迁移")
                return

            # 添加字段
            logger.info("📝 添加 bet_details 字段...")
            alter_sql = text("""
                ALTER TABLE `bets`
                ADD COLUMN `bet_details` TEXT COLLATE utf8mb4_unicode_ci DEFAULT NULL
                COMMENT '投注详情JSON（包含完整的下注信息）'
                AFTER `issue`
            """)

            conn.execute(alter_sql)
            conn.commit()

            logger.info("✅ bet_details 字段添加成功！")

            # 验证
            verify_sql = text("""
                SHOW COLUMNS FROM `bets` LIKE 'bet_details'
            """)

            result = conn.execute(verify_sql)
            row = result.fetchone()

            if row:
                logger.info(f"✅ 验证成功: {row}")
            else:
                logger.error("❌ 验证失败：字段未找到")

    except Exception as e:
        logger.error(f"❌ 迁移失败: {str(e)}")
        raise
    finally:
        engine.dispose()

    logger.info("🎉 数据库迁移完成！")


if __name__ == "__main__":
    run_migration()
