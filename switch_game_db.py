#!/usr/bin/env python3
"""
直接通过数据库切换游戏类型
"""
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine, text
from base.config import get_config

def switch_game_type(chat_id: str, new_game_type: str):
    """切换游戏类型"""
    # 获取配置
    config = get_config()
    db_uri = config.sync_database_uri

    print(f"\n📊 数据库连接: {db_uri.split('@')[1] if '@' in db_uri else db_uri}")

    # 创建同步引擎
    engine = create_engine(db_uri)

    try:
        with engine.connect() as conn:
            # 1. 查询当前状态
            print(f"\n【步骤1】查询当前游戏类型")
            query = text("SELECT id, name, game_type FROM chats WHERE id = :chat_id")
            result = conn.execute(query, {"chat_id": chat_id})
            row = result.fetchone()

            if not row:
                print(f"❌ 群聊 {chat_id} 不存在")
                return False

            current_game = row[2] if len(row) > 2 else 'lucky8'
            print(f"   群聊ID: {row[0]}")
            print(f"   群聊名: {row[1]}")
            print(f"   当前游戏类型: {current_game}")

            # 2. 更新游戏类型
            print(f"\n【步骤2】更新游戏类型为: {new_game_type}")
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

            print(f"✅ 数据库已更新")

            # 3. 验证更新
            print(f"\n【步骤3】验证更新结果")
            result = conn.execute(query, {"chat_id": chat_id})
            row = result.fetchone()
            final_game = row[2] if len(row) > 2 else 'unknown'

            if final_game == new_game_type:
                print(f"✅ 验证成功！游戏类型已切换为: {final_game}")

                print(f"\n" + "=" * 60)
                if new_game_type == "liuhecai":
                    print("📝 六合彩游戏说明:")
                    print("   - 开奖间隔: 24小时")
                    print("   - 支持玩法: 特码 (tema)")
                    print("   - 特码范围: 1-49")
                    print("   - 下注示例: 特码8/100 (下注特码8，金额100)")
                    print("   - 赔率: 1:40")
                else:
                    print("📝 澳洲幸运8游戏说明:")
                    print("   - 开奖间隔: 5分钟")
                    print("   - 支持玩法: 番、正、念、角、通")
                    print("   - 下注示例: 3番200 (下注番数3，金额200)")

                print(f"\n⚠️  重要提示:")
                print("   1. 请重启应用使定时器生效")
                print("   2. 或者等待下次webhook事件自动同步")
                print("=" * 60)
                return True
            else:
                print(f"❌ 验证失败！当前游戏类型: {final_game}")
                return False

    except Exception as e:
        print(f"❌ 操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 游戏类型切换工具（数据库直连）")
    print("=" * 60)

    # 群聊ID
    CHAT_ID = "69114d5e2443a3e5f5fddc30"

    # 提示用户选择
    print(f"\n当前群聊ID: {CHAT_ID}")
    print("\n请选择要切换的游戏类型:")
    print("  1) lucky8 (澳洲幸运8 - 5分钟开奖)")
    print("  2) liuhecai (六合彩 - 24小时开奖)")
    print()

    choice = input("请选择 (1 或 2): ").strip()

    if choice == "1":
        new_game = "lucky8"
    elif choice == "2":
        new_game = "liuhecai"
    else:
        print("❌ 无效选择")
        exit(1)

    # 执行切换
    success = switch_game_type(CHAT_ID, new_game)

    if success:
        print(f"\n🎉 游戏类型切换完成！")
    else:
        print(f"\n❌ 游戏类型切换失败")

    print()
