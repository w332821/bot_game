#!/usr/bin/env python3
"""
数据迁移脚本：从 Node.js JSON 文件迁移到 MySQL 数据库

使用方法：
1. 确保MySQL数据库已创建并配置好
2. 确保已运行 python -m base.init_db 初始化表结构
3. 运行: python migrate_data.py
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, create_engine, select
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入模型
from biz.user.models.model import User
from biz.chat.models.model import Chat
from biz.game.models.model import Bet
from base.database import get_sync_engine


def load_json_data(json_file: str) -> dict:
    """加载Node.js的JSON数据文件"""
    print(f"📂 加载数据文件: {json_file}")

    if not os.path.exists(json_file):
        print(f"❌ 文件不存在: {json_file}")
        return None

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✅ 数据文件加载成功")
    return data


def migrate_chats(session: Session, data: dict):
    """迁移群聊数据"""
    print("\n📋 开始迁移群聊数据...")

    chats_data = data.get('chats', {})
    if not chats_data:
        print("⚠️  没有找到群聊数据")
        return

    count = 0
    for chat_id, chat_info in chats_data.items():
        # 检查是否已存在
        existing = session.exec(
            select(Chat).where(Chat.id == chat_id)
        ).first()

        if existing:
            print(f"  ⏭️  群聊已存在，跳过: {chat_info.get('name')} ({chat_id})")
            continue

        # 创建新群聊记录
        chat = Chat(
            id=chat_id,
            name=chat_info.get('name', 'Unknown'),
            game_type=chat_info.get('gameType', 'lucky8'),
            owner_id=chat_info.get('ownerId')
        )

        session.add(chat)
        count += 1
        print(f"  ✓ 迁移群聊: {chat.name} ({chat_id})")

    session.commit()
    print(f"✅ 群聊迁移完成，共迁移 {count} 个群聊")


def migrate_users(session: Session, data: dict):
    """迁移用户数据"""
    print("\n👥 开始迁移用户数据...")

    users_data = data.get('users', {})
    if not users_data:
        print("⚠️  没有找到用户数据")
        return

    count = 0
    for user_key, user_info in users_data.items():
        user_id = user_info.get('id')
        chat_id = user_info.get('chatId')

        if not user_id or not chat_id:
            print(f"  ⚠️  跳过无效用户数据: {user_key}")
            continue

        # 检查是否已存在
        existing = session.exec(
            select(User).where(User.id == user_id, User.chat_id == chat_id)
        ).first()

        if existing:
            # 更新余额
            existing.balance = float(user_info.get('balance', 1000))
            print(f"  🔄 更新用户: {user_info.get('username')} (余额: {existing.balance})")
        else:
            # 创建新用户
            user = User(
                id=user_id,
                name=user_info.get('username', 'Unknown'),
                chat_id=chat_id,
                balance=float(user_info.get('balance', 1000)),
                rebate_ratio=float(user_info.get('rebateRatio', 0.02))
            )

            session.add(user)
            count += 1
            print(f"  ✓ 迁移用户: {user.name} (余额: {user.balance})")

    session.commit()
    print(f"✅ 用户迁移完成，共迁移 {count} 个新用户")


def migrate_bets(session: Session, data: dict):
    """迁移投注数据"""
    print("\n💰 开始迁移投注数据...")

    bets_data = data.get('bets', [])
    if not bets_data:
        print("⚠️  没有找到投注数据")
        return

    count = 0
    for bet_info in bets_data:
        user_id = bet_info.get('userId')
        chat_id = bet_info.get('chatId')

        if not user_id or not chat_id:
            continue

        # 创建投注记录
        bet = Bet(
            user_id=user_id,
            chat_id=chat_id,
            lottery_type=bet_info.get('lotteryType', 'unknown'),
            bet_number=str(bet_info.get('betNumber', '')),
            bet_amount=float(bet_info.get('betAmount', 0)),
            odds=float(bet_info.get('odds', 0)),
            status=bet_info.get('status', 'pending'),
            result=bet_info.get('result'),
            pnl=float(bet_info.get('pnl', 0)) if bet_info.get('pnl') else None,
            draw_number=bet_info.get('drawNumber'),
            draw_code=bet_info.get('drawCode'),
            issue=bet_info.get('issue')
        )

        session.add(bet)
        count += 1

        if count % 100 == 0:
            print(f"  📊 已迁移 {count} 条投注记录...")

    session.commit()
    print(f"✅ 投注迁移完成，共迁移 {count} 条记录")


def main():
    """主迁移流程"""
    print("=" * 60)
    print("🚀 数据迁移工具：Node.js JSON → MySQL")
    print("=" * 60)

    # 1. 加载JSON数据
    json_file = 'game-bot-master/game-data.json'
    data = load_json_data(json_file)

    if not data:
        print("\n❌ 无法加载数据文件，退出")
        return

    # 显示数据统计
    print(f"\n📊 数据统计:")
    print(f"  - 群聊: {len(data.get('chats', {}))} 个")
    print(f"  - 用户: {len(data.get('users', {}))} 个")
    print(f"  - 投注: {len(data.get('bets', []))} 条")
    print(f"  - 开奖历史: {len(data.get('drawHistory', []))} 条")

    # 确认迁移
    confirm = input("\n⚠️  确认开始迁移？(yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ 取消迁移")
        return

    # 2. 连接数据库
    print("\n🔌 连接数据库...")
    engine = get_sync_engine()

    # 3. 开始迁移
    with Session(engine) as session:
        # 迁移群聊
        migrate_chats(session, data)

        # 迁移用户
        migrate_users(session, data)

        # 迁移投注记录
        migrate_bets(session, data)

    print("\n" + "=" * 60)
    print("✅ 数据迁移完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("  1. 请验证数据是否正确迁移")
    print("  2. 可以备份 game-data.json 文件")
    print("  3. 重启Python应用使新数据生效")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
