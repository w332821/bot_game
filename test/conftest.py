"""
pytest配置文件 - 全局fixtures
"""
import os
import sys
import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 测试数据库配置
TEST_DATABASE_URL = "mysql+asyncmy://root:123456@localhost:3306/game_bot_test"


@pytest.fixture(scope="function")
async def db_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )

    # 创建测试数据库（如果不存在）
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        # 数据库不存在，创建它
        temp_engine = create_async_engine(
            "mysql+asyncmy://root:123456@localhost:3306/",
            echo=False
        )
        async with temp_engine.begin() as conn:
            await conn.execute(text("CREATE DATABASE IF NOT EXISTS game_bot_test"))
        await temp_engine.dispose()

    yield engine

    # 清理
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """创建测试数据库会话"""
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    session = session_factory()

    try:
        yield session
    finally:
        await session.close()


@pytest.fixture(scope="function")
async def session_factory(db_engine):
    """返回session工厂"""
    return async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


# 测试数据fixtures

@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "id": "test_user_001",
        "username": "测试用户",
        "chat_id": "test_chat_001",
        "balance": Decimal("1000.00"),
        "score": 100,
        "rebate_ratio": Decimal("0.02"),
        "status": "活跃",
        "role": "normal",
        "created_by": "admin"
    }


@pytest.fixture
def sample_chat_data():
    """示例群聊数据"""
    return {
        "id": "test_chat_001",
        "name": "测试群聊",
        "game_type": "lucky8",
        "status": "active",
        "member_count": 10
    }


@pytest.fixture
def sample_bet_data():
    """示例投注数据"""
    return {
        "id": "bet_test_001",
        "user_id": "test_user_001",
        "username": "测试用户",
        "chat_id": "test_chat_001",
        "game_type": "lucky8",
        "lottery_type": "fan",
        "bet_number": 1,
        "bet_amount": Decimal("100.00"),
        "odds": Decimal("3.00"),
        "status": "active",
        "result": "pending"
    }


@pytest.fixture
def sample_admin_data():
    """示例管理员数据"""
    return {
        "id": "admin_test_001",
        "username": "test_admin",
        "password": "test_password_123",
        "role": "admin",
        "status": "active"
    }