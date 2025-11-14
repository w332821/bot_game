#!/usr/bin/env python3
"""
测试所有关键模块的导入
确保没有运行时导入错误
"""

import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试所有关键导入"""
    print("="*60)
    print("测试 Python Bot 模块导入")
    print("="*60 + "\n")

    errors = []

    # 1. 测试 BotApiClient
    try:
        from external.bot_api_client import BotApiClient, get_bot_api_client
        print("✅ external.bot_api_client 导入成功")

        # 检查方法存在
        client = BotApiClient()
        assert hasattr(client, '_generate_signature'), "缺少 _generate_signature 方法"
        assert hasattr(client, '_get_headers'), "缺少 _get_headers 方法"
        assert hasattr(client, 'send_message'), "缺少 send_message 方法"
        assert hasattr(client, 'join_chat'), "缺少 join_chat 方法"
        assert hasattr(client, 'send_image'), "缺少 send_image 方法"
        print("  ✅ BotApiClient 所有方法存在")

    except Exception as e:
        errors.append(f"BotApiClient: {e}")
        print(f"❌ external.bot_api_client 导入失败: {e}")

    # 2. 测试 ChatRepository
    try:
        from biz.chat.repo.chat_repo import ChatRepository
        print("✅ ChatRepository 导入成功")

        # 检查方法存在（不实例化，只检查类）
        assert hasattr(ChatRepository, 'get_by_id'), "缺少 get_by_id 方法"
        assert hasattr(ChatRepository, 'get_chat'), "缺少 get_chat 方法"
        assert hasattr(ChatRepository, 'create_chat'), "缺少 create_chat 方法"
        assert hasattr(ChatRepository, 'update_chat'), "缺少 update_chat 方法"
        print("  ✅ ChatRepository 所有方法存在")

    except Exception as e:
        errors.append(f"ChatRepository: {e}")
        print(f"❌ ChatRepository 导入失败: {e}")

    # 3. 测试 UserRepository
    try:
        from biz.user.repo.user_repo import UserRepository
        print("✅ UserRepository 导入成功")

        assert hasattr(UserRepository, 'get_user_in_chat'), "缺少 get_user_in_chat 方法"
        assert hasattr(UserRepository, 'create_user'), "缺少 create_user 方法"
        assert hasattr(UserRepository, 'add_balance'), "缺少 add_balance 方法"
        assert hasattr(UserRepository, 'subtract_balance'), "缺少 subtract_balance 方法"
        print("  ✅ UserRepository 所有方法存在")

    except Exception as e:
        errors.append(f"UserRepository: {e}")
        print(f"❌ UserRepository 导入失败: {e}")

    # 4. 测试 GameService
    try:
        from biz.game.service.game_service import GameService
        print("✅ GameService 导入成功")

        assert hasattr(GameService, 'handle_bet_message'), "缺少 handle_bet_message 方法"
        assert hasattr(GameService, 'handle_query_balance'), "缺少 handle_query_balance 方法"
        assert hasattr(GameService, 'execute_draw'), "缺少 execute_draw 方法"
        print("  ✅ GameService 所有方法存在")

    except Exception as e:
        errors.append(f"GameService: {e}")
        print(f"❌ GameService 导入失败: {e}")

    # 5. 测试 game_logic
    try:
        from biz.game.logic import game_logic
        print("✅ game_logic 导入成功")

        assert hasattr(game_logic, 'parse_bets'), "缺少 parse_bets 函数"
        assert hasattr(game_logic, 'validate_bet'), "缺少 validate_bet 函数"
        print("  ✅ game_logic 所有函数存在")

    except Exception as e:
        errors.append(f"game_logic: {e}")
        print(f"❌ game_logic 导入失败: {e}")

    # 6. 测试 webhook_api
    try:
        from biz.game.webhook.webhook_api import router
        print("✅ webhook_api 导入成功")

    except Exception as e:
        errors.append(f"webhook_api: {e}")
        print(f"❌ webhook_api 导入失败: {e}")

    # 汇总
    print("\n" + "="*60)
    if errors:
        print(f"❌ 发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ 所有模块导入成功，无错误！")
        return True


if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
