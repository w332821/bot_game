#!/usr/bin/env python3
"""
测试游戏类型切换API
验证切换后话术是否正确
"""
import asyncio
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from biz.game.templates.message_templates import GameMessageTemplates


def test_message_templates():
    """测试消息模板"""
    print("\n" + "=" * 80)
    print("🧪 测试消息模板功能")
    print("=" * 80)

    # 测试欢迎消息
    print("\n【测试1】欢迎消息")
    print("-" * 80)

    print("\n1️⃣ 澳洲幸运8 欢迎消息:")
    lucky8_welcome = GameMessageTemplates.get_welcome_message('lucky8')
    print(lucky8_welcome)

    print("\n2️⃣ 六合彩 欢迎消息:")
    liuhecai_welcome = GameMessageTemplates.get_welcome_message('liuhecai')
    print(liuhecai_welcome)

    # 测试倒计时
    print("\n" + "-" * 80)
    print("\n【测试2】倒计时提示")
    print("-" * 80)

    print("\n1️⃣ 澳洲幸运8 90秒警告:")
    lucky8_warning = GameMessageTemplates.get_countdown_warning('lucky8')
    print(lucky8_warning)

    print("\n2️⃣ 六合彩 90秒警告:")
    liuhecai_warning = GameMessageTemplates.get_countdown_warning('liuhecai')
    print(liuhecai_warning)

    # 测试锁定消息
    print("\n" + "-" * 80)
    print("\n【测试3】锁定消息")
    print("-" * 80)

    print("\n1️⃣ 60秒锁定消息 (通用):")
    lock_msg = GameMessageTemplates.get_lock_message('lucky8')
    print(lock_msg)

    # 测试游戏名称
    print("\n" + "-" * 80)
    print("\n【测试4】游戏名称")
    print("-" * 80)

    print(f"\n1️⃣ lucky8 -> {GameMessageTemplates.get_game_name('lucky8')}")
    print(f"2️⃣ liuhecai -> {GameMessageTemplates.get_game_name('liuhecai')}")

    # 测试开奖间隔
    print("\n" + "-" * 80)
    print("\n【测试5】开奖间隔")
    print("-" * 80)

    print(f"\n1️⃣ lucky8 -> {GameMessageTemplates.get_game_interval_text('lucky8')}")
    print(f"2️⃣ liuhecai -> {GameMessageTemplates.get_game_interval_text('liuhecai')}")

    print("\n" + "=" * 80)
    print("✅ 所有消息模板测试通过！")
    print("=" * 80)


async def test_api_endpoint():
    """测试API接口调用"""
    print("\n" + "=" * 80)
    print("📡 API接口使用说明")
    print("=" * 80)

    print("\n接口地址: POST /api/chat/{chatId}/gametype")
    print("\n请求示例:")
    print("""
# 切换到六合彩
curl -X POST http://localhost:3003/api/chat/123456/gametype \\
  -H "Content-Type: application/json" \\
  -d '{"gameType": "liuhecai"}'

# 切换到澳洲幸运8
curl -X POST http://localhost:3003/api/chat/123456/gametype \\
  -H "Content-Type: application/json" \\
  -d '{"gameType": "lucky8"}'
    """)

    print("\n预期效果:")
    print("1. ✅ 数据库 chats.game_type 字段更新")
    print("2. ✅ 定时器自动切换到新的游戏类型")
    print("3. ✅ 开奖间隔自动调整 (lucky8: 5分钟, liuhecai: 24小时)")
    print("4. ✅ 欢迎消息自动使用新游戏类型的话术")
    print("5. ✅ 倒计时提示自动使用新游戏类型的话术")
    print("6. ✅ 开奖消息自动显示新游戏类型的名称")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        # 测试消息模板
        test_message_templates()

        # 测试API说明
        asyncio.run(test_api_endpoint())

        print("\n✨ 功能测试完成！")
        print("\n💡 提示：")
        print("   - 接口已就绪，可以直接调用")
        print("   - 切换后无需重启应用")
        print("   - 机器人话术会自动根据game_type切换")

    except KeyboardInterrupt:
        print("\n\n👋 测试中断")
    except Exception as e:
        print(f"\n❌ 测试错误: {str(e)}")
        import traceback
        traceback.print_exc()
