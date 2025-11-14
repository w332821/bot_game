#!/usr/bin/env python3
"""
Day 1 验证脚本
验证数据库连接、表结构、基础模块是否正常
"""
import asyncio
import sys
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 数据库配置
DATABASE_URL = "mysql+asyncmy://root:123456@localhost:3306/game_bot"

# ANSI颜色代码
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    print(f"{RED}❌ {message}{RESET}")


def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")


def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")


async def validate_database_connection():
    """验证数据库连接"""
    print_info("验证数据库连接...")
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        await engine.dispose()
        print_success("数据库连接成功")
        return True
    except Exception as e:
        print_error(f"数据库连接失败: {e}")
        return False


async def validate_tables():
    """验证数据库表结构"""
    print_info("验证数据库表结构...")

    required_tables = [
        'users', 'bets', 'chats', 'admin_accounts',
        'draw_history', 'odds_config', 'deposit_records',
        'account_changes', 'rebate_records', 'operation_logs',
        'wallet_transfers'
    ]

    required_views = [
        'v_user_details', 'v_admin_earnings', 'v_daily_bet_stats'
    ]

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            # 检查表
            result = await conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]

            missing_tables = [t for t in required_tables if t not in tables]
            missing_views = [v for v in required_views if v not in tables]

            if missing_tables:
                print_error(f"缺失表: {', '.join(missing_tables)}")
                return False

            if missing_views:
                print_warning(f"缺失视图: {', '.join(missing_views)}")

            print_success(f"所有必需的表已创建 ({len(required_tables)}个表)")
            if not missing_views:
                print_success(f"所有视图已创建 ({len(required_views)}个视图)")

        await engine.dispose()
        return True
    except Exception as e:
        print_error(f"验证表结构失败: {e}")
        return False


async def validate_user_table():
    """验证users表结构"""
    print_info("验证users表结构...")

    required_columns = {
        'id': 'varchar',
        'username': 'varchar',
        'chat_id': 'varchar',
        'balance': 'decimal',
        'score': 'int',
        'rebate_ratio': 'decimal',
        'status': 'varchar',
        'created_at': 'datetime'
    }

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("DESCRIBE users"))
            columns = {row[0]: row[1] for row in result.fetchall()}

            missing = [col for col in required_columns if col not in columns]
            if missing:
                print_error(f"users表缺失字段: {', '.join(missing)}")
                return False

            print_success("users表结构正确")

        await engine.dispose()
        return True
    except Exception as e:
        print_error(f"验证users表失败: {e}")
        return False


async def test_user_crud():
    """测试用户CRUD操作"""
    print_info("测试用户CRUD操作...")

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        session_factory = async_sessionmaker(engine, class_=AsyncSession)

        async with session_factory() as session:
            # 插入测试用户
            insert_query = text("""
                INSERT INTO users (
                    id, username, chat_id, balance, score, rebate_ratio,
                    join_date, status, role, created_by, is_bot,
                    bot_config, is_new, created_at, updated_at
                ) VALUES (
                    :id, :username, :chat_id, :balance, :score, :rebate_ratio,
                    CURDATE(), :status, :role, :created_by, :is_bot,
                    '{}', :is_new, NOW(), NOW()
                )
            """)

            await session.execute(insert_query, {
                "id": "validate_test_user",
                "username": "验证测试用户",
                "chat_id": "validate_test_chat",
                "balance": Decimal("1000.00"),
                "score": 0,
                "rebate_ratio": Decimal("0.02"),
                "status": "活跃",
                "role": "normal",
                "created_by": "admin",
                "is_bot": False,
                "is_new": True
            })
            await session.commit()

            # 查询用户
            select_query = text("""
                SELECT * FROM users
                WHERE id = :id AND chat_id = :chat_id
            """)
            result = await session.execute(select_query, {
                "id": "validate_test_user",
                "chat_id": "validate_test_chat"
            })
            user = result.fetchone()

            if not user:
                print_error("插入的用户无法查询到")
                return False

            # 更新余额
            update_query = text("""
                UPDATE users
                SET balance = balance + :amount
                WHERE id = :id AND chat_id = :chat_id
            """)
            await session.execute(update_query, {
                "amount": Decimal("500.00"),
                "id": "validate_test_user",
                "chat_id": "validate_test_chat"
            })
            await session.commit()

            # 验证更新
            result = await session.execute(select_query, {
                "id": "validate_test_user",
                "chat_id": "validate_test_chat"
            })
            updated_user = result.fetchone()

            if float(updated_user.balance) != 1500.00:
                print_error(f"余额更新失败，期望1500.00，实际{updated_user.balance}")
                return False

            # 删除测试数据
            delete_query = text("""
                DELETE FROM users
                WHERE id = :id AND chat_id = :chat_id
            """)
            await session.execute(delete_query, {
                "id": "validate_test_user",
                "chat_id": "validate_test_chat"
            })
            await session.commit()

            print_success("用户CRUD操作测试通过")

        await engine.dispose()
        return True
    except Exception as e:
        print_error(f"用户CRUD测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def validate_modules_import():
    """验证模块导入"""
    print_info("验证模块导入...")

    modules_to_test = [
        ('biz.user.models.model', ['User', 'UserCreate', 'UserUpdate']),
        ('biz.user.repo.user_repo', ['UserRepository']),
        ('biz.user.service.user_service', ['UserService']),
        ('biz.bet.models.model', ['Bet', 'BetCreate']),
        ('biz.bet.repo.bet_repo', ['BetRepository']),
        ('biz.chat.models.model', ['Chat', 'ChatCreate']),
        ('biz.admin.models.model', ['AdminAccount', 'AdminLogin']),
        ('biz.draw.models.model', ['DrawHistory', 'DrawCreate']),
        ('biz.odds.models.model', ['OddsConfig', 'OddsUpdate']),
    ]

    all_success = True

    for module_path, classes in modules_to_test:
        try:
            module = __import__(module_path, fromlist=classes)
            for cls_name in classes:
                if not hasattr(module, cls_name):
                    print_error(f"{module_path} 缺少类 {cls_name}")
                    all_success = False
        except ImportError as e:
            print_error(f"导入失败: {module_path} - {e}")
            all_success = False

    if all_success:
        print_success("所有模块导入成功")

    return all_success


async def main():
    """主验证流程"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Day 1 验证测试{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    results = {}

    # 1. 数据库连接
    results['db_connection'] = await validate_database_connection()
    print()

    # 2. 表结构
    if results['db_connection']:
        results['tables'] = await validate_tables()
        print()

        results['user_table'] = await validate_user_table()
        print()
    else:
        results['tables'] = False
        results['user_table'] = False

    # 3. CRUD操作
    if results['user_table']:
        results['user_crud'] = await test_user_crud()
        print()
    else:
        results['user_crud'] = False

    # 4. 模块导入
    results['modules_import'] = await validate_modules_import()
    print()

    # 总结
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}验证总结{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test_name, result in results.items():
        status = f"{GREEN}✅ PASSED{RESET}" if result else f"{RED}❌ FAILED{RESET}"
        print(f"{test_name:20s}: {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print(f"\n{GREEN}🎉 所有验证测试通过！Day 1 完成度: 100%{RESET}\n")
        return 0
    else:
        print(f"\n{RED}⚠️  部分验证测试失败，请检查错误信息{RESET}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
