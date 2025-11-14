"""
User Repository单元测试
"""
import pytest
from decimal import Decimal
from biz.user.repo.user_repo import UserRepository


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.db
class TestUserRepository:
    """用户Repository测试"""

    async def test_create_and_get_user(self, session_factory, sample_user_data):
        """测试创建和获取用户"""
        repo = UserRepository(session_factory)

        # 创建用户
        user = await repo.create_user(sample_user_data)
        assert user is not None
        assert user["id"] == sample_user_data["id"]
        assert user["username"] == sample_user_data["username"]
        assert float(user["balance"]) == float(sample_user_data["balance"])

        # 获取用户
        fetched_user = await repo.get_user_in_chat(
            sample_user_data["id"],
            sample_user_data["chat_id"]
        )
        assert fetched_user is not None
        assert fetched_user["id"] == sample_user_data["id"]

        # 清理
        await repo.delete_user(sample_user_data["id"], sample_user_data["chat_id"])

    async def test_add_balance(self, session_factory, sample_user_data):
        """测试增加余额"""
        repo = UserRepository(session_factory)

        # 创建用户
        await repo.create_user(sample_user_data)

        # 增加余额
        updated_user = await repo.add_balance(
            sample_user_data["id"],
            sample_user_data["chat_id"],
            Decimal("500.00")
        )

        assert updated_user is not None
        expected_balance = float(sample_user_data["balance"]) + 500.00
        assert abs(float(updated_user["balance"]) - expected_balance) < 0.01

        # 清理
        await repo.delete_user(sample_user_data["id"], sample_user_data["chat_id"])

    async def test_subtract_balance(self, session_factory, sample_user_data):
        """测试减少余额"""
        repo = UserRepository(session_factory)

        # 创建用户
        await repo.create_user(sample_user_data)

        # 减少余额
        updated_user = await repo.subtract_balance(
            sample_user_data["id"],
            sample_user_data["chat_id"],
            Decimal("200.00")
        )

        assert updated_user is not None
        expected_balance = float(sample_user_data["balance"]) - 200.00
        assert abs(float(updated_user["balance"]) - expected_balance) < 0.01

        # 清理
        await repo.delete_user(sample_user_data["id"], sample_user_data["chat_id"])

    async def test_subtract_balance_insufficient(self, session_factory, sample_user_data):
        """测试余额不足时减少余额"""
        repo = UserRepository(session_factory)

        # 创建用户
        await repo.create_user(sample_user_data)

        # 尝试减少超过余额的金额
        result = await repo.subtract_balance(
            sample_user_data["id"],
            sample_user_data["chat_id"],
            Decimal("2000.00")  # 超过1000.00
        )

        # 应该返回None（余额不足）
        assert result is None

        # 清理
        await repo.delete_user(sample_user_data["id"], sample_user_data["chat_id"])

    async def test_update_rebate_ratio(self, session_factory, sample_user_data):
        """测试更新回水比例"""
        repo = UserRepository(session_factory)

        # 创建用户
        await repo.create_user(sample_user_data)

        # 更新回水比例
        new_ratio = Decimal("0.05")
        updated_user = await repo.update_rebate_ratio(
            sample_user_data["id"],
            sample_user_data["chat_id"],
            new_ratio
        )

        assert updated_user is not None
        assert abs(float(updated_user["rebate_ratio"]) - 0.05) < 0.001

        # 清理
        await repo.delete_user(sample_user_data["id"], sample_user_data["chat_id"])

    async def test_user_exists(self, session_factory, sample_user_data):
        """测试检查用户是否存在"""
        repo = UserRepository(session_factory)

        # 用户不存在
        exists_before = await repo.exists(
            sample_user_data["id"],
            sample_user_data["chat_id"]
        )
        assert not exists_before

        # 创建用户
        await repo.create_user(sample_user_data)

        # 用户存在
        exists_after = await repo.exists(
            sample_user_data["id"],
            sample_user_data["chat_id"]
        )
        assert exists_after

        # 清理
        await repo.delete_user(sample_user_data["id"], sample_user_data["chat_id"])
