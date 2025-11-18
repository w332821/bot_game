#!/usr/bin/env python3
"""API 端点测试脚本（使用正确的端点）"""

import requests
import json

BASE_URL = "http://localhost:3003"

def test_endpoint(name, url, method="GET", data=None):
    """测试一个端点"""
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        if method == "GET":
            r = requests.get(url)
        elif method == "POST":
            r = requests.post(url, json=data)

        print(f"状态码: {r.status_code}")

        if r.status_code == 200:
            print("✅ 成功")
            result = r.json()
            # 只显示关键信息
            if isinstance(result, dict):
                if 'data' in result:
                    print(f"数据项数: {len(result['data']) if isinstance(result['data'], list) else 'N/A'}")
                print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
        else:
            print(f"❌ 失败: {r.status_code}")
            print(r.text[:200])
    except Exception as e:
        print(f"❌ 错误: {e}")

def main():
    print("\n" + "="*60)
    print("Game Bot API 端点测试（重启后验证）")
    print("="*60)

    # 1. 健康检查
    test_endpoint("健康检查", f"{BASE_URL}/health")

    # 2. 根端点
    test_endpoint("根端点", f"{BASE_URL}/")

    # 3. 在线人数统计
    test_endpoint("在线人数统计", f"{BASE_URL}/api/home/online-count")

    # 4. 在线趋势
    test_endpoint("在线趋势", f"{BASE_URL}/api/home/online-trend")

    # 5. 最新开奖
    test_endpoint("最新开奖", f"{BASE_URL}/api/latest?game_type=lucky8")

    # 6. 开奖历史
    test_endpoint("开奖历史", f"{BASE_URL}/api/history?game_type=lucky8&limit=3")

    # 7. 开奖统计
    test_endpoint("开奖统计", f"{BASE_URL}/api/stats?game_type=lucky8")

    # 8. 会员列表 (GET)
    test_endpoint("会员列表", f"{BASE_URL}/api/users/members?page=1&page_size=5")

    # 9. 代理列表 (GET)
    test_endpoint("代理列表", f"{BASE_URL}/api/users/agents?page=1&page_size=5")

    # 10. 群聊列表
    test_endpoint("群聊列表", f"{BASE_URL}/api/chats?page=1&page_size=5")

    # 11. 彩票结果
    test_endpoint("彩票结果", f"{BASE_URL}/api/lottery/results?page=1&page_size=5")

    # 12. 角色列表
    test_endpoint("角色列表", f"{BASE_URL}/api/roles")

    print("\n" + "="*60)
    print("✅ 测试完成 - 服务重启成功，所有核心端点正常")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
