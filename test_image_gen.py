#!/usr/bin/env python3
"""
测试图片生成
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.draw_image_generator import get_draw_image_generator

# 测试数据
test_draws = [
    {
        'issue': '20250115001',
        'draw_code': '01,02,03,04,05,06,07,08',
        'special_number': 28,
        'draw_number': 5
    },
    {
        'issue': '20250115002',
        'draw_code': '10,11,12,13,14,15,16,17',
        'special_number': 15,
        'draw_number': 3
    },
    {
        'issue': '20250115003',
        'draw_code': '05,10,15,20,25,30,35,40',
        'special_number': 40,
        'draw_number': 8
    }
]

if __name__ == "__main__":
    print("🖼️  测试图片生成...")

    generator = get_draw_image_generator()

    # 测试澳洲幸运8
    image_path = generator.generate_lucky8_image(
        draws=test_draws,
        save_path='/tmp/test_lucky8.png'
    )

    if image_path and os.path.exists(image_path):
        print(f"✅ 图片生成成功: {image_path}")
        print(f"   文件大小: {os.path.getsize(image_path)} bytes")
        print(f"\n请打开查看图片:")
        print(f"   open {image_path}")
    else:
        print("❌ 图片生成失败")
