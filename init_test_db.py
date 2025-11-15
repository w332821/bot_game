#!/usr/bin/env python3
"""
初始化测试数据库
"""

import sys
import os
import logging
from sqlalchemy import create_engine
from sqlmodel import SQLModel

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TEST_DB_URI = "mysql+pymysql://root:123456@localhost:3306/game_bot_test"

if __name__ == "__main__":
    print("🗄️  初始化测试数据库...")
    try:
        # 导入所有表模型
        from biz.all_tables import (
            UserTable,
            BetTable,
            ChatTable,
            DrawHistoryTable,
            OddsConfigTable,
            AdminAccountTable
        )

        # 创建引擎
        engine = create_engine(TEST_DB_URI, echo=False)

        # 创建所有表
        SQLModel.metadata.create_all(engine)

        engine.dispose()

        print("✅ 测试数据库初始化成功!")
        print(f"   - {UserTable.__tablename__}")
        print(f"   - {BetTable.__tablename__}")
        print(f"   - {ChatTable.__tablename__}")
        print(f"   - {DrawHistoryTable.__tablename__}")
        print(f"   - {OddsConfigTable.__tablename__}")
        print(f"   - {AdminAccountTable.__tablename__}")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
