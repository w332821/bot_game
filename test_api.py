#!/usr/bin/env python3
"""API 端点测试脚本"""

import requests
import json

BASE_URL = "http://localhost:3003"

def test_endpoint(name, url, method="GET", data=None):
    """测试一个端点"""
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"URL: {url}")
    print(f"方法: {method}")
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
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 失败: {r.status_code}")
            print(r.text)
    except Exception as e:
        print(f"❌ 错误: {e}")

def main():
    print("\n" + "="*60)
    print("Game Bot API 端点测试")
    print("="*60)

    # 1. 健康检查
    test_endpoint("健康检查", f"{BASE_URL}/health")

    # 2. 根端点
    test_endpoint("根端点", f"{BASE_URL}/")

    # 3. 首页统计
    test_endpoint("首页统计", f"{BASE_URL}/api/home/dashboard")

    # 4. 开奖历史 (Lucky8)
    test_endpoint("开奖历史 (Lucky8)", f"{BASE_URL}/api/draw/history?game_type=lucky8&limit=5")

    # 5. 开奖历史 (Liuhecai)
    test_endpoint("开奖历史 (Liuhecai)", f"{BASE_URL}/api/draw/history?game_type=liuhecai&limit=5")

    # 6. 会员列表
    test_endpoint("会员列表", f"{BASE_URL}/api/members?page=1&page_size=10")

    # 7. 代理列表
    test_endpoint("代理列表", f"{BASE_URL}/api/agents?page=1&page_size=10")

    print("\n" + "="*60)
    print("测试完成")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
