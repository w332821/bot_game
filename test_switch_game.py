#!/usr/bin/env python3
"""
测试切换游戏类型的脚本
"""
import requests
import json

# 配置
CHAT_ID = "69114d5e2443a3e5f5fddc30"  # 你的群聊ID
API_BASE = "http://127.0.0.1:3003"

def switch_game_type(game_type):
    """切换游戏类型"""
    url = f"{API_BASE}/api/v1/chat/{CHAT_ID}/gametype"
    data = {"gameType": game_type}

    print(f"\n📡 切换游戏类型到: {game_type}")
    print(f"   URL: {url}")
    print(f"   Data: {json.dumps(data)}")

    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"   状态码: {response.status_code}")

        result = response.json()
        print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

        if result.get('success'):
            print(f"✅ 成功切换到 {game_type}")

            # 自动通知bot-server同步
            sync_url = f"{API_BASE}/api/sync-gametype"
            sync_data = {
                "chatId": CHAT_ID,
                "gameType": game_type,
                "oldGameType": "lucky8" if game_type == "liuhecai" else "liuhecai"
            }

            print(f"\n📡 通知bot-server同步...")
            sync_response = requests.post(sync_url, json=sync_data, timeout=10)
            sync_result = sync_response.json()
            print(f"   同步响应: {json.dumps(sync_result, ensure_ascii=False, indent=2)}")

            if sync_result.get('success'):
                print(f"✅ 定时器已同步")
            else:
                print(f"❌ 定时器同步失败: {sync_result.get('error')}")
        else:
            print(f"❌ 切换失败: {result.get('error')}")

        return result

    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return None

def get_chat_info():
    """获取群聊信息"""
    url = f"{API_BASE}/api/v1/chat/{CHAT_ID}"

    print(f"\n📡 获取群聊信息...")
    try:
        response = requests.get(url, timeout=10)
        result = response.json()

        if result.get('success'):
            chat = result.get('chat', {})
            print(f"✅ 群聊信息:")
            print(f"   ID: {chat.get('id')}")
            print(f"   名称: {chat.get('name')}")
            print(f"   游戏类型: {chat.get('game_type')}")
            return chat
        else:
            print(f"❌ 获取失败: {result.get('error')}")
            return None

    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 游戏类型切换测试")
    print("=" * 60)

    # 1. 查看当前状态
    print("\n【步骤1】查看当前游戏类型")
    chat = get_chat_info()

    if not chat:
        print("\n❌ 无法获取群聊信息，请检查:")
        print("   1. API服务是否运行在 http://127.0.0.1:3003")
        print("   2. 群聊ID是否正确")
        exit(1)

    current_game = chat.get('game_type', 'lucky8')
    print(f"\n当前游戏类型: {current_game}")

    # 2. 切换到另一个游戏
    print("\n【步骤2】切换游戏类型")
    new_game = "liuhecai" if current_game == "lucky8" else "lucky8"
    switch_game_type(new_game)

    # 3. 验证切换结果
    print("\n【步骤3】验证切换结果")
    chat = get_chat_info()

    if chat and chat.get('game_type') == new_game:
        print(f"\n🎉 成功！游戏类型已切换为: {new_game}")

        if new_game == "liuhecai":
            print("\n📝 六合彩游戏说明:")
            print("   - 开奖间隔: 24小时")
            print("   - 支持玩法: 特码 (tema)")
            print("   - 下注示例: 特码8/100")
        else:
            print("\n📝 澳洲幸运8游戏说明:")
            print("   - 开奖间隔: 5分钟")
            print("   - 支持玩法: 番、正、念、角、通")
            print("   - 下注示例: 3番200")
    else:
        print(f"\n❌ 切换失败！当前游戏类型仍为: {chat.get('game_type') if chat else '未知'}")

    print("\n" + "=" * 60)
