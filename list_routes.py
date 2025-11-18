#!/usr/bin/env python3
"""列出所有可用的API路由"""

import requests
import json

BASE_URL = "http://localhost:3003"

def main():
    print("\n" + "="*80)
    print("Game Bot API 可用路由")
    print("="*80 + "\n")

    try:
        r = requests.get(f"{BASE_URL}/openapi.json")
        openapi = r.json()

        paths = openapi.get('paths', {})

        print(f"总共 {len(paths)} 个端点:\n")

        for path, methods in sorted(paths.items()):
            print(f"\n路径: {path}")
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    summary = details.get('summary', '无描述')
                    print(f"  - {method.upper():6s} {summary}")

    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
