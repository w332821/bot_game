#!/usr/bin/env python3
"""
完整的Day 1测试套件
测试所有Repository和Service层的核心方法
"""
import asyncio
import sys
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import json

# 数据库配置
DATABASE_URL = "mysql+asyncmy://root:123456@localhost:3306/game_bot"

# 导入所有Repository
from biz.user.repo.user_repo import UserRepository
from biz.bet.repo.bet_repo import BetRepository
from biz.chat.repo.chat_repo import ChatRepository
from biz.admin.repo.admin_repo import AdminRepository
from biz.draw.repo.draw_repo import DrawRepository
from biz.odds.repo.odds_repo import OddsRepository

# 导入所有Service
from biz.user.service.user_service import UserService
from biz.admin.service.admin_service import AdminService

# 颜色输出
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")

def print_section(title):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


class TestResults:
    """测试结果记录器"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_pass(self, test_name):
        self.total += 1
        self.passed += 1
        print_success(f"{test_name}")

    def add_fail(self, test_name, error):
        self.total += 1
        self.failed += 1
        self.errors.append((test_name, error))
        print_error(f"{test_name}: {error}")

    def summary(self):
        print_section("测试总结")
        print(f"总计: {self.total} 个测试")
        print(f"{GREEN}通过: {self.passed}{RESET}")
        if self.failed > 0:
            print(f"{RED}失败: {self.failed}{RESET}")
            print(f"\n{RED}失败详情:{RESET}")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")

        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"\n成功率: {success_rate:.1f}%")

        if self.failed == 0:
            print(f"\n{GREEN}🎉 所有测试通过！{RESET}")
            return 0
        else:
            print(f"\n{RED}⚠️  有{self.failed}个测试失败{RESET}")
            return 1


async def test_user_repository(session_factory, results: TestResults):
    """测试User Repository"""
    print_section("测试 User Repository")

    repo = UserRepository(session_factory)
    test_user_id = "test_user_comprehensive"
    test_chat_id = "test_chat_comprehensive"

    try:
        # 清理可能存在的测试数据
        await repo.delete_user(test_user_id, test_chat_id)

        # Test 1: 创建用户
        user_data = {
            "id": test_user_id,
            "username": "综合测试用户",
            "chat_id": test_chat_id,
            "balance": Decimal("1000.00"),
            "score": 100,
            "rebate_ratio": Decimal("0.02"),
            "status": "活跃",
            "role": "normal",
            "created_by": "admin"
        }
        user = await repo.create_user(user_data)
        if user and user["id"] == test_user_id:
            results.add_pass("User Repository: create_user")
        else:
            results.add_fail("User Repository: create_user", "创建失败")

        # Test 2: 获取用户
        user = await repo.get_user_in_chat(test_user_id, test_chat_id)
        if user and user["username"] == "综合测试用户":
            results.add_pass("User Repository: get_user_in_chat")
        else:
            results.add_fail("User Repository: get_user_in_chat", "获取失败")

        # Test 3: 增加余额
        updated_user = await repo.add_balance(test_user_id, test_chat_id, Decimal("500.00"))
        if updated_user and float(updated_user["balance"]) == 1500.00:
            results.add_pass("User Repository: add_balance")
        else:
            results.add_fail("User Repository: add_balance", f"余额错误: {updated_user['balance'] if updated_user else 'None'}")

        # Test 4: 减少余额
        updated_user = await repo.subtract_balance(test_user_id, test_chat_id, Decimal("200.00"))
        if updated_user and float(updated_user["balance"]) == 1300.00:
            results.add_pass("User Repository: subtract_balance")
        else:
            results.add_fail("User Repository: subtract_balance", f"余额错误: {updated_user['balance'] if updated_user else 'None'}")

        # Test 5: 余额不足验证
        result = await repo.subtract_balance(test_user_id, test_chat_id, Decimal("2000.00"))
        if result is None:
            results.add_pass("User Repository: subtract_balance (insufficient funds)")
        else:
            results.add_fail("User Repository: subtract_balance (insufficient funds)", "应该返回None")

        # Test 6: 更新回水比例
        updated_user = await repo.update_rebate_ratio(test_user_id, test_chat_id, Decimal("0.05"))
        if updated_user and abs(float(updated_user["rebate_ratio"]) - 0.05) < 0.001:
            results.add_pass("User Repository: update_rebate_ratio")
        else:
            results.add_fail("User Repository: update_rebate_ratio", "回水比例错误")

        # Test 7: 检查用户存在性
        exists = await repo.exists(test_user_id, test_chat_id)
        if exists:
            results.add_pass("User Repository: exists")
        else:
            results.add_fail("User Repository: exists", "应该返回True")

        # Test 8: 删除用户
        deleted = await repo.delete_user(test_user_id, test_chat_id)
        if deleted:
            results.add_pass("User Repository: delete_user")
        else:
            results.add_fail("User Repository: delete_user", "删除失败")

    except Exception as e:
        results.add_fail("User Repository: General", str(e))
        import traceback
        traceback.print_exc()


async def test_user_service(session_factory, results: TestResults):
    """测试User Service"""
    print_section("测试 User Service")

    repo = UserRepository(session_factory)
    service = UserService(repo)
    test_user_id = "test_service_user"
    test_chat_id = "test_service_chat"

    try:
        # 清理
        await repo.delete_user(test_user_id, test_chat_id)

        # Test 1: 获取或创建用户
        user = await service.get_or_create_user(test_user_id, "服务测试用户", test_chat_id)
        if user and user["id"] == test_user_id:
            results.add_pass("User Service: get_or_create_user")
        else:
            results.add_fail("User Service: get_or_create_user", "创建失败")

        # Test 2: 充值
        result = await service.add_credit(test_user_id, test_chat_id, Decimal("500.00"), "admin", "测试充值")
        if result["success"] and result["new_balance"] == Decimal("500.00"):
            results.add_pass("User Service: add_credit")
        else:
            results.add_fail("User Service: add_credit", "充值失败")

        # Test 3: 扣款
        result = await service.remove_credit(test_user_id, test_chat_id, Decimal("200.00"), "admin", "测试扣款")
        if result["success"] and result["new_balance"] == Decimal("300.00"):
            results.add_pass("User Service: remove_credit")
        else:
            results.add_fail("User Service: remove_credit", "扣款失败")

        # Test 4: 余额不足验证
        try:
            await service.remove_credit(test_user_id, test_chat_id, Decimal("1000.00"), "admin", "测试余额不足")
            results.add_fail("User Service: remove_credit (insufficient)", "应该抛出异常")
        except ValueError as e:
            if "余额不足" in str(e):
                results.add_pass("User Service: remove_credit (insufficient validation)")
            else:
                results.add_fail("User Service: remove_credit (insufficient)", f"错误信息不正确: {e}")

        # 清理
        await repo.delete_user(test_user_id, test_chat_id)

    except Exception as e:
        results.add_fail("User Service: General", str(e))
        import traceback
        traceback.print_exc()


async def test_bet_repository(session_factory, results: TestResults):
    """测试Bet Repository"""
    print_section("测试 Bet Repository")

    repo = BetRepository(session_factory)
    test_bet_id = "test_bet_001"

    try:
        # 清理可能存在的测试数据
        async with session_factory() as session:
            from sqlalchemy import text
            await session.execute(text("DELETE FROM bets WHERE id = :id"), {"id": test_bet_id})
            await session.commit()

        # Test 1: 创建投注
        bet_data = {
            "id": test_bet_id,
            "user_id": "test_user",
            "username": "测试用户",
            "chat_id": "test_chat",
            "game_type": "lucky8",
            "lottery_type": "fan",
            "bet_number": 1,
            "bet_amount": Decimal("100.00"),
            "odds": Decimal("3.00"),
            "status": "active",
            "result": "pending",
            "issue": "20250101-001"
        }
        bet = await repo.create_bet(bet_data)
        if bet and bet["id"] == test_bet_id:
            results.add_pass("Bet Repository: create_bet")
        else:
            results.add_fail("Bet Repository: create_bet", "创建失败")

        # Test 2: 获取投注
        bet = await repo.get_bet(test_bet_id)
        if bet and bet["lottery_type"] == "fan":
            results.add_pass("Bet Repository: get_bet")
        else:
            results.add_fail("Bet Repository: get_bet", "获取失败")

        # Test 3: 结算投注
        settled = await repo.settle_bet(test_bet_id, "win", Decimal("200.00"), 1, "01,02,03,04,05,06,07,08")
        if settled:
            results.add_pass("Bet Repository: settle_bet")
        else:
            results.add_fail("Bet Repository: settle_bet", "结算失败")

        # Test 4: 验证结算结果
        bet = await repo.get_bet(test_bet_id)
        if bet and bet["result"] == "win" and float(bet["pnl"]) == 200.00:
            results.add_pass("Bet Repository: settle_bet (verification)")
        else:
            results.add_fail("Bet Repository: settle_bet (verification)", "结算数据错误")

        # 清理（手动删除，因为BetRepository可能没有delete方法）
        async with session_factory() as session:
            from sqlalchemy import text
            await session.execute(text("DELETE FROM bets WHERE id = :id"), {"id": test_bet_id})
            await session.commit()

    except Exception as e:
        results.add_fail("Bet Repository: General", str(e))
        import traceback
        traceback.print_exc()


async def test_chat_repository(session_factory, results: TestResults):
    """测试Chat Repository"""
    print_section("测试 Chat Repository")

    repo = ChatRepository(session_factory)
    test_chat_id = "test_chat_repo_001"

    try:
        # 清理
        await repo.delete_chat(test_chat_id)

        # Test 1: 创建群聊
        chat_data = {
            "id": test_chat_id,
            "name": "测试群聊",
            "game_type": "lucky8",
            "status": "active",
            "member_count": 10
        }
        chat = await repo.create_chat(chat_data)
        if chat and chat["id"] == test_chat_id:
            results.add_pass("Chat Repository: create_chat")
        else:
            results.add_fail("Chat Repository: create_chat", "创建失败")

        # Test 2: 获取群聊
        chat = await repo.get_chat(test_chat_id)
        if chat and chat["name"] == "测试群聊":
            results.add_pass("Chat Repository: get_chat")
        else:
            results.add_fail("Chat Repository: get_chat", "获取失败")

        # Test 3: 更新游戏类型
        updated = await repo.update_game_type(test_chat_id, "liuhecai")
        if updated and updated["game_type"] == "liuhecai":
            results.add_pass("Chat Repository: update_game_type")
        else:
            results.add_fail("Chat Repository: update_game_type", "更新失败")

        # 清理
        await repo.delete_chat(test_chat_id)

    except Exception as e:
        results.add_fail("Chat Repository: General", str(e))
        import traceback
        traceback.print_exc()


async def test_admin_repository(session_factory, results: TestResults):
    """测试Admin Repository"""
    print_section("测试 Admin Repository")

    repo = AdminRepository(session_factory)
    test_admin_id = "test_admin_001"

    try:
        # 清理
        existing = await repo.get_admin_by_username("test_admin_user")
        if existing:
            await repo.delete_admin(existing["id"])

        # Test 1: 创建管理员
        admin_data = {
            "id": test_admin_id,
            "username": "test_admin_user",
            "password": "test_password_123",  # 修改为password而不是password_hash
            "role": "admin",
            "status": "active"
        }
        admin = await repo.create_admin(admin_data)
        if admin and admin["username"] == "test_admin_user":
            results.add_pass("Admin Repository: create_admin")
        else:
            results.add_fail("Admin Repository: create_admin", "创建失败")

        # Test 2: 通过用户名获取管理员
        admin = await repo.get_admin_by_username("test_admin_user")
        if admin and admin["role"] == "admin":
            results.add_pass("Admin Repository: get_admin_by_username")
        else:
            results.add_fail("Admin Repository: get_admin_by_username", "获取失败")

        # 清理
        await repo.delete_admin(test_admin_id)

    except Exception as e:
        results.add_fail("Admin Repository: General", str(e))
        import traceback
        traceback.print_exc()


async def test_draw_repository(session_factory, results: TestResults):
    """测试Draw Repository"""
    print_section("测试 Draw Repository")

    repo = DrawRepository(session_factory)

    try:
        # Test 1: 创建开奖记录
        draw_data = {
            "game_type": "lucky8",
            "issue": "20250101-TEST-001",
            "draw_code": "01,02,03,04,05,06,07,08",
            "draw_number": 1
        }
        draw = await repo.create_draw(draw_data)
        if draw and draw["issue"] == "20250101-TEST-001":
            results.add_pass("Draw Repository: create_draw")
        else:
            results.add_fail("Draw Repository: create_draw", "创建失败")

        # Test 2: 通过期号获取
        draw = await repo.get_draw_by_issue("20250101-TEST-001")
        if draw and draw["draw_number"] == 1:
            results.add_pass("Draw Repository: get_draw_by_issue")
        else:
            results.add_fail("Draw Repository: get_draw_by_issue", "获取失败")

        # Test 3: 获取最新开奖
        latest = await repo.get_latest_draw("lucky8")
        if latest:
            results.add_pass("Draw Repository: get_latest_draw")
        else:
            results.add_fail("Draw Repository: get_latest_draw", "获取失败")

        # 清理
        if draw:
            await repo.delete_draw(draw["id"])

    except Exception as e:
        results.add_fail("Draw Repository: General", str(e))
        import traceback
        traceback.print_exc()


async def test_odds_repository(session_factory, results: TestResults):
    """测试Odds Repository"""
    print_section("测试 Odds Repository")

    repo = OddsRepository(session_factory)
    test_bet_type = "test_fan"

    try:
        # 清理
        existing = await repo.get_odds(test_bet_type)
        if existing:
            await repo.delete_odds(test_bet_type)

        # Test 1: 创建赔率配置
        odds_data = {
            "bet_type": test_bet_type,
            "game_type": "lucky8",
            "odds": Decimal("3.00"),
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("1000.00"),
            "period_max": Decimal("5000.00"),
            "description": "测试番玩法"
        }
        odds = await repo.create_odds(odds_data)
        if odds and odds["bet_type"] == test_bet_type:
            results.add_pass("Odds Repository: create_odds")
        else:
            results.add_fail("Odds Repository: create_odds", "创建失败")

        # Test 2: 获取赔率配置
        odds = await repo.get_odds(test_bet_type)
        if odds and float(odds["odds"]) == 3.00:
            results.add_pass("Odds Repository: get_odds")
        else:
            results.add_fail("Odds Repository: get_odds", "获取失败")

        # Test 3: 更新赔率
        updated = await repo.update_odds(test_bet_type, "lucky8", {"odds": Decimal("3.50")})
        if updated and float(updated["odds"]) == 3.50:
            results.add_pass("Odds Repository: update_odds")
        else:
            results.add_fail("Odds Repository: update_odds", "更新失败")

        # 清理
        await repo.delete_odds(test_bet_type)

    except Exception as e:
        results.add_fail("Odds Repository: General", str(e))
        import traceback
        traceback.print_exc()


async def main():
    """主测试流程"""
    print_section("Day 1 完整测试套件")
    print_info("开始运行所有Repository和Service层测试...\n")

    results = TestResults()

    # 创建数据库连接
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        # 运行所有测试
        await test_user_repository(session_factory, results)
        await test_user_service(session_factory, results)
        await test_bet_repository(session_factory, results)
        await test_chat_repository(session_factory, results)
        await test_admin_repository(session_factory, results)
        await test_draw_repository(session_factory, results)
        await test_odds_repository(session_factory, results)

    finally:
        await engine.dispose()

    # 输出总结
    return results.summary()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
