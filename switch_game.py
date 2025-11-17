#!/usr/bin/env python3
"""
游戏类型切换工具（简单易用版）
"""
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine, text
from base.config import get_config

def list_all_chats():
    """列出所有群聊"""
    config = get_config()
    db_uri = config.sync_database_uri
    engine = create_engine(db_uri)

    try:
        with engine.connect() as conn:
            query = text("""
                SELECT id, name, game_type, status
                FROM chats
                ORDER BY created_at DESC
            """)
            result = conn.execute(query)
            rows = result.fetchall()

            if not rows:
                print("❌ 数据库中没有任何群聊")
                return []

            print("\n" + "=" * 80)
            print("📋 所有群聊列表")
            print("=" * 80)
            print(f"{'序号':<6} {'群聊名称':<20} {'游戏类型':<15} {'状态':<10} {'群聊ID'}")
            print("-" * 80)

            chats = []
            for idx, row in enumerate(rows, 1):
                chat_id = row[0]
                name = row[1]
                game_type = row[2] if row[2] else 'lucky8'
                status = row[3] if row[3] else 'active'

                # 游戏类型显示
                game_display = {
                    'lucky8': '澳洲幸运8 (5分钟)',
                    'liuhecai': '六合彩 (24小时)'
                }.get(game_type, game_type)

                print(f"{idx:<6} {name:<20} {game_display:<15} {status:<10} {chat_id}")
                chats.append({
                    'index': idx,
                    'id': chat_id,
                    'name': name,
                    'game_type': game_type,
                    'status': status
                })

            print("-" * 80)
            return chats

    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        return []
    finally:
        engine.dispose()

def switch_game_type(chat_id: str, new_game_type: str):
    """切换游戏类型"""
    config = get_config()
    db_uri = config.sync_database_uri
    engine = create_engine(db_uri)

    try:
        with engine.connect() as conn:
            # 更新游戏类型
            update_query = text("""
                UPDATE chats
                SET game_type = :game_type, updated_at = NOW()
                WHERE id = :chat_id
            """)
            conn.execute(update_query, {
                "chat_id": chat_id,
                "game_type": new_game_type
            })
            conn.commit()

            print(f"\n✅ 数据库已更新！")
            return True

    except Exception as e:
        print(f"\n❌ 更新失败: {str(e)}")
        return False
    finally:
        engine.dispose()

def main():
    print("\n" + "=" * 80)
    print("🎮 游戏类型切换工具")
    print("=" * 80)

    # 1. 列出所有群聊
    chats = list_all_chats()

    if not chats:
        print("\n提示：数据库中没有群聊，请先在Telegram中添加机器人到群聊")
        return

    print(f"\n共找到 {len(chats)} 个群聊")

    # 2. 让用户选择群聊
    print("\n" + "=" * 80)
    while True:
        try:
            choice = input("\n请输入要切换游戏类型的群聊序号 (输入 0 退出): ").strip()

            if choice == '0':
                print("👋 已退出")
                return

            idx = int(choice)
            if idx < 1 or idx > len(chats):
                print(f"❌ 无效序号，请输入 1-{len(chats)} 之间的数字")
                continue

            selected_chat = chats[idx - 1]
            break

        except ValueError:
            print("❌ 请输入有效的数字")
            continue

    # 3. 显示当前群聊信息
    print("\n" + "=" * 80)
    print("📌 已选择的群聊:")
    print(f"   名称: {selected_chat['name']}")
    print(f"   ID: {selected_chat['id']}")
    print(f"   当前游戏类型: {selected_chat['game_type']}")

    # 4. 选择新游戏类型
    print("\n请选择要切换到的游戏类型:")
    print("  1) lucky8 (澳洲幸运8)")
    print("     - 开奖间隔: 5分钟")
    print("     - 玩法: 番、正、念、角、通")
    print("     - 示例: 3番200")
    print()
    print("  2) liuhecai (六合彩)")
    print("     - 开奖间隔: 24小时")
    print("     - 玩法: 特码")
    print("     - 示例: 特码8/100")
    print()

    while True:
        game_choice = input("请选择 (1 或 2): ").strip()

        if game_choice == '1':
            new_game = 'lucky8'
            break
        elif game_choice == '2':
            new_game = 'liuhecai'
            break
        else:
            print("❌ 无效选择，请输入 1 或 2")

    # 5. 确认切换
    if new_game == selected_chat['game_type']:
        print(f"\n⚠️  该群聊已经是 {new_game} 类型，无需切换")
        return

    print(f"\n即将切换游戏类型:")
    print(f"   群聊: {selected_chat['name']}")
    print(f"   从: {selected_chat['game_type']}")
    print(f"   到: {new_game}")

    confirm = input("\n确认切换? (y/n): ").strip().lower()

    if confirm != 'y':
        print("❌ 已取消")
        return

    # 6. 执行切换
    print("\n⏳ 正在切换...")
    success = switch_game_type(selected_chat['id'], new_game)

    if success:
        print("\n" + "=" * 80)
        print("🎉 游戏类型切换成功！")
        print("=" * 80)

        if new_game == 'liuhecai':
            print("\n📝 六合彩游戏说明:")
            print("   - 开奖间隔: 24小时")
            print("   - 支持玩法: 特码")
            print("   - 特码范围: 1-49")
            print("   - 赔率: 1:40")
            print("   - 下注示例: 特码8/100 (下注特码8，金额100元)")
        else:
            print("\n📝 澳洲幸运8游戏说明:")
            print("   - 开奖间隔: 5分钟")
            print("   - 支持玩法: 番(1-4)、正、念、角、通")
            print("   - 下注示例:")
            print("     • 3番200 (下注番数3，金额200)")
            print("     • 1正100 (下注正数1，金额100)")
            print("     • 1念2/300 (下注念数1和2，金额300)")

        print("\n⚠️  下一步操作（二选一）:")
        print("   方式1: 重启应用 (推荐)")
        print("          重启后定时器会自动使用新的游戏类型")
        print()
        print("   方式2: 在群里发送任意消息")
        print("          webhook会自动检测并同步游戏类型")
        print("=" * 80)
    else:
        print("\n❌ 切换失败")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已退出")
    except Exception as e:
        print(f"\n❌ 程序错误: {str(e)}")
        import traceback
        traceback.print_exc()
