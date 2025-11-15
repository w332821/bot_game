"""
初始化赔率配置脚本
插入所有游戏类型的默认赔率配置
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from biz.containers import Container


async def init_odds():
    """初始化赔率配置"""
    container = Container()
    container.config.from_yaml("config.yaml")
    container.wire(modules=[__name__])

    odds_service = container.odds_service()

    print("🎲 初始化赔率配置...")
    print("=" * 60)

    # 澳洲幸运8赔率配置
    lucky8_odds = [
        {
            "bet_type": "fan",
            "odds": Decimal("3.0"),
            "description": "番：单号投注",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "lucky8"
        },
        {
            "bet_type": "zheng",
            "odds": Decimal("2.0"),
            "description": "正：对立号投注",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "lucky8"
        },
        {
            "bet_type": "nian",
            "odds": Decimal("2.0"),
            "description": "念：两个番数",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "lucky8"
        },
        {
            "bet_type": "jiao",
            "odds": Decimal("1.5"),
            "description": "角：相邻番数",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "lucky8"
        },
        {
            "bet_type": "tong",
            "odds": Decimal("2.0"),
            "description": "通/借：首位赢，末位输",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "lucky8"
        },
        {
            "bet_type": "zheng_jin",
            "odds": Decimal("2.0"),
            "description": "正（禁号）：指定禁号",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "lucky8"
        },
        {
            "bet_type": "zhong",
            "odds": Decimal("1.333"),
            "description": "三码（中）：覆盖3个结果号",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "lucky8"
        },
        {
            "bet_type": "odd",
            "odds": Decimal("2.0"),
            "description": "单：奇数投注",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "lucky8"
        },
        {
            "bet_type": "even",
            "odds": Decimal("2.0"),
            "description": "双：偶数投注",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "lucky8"
        },
        {
            "bet_type": "tema_lucky8",
            "odds": Decimal("10.0"),
            "description": "澳8特码：1-20号",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("5000.00"),
            "period_max": Decimal("20000.00"),
            "game_type": "lucky8",
            "tema_odds": None  # 可以后续配置每个号码的不同赔率
        }
    ]

    # 六合彩赔率配置
    liuhecai_odds = [
        {
            "bet_type": "fan",
            "odds": Decimal("3.0"),
            "description": "番：单号投注",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "liuhecai"
        },
        {
            "bet_type": "zheng",
            "odds": Decimal("2.0"),
            "description": "正：对立号投注",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "liuhecai"
        },
        {
            "bet_type": "nian",
            "odds": Decimal("2.0"),
            "description": "念：两个番数",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "liuhecai"
        },
        {
            "bet_type": "jiao",
            "odds": Decimal("1.5"),
            "description": "角：相邻番数",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "liuhecai"
        },
        {
            "bet_type": "tong",
            "odds": Decimal("2.0"),
            "description": "通/借：首位赢，末位输",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "liuhecai"
        },
        {
            "bet_type": "zheng_jin",
            "odds": Decimal("2.0"),
            "description": "正（禁号）：指定禁号",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "liuhecai"
        },
        {
            "bet_type": "zhong",
            "odds": Decimal("1.333"),
            "description": "三码（中）：覆盖3个结果号",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "liuhecai"
        },
        {
            "bet_type": "odd",
            "odds": Decimal("2.0"),
            "description": "单：奇数投注",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "liuhecai"
        },
        {
            "bet_type": "even",
            "odds": Decimal("2.0"),
            "description": "双：偶数投注",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("10000.00"),
            "period_max": Decimal("50000.00"),
            "game_type": "liuhecai"
        },
        {
            "bet_type": "tema_liuhecai",
            "odds": Decimal("40.0"),
            "description": "六合彩特码：1-49号",
            "min_bet": Decimal("10.00"),
            "max_bet": Decimal("2000.00"),
            "period_max": Decimal("10000.00"),
            "game_type": "liuhecai",
            "tema_odds": None  # 可以后续配置每个号码的不同赔率
        }
    ]

    # 合并所有配置
    all_odds = lucky8_odds + liuhecai_odds

    success_count = 0
    skip_count = 0
    error_count = 0

    for odds_config in all_odds:
        bet_type = odds_config["bet_type"]
        game_type = odds_config["game_type"]

        # 检查是否已存在
        existing = await odds_service.get_odds(bet_type, game_type)
        if existing:
            print(f"⏭️  跳过（已存在）: {bet_type} ({game_type})")
            skip_count += 1
            continue

        # 创建配置
        result = await odds_service.create_odds(**odds_config)

        if result["success"]:
            print(f"✅ 创建成功: {bet_type} ({game_type}) - {odds_config['description']} - 赔率 {odds_config['odds']}")
            success_count += 1
        else:
            print(f"❌ 创建失败: {bet_type} ({game_type}) - {result['error']}")
            error_count += 1

    print("=" * 60)
    print(f"📊 初始化完成:")
    print(f"   ✅ 成功创建: {success_count} 条")
    print(f"   ⏭️  跳过: {skip_count} 条")
    print(f"   ❌ 失败: {error_count} 条")
    print(f"   📝 总计: {len(all_odds)} 条")


if __name__ == "__main__":
    asyncio.run(init_odds())
