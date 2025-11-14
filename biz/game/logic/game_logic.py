"""
澳洲幸运8游戏逻辑（完整Python版本 - 从game-logic.js迁移）

支持的玩法：
- 番：单号投注 (如: "番 3/200" 或 "3番200")
- 正：对立号投注 (如: "正1/200" 或 "1/200")
- 念：两个番数 (如: "1念2/300")
- 角：相邻番数 (如: "角12/200" 或 "12角200")
- 通/借：首位赢，末位输，其它和局 (如: "34通/150" 或 "134通/150" 或 "13借4/120")
- 正（禁号）：指定禁号 (如: "3无4/220")
- 三码（中）：覆盖3个结果号 (如: "123/500")
- 单双：按开奖号码（1-49）奇偶判定 (如: "单200" 或 "双150")
- 澳8特码：澳洲幸运8的特码1-20 (如: "5特20" 或 "2.100" 或 "1.20.10.10")
- 六合彩特码：新澳的特码1-49（在liuhecai游戏中使用）
"""

import re
import logging
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# 正玩法的对立号配置 (1↔3, 2↔4)
ZHENG_PAIRS = {1: 3, 2: 4, 3: 1, 4: 2}


async def get_odds_from_backend(
    odds_service,
    bet_type: str,
    tema_number: Optional[int] = None,
    game_type: Optional[str] = None
) -> Decimal:
    """
    从后台获取赔率

    Args:
        odds_service: OddsService实例
        bet_type: 下注类型
        tema_number: 特码号码（仅当bet_type为tema时使用）
        game_type: 游戏类型（lucky8或liuhecai，用于特码赔率查询）

    Returns:
        Decimal: 赔率值
    """
    # 如果是查询特码赔率
    if bet_type == 'tema':
        # 首先根据游戏类型查询分离的特码配置（如果提供了game_type）
        if game_type:
            tema_type = 'tema_lucky8' if game_type == 'lucky8' else 'tema_liuhecai'
            odds_config = await odds_service.get_odds(tema_type, game_type)
        else:
            odds_config = None

        # 如果没有找到分离的配置，尝试查找旧的统一配置
        if not odds_config:
            odds_config = await odds_service.get_odds('tema', game_type or 'lucky8')

        # 如果还是没有找到，尝试两个分离的配置中的任何一个
        if not odds_config:
            odds_config = (
                await odds_service.get_odds('tema_lucky8', 'lucky8') or
                await odds_service.get_odds('tema_liuhecai', 'liuhecai')
            )
    else:
        odds_config = await odds_service.get_odds(bet_type, game_type or 'lucky8')

    if not odds_config:
        # 如果后台没有配置，使用默认值
        defaults = {
            'fan': Decimal('3.0'),
            'zheng': Decimal('2.0'),
            'nian': Decimal('2.0'),
            'jiao': Decimal('1.5'),
            'tong': Decimal('2.0'),
            'zheng_jin': Decimal('2.0'),
            'zhong': Decimal('1.333'),
            'odd': Decimal('2.0'),
            'even': Decimal('2.0'),
            'tema': Decimal('10.0'),
            'tema_lucky8': Decimal('10.0'),
            'tema_liuhecai': Decimal('10.0')
        }
        return defaults.get(bet_type, Decimal('2.0'))

    # 特码：如果有细分赔率配置，使用对应号码的赔率
    if bet_type in ('tema', 'tema_lucky8', 'tema_liuhecai') and tema_number and odds_config.get('tema_odds'):
        tema_odds = odds_config['tema_odds']
        if isinstance(tema_odds, dict) and str(tema_number) in tema_odds:
            return Decimal(str(tema_odds[str(tema_number)]))

    return odds_config['odds']


async def parse_bets(
    message: str,
    player: str,
    odds_service,
    game_type: str = 'lucky8'
) -> List[Dict[str, Any]]:
    """
    解析下注指令

    Args:
        message: 用户消息
        player: 玩家名称
        odds_service: OddsService实例（用于获取赔率）
        game_type: 游戏类型 ('lucky8' 或 'liuhecai')

    Returns:
        List[Dict]: 下注列表
    """
    bets = []

    # 1. 番玩法: "番 3/200" 或 "3番200"
    fan_pattern1 = re.compile(r'番\s*([1-4])\s*/\s*(\d+)', re.IGNORECASE)
    fan_pattern2 = re.compile(r'([1-4])\s*番\s*(\d+)', re.IGNORECASE)

    for match in fan_pattern1.finditer(message):
        odds = await get_odds_from_backend(odds_service, 'fan', game_type=game_type)
        bets.append({
            'type': 'fan',
            'number': int(match.group(1)),
            'amount': Decimal(match.group(2)),
            'odds': odds,
            'player': player,
            'raw': match.group(0)
        })

    for match in fan_pattern2.finditer(message):
        odds = await get_odds_from_backend(odds_service, 'fan', game_type=game_type)
        bets.append({
            'type': 'fan',
            'number': int(match.group(1)),
            'amount': Decimal(match.group(2)),
            'odds': odds,
            'player': player,
            'raw': match.group(0)
        })

    # 2. 正玩法: "正1/200" 或 "1/200"
    zheng_pattern1 = re.compile(r'正\s*([1-4])\s*/\s*(\d+)', re.IGNORECASE)
    zheng_pattern2 = re.compile(r'^([1-4])\s*/\s*(\d+)$', re.MULTILINE)

    for match in zheng_pattern1.finditer(message):
        odds = await get_odds_from_backend(odds_service, 'zheng', game_type=game_type)
        bets.append({
            'type': 'zheng',
            'number': int(match.group(1)),
            'amount': Decimal(match.group(2)),
            'odds': odds,
            'player': player,
            'raw': match.group(0)
        })

    # 只有在没有匹配到番时才尝试简单数字格式
    if len(bets) == 0:
        for match in zheng_pattern2.finditer(message):
            odds = await get_odds_from_backend(odds_service, 'zheng', game_type=game_type)
            bets.append({
                'type': 'zheng',
                'number': int(match.group(1)),
                'amount': Decimal(match.group(2)),
                'odds': odds,
                'player': player,
                'raw': match.group(0)
            })

    # 3. 念玩法: "1念2/300" 或 "念12/200"
    nian_pattern1 = re.compile(r'([1-4])\s*念\s*([1-4])\s*/\s*(\d+)', re.IGNORECASE)
    nian_pattern2 = re.compile(r'念\s*([1-4][1-4])\s*/\s*(\d+)', re.IGNORECASE)

    for match in nian_pattern1.finditer(message):
        num1 = int(match.group(1))
        num2 = int(match.group(2))
        if num1 != num2:
            odds = await get_odds_from_backend(odds_service, 'nian', game_type=game_type)
            bets.append({
                'type': 'nian',
                'first': num1,    # 首位
                'second': num2,   # 次位
                'amount': Decimal(match.group(3)),
                'odds': odds,
                'player': player,
                'raw': match.group(0)
            })

    for match in nian_pattern2.finditer(message):
        numbers = [int(n) for n in match.group(1)]
        if numbers[0] != numbers[1]:
            odds = await get_odds_from_backend(odds_service, 'nian', game_type=game_type)
            bets.append({
                'type': 'nian',
                'first': numbers[0],
                'second': numbers[1],
                'amount': Decimal(match.group(2)),
                'odds': odds,
                'player': player,
                'raw': match.group(0)
            })

    # 4. 角玩法: "角12/200" 或 "12角200" 或 "12/200"
    jiao_pattern1 = re.compile(r'角\s*([1-4][1-4])\s*/\s*(\d+)', re.IGNORECASE)
    jiao_pattern2 = re.compile(r'([1-4][1-4])\s*角\s*(\d+)', re.IGNORECASE)
    # 使用负向后查来避免匹配三码/更长序列中的中间部分（如"123/100"中的"23"）
    jiao_pattern3 = re.compile(r'(?<![1-4])([1-4][1-4])\s*/\s*(\d+)', re.IGNORECASE)

    for match in jiao_pattern1.finditer(message):
        numbers = [int(n) for n in match.group(1)]
        # 确保是相邻数字
        if abs(numbers[0] - numbers[1]) == 1 or (1 in numbers and 4 in numbers):
            odds = await get_odds_from_backend(odds_service, 'jiao', game_type=game_type)
            bets.append({
                'type': 'jiao',
                'numbers': sorted(numbers),
                'amount': Decimal(match.group(2)),
                'odds': odds,
                'player': player,
                'raw': match.group(0)
            })

    for match in jiao_pattern2.finditer(message):
        numbers = [int(n) for n in match.group(1)]
        if abs(numbers[0] - numbers[1]) == 1 or (1 in numbers and 4 in numbers):
            odds = await get_odds_from_backend(odds_service, 'jiao', game_type=game_type)
            bets.append({
                'type': 'jiao',
                'numbers': sorted(numbers),
                'amount': Decimal(match.group(2)),
                'odds': odds,
                'player': player,
                'raw': match.group(0)
            })

    for match in jiao_pattern3.finditer(message):
        numbers = [int(n) for n in match.group(1)]
        # 确保是相邻数字（12, 23, 34, 14）
        if abs(numbers[0] - numbers[1]) == 1 or (1 in numbers and 4 in numbers):
            odds = await get_odds_from_backend(odds_service, 'jiao', game_type=game_type)
            bets.append({
                'type': 'jiao',
                'numbers': sorted(numbers),
                'amount': Decimal(match.group(2)),
                'odds': odds,
                'player': player,
                'raw': match.group(0)
            })

    # 5. 通/借玩法: "34通/150" 或 "134通/150" 或 "13借4/120"
    tong_pattern1 = re.compile(r'([1-4]{2,3})\s*通\s*/\s*(\d+)', re.IGNORECASE)
    tong_pattern2 = re.compile(r'([1-4][1-4])\s*借\s*([1-4])\s*/\s*(\d+)', re.IGNORECASE)

    for match in tong_pattern1.finditer(message):
        numbers = [int(n) for n in match.group(1)]
        odds = await get_odds_from_backend(odds_service, 'tong', game_type=game_type)
        # 取首位和末位
        first = numbers[0]
        second = numbers[-1]
        bets.append({
            'type': 'tong',
            'first': first,    # 首位赢
            'second': second,  # 末位输
            'amount': Decimal(match.group(2)),
            'odds': odds,
            'player': player,
            'raw': match.group(0)
        })

    for match in tong_pattern2.finditer(message):
        first = int(match.group(1)[0])
        second = int(match.group(2))
        odds = await get_odds_from_backend(odds_service, 'tong', game_type=game_type)
        bets.append({
            'type': 'tong',
            'first': first,    # 首位赢
            'second': second,  # 末位输
            'amount': Decimal(match.group(3)),
            'odds': odds,
            'player': player,
            'raw': match.group(0)
        })

    # 6. 正（禁号）玩法: "3无4/220"
    zheng_jin_pattern = re.compile(r'([1-4])\s*无\s*([1-4])\s*/\s*(\d+)', re.IGNORECASE)

    for match in zheng_jin_pattern.finditer(message):
        odds = await get_odds_from_backend(odds_service, 'zheng_jin', game_type=game_type)
        bets.append({
            'type': 'zheng_jin',
            'number': int(match.group(1)),      # 赢号
            'jin_number': int(match.group(2)),  # 禁号
            'amount': Decimal(match.group(3)),
            'odds': odds,
            'player': player,
            'raw': match.group(0)
        })

    # 7. 三码（中）玩法: "123/500" 或 "中123/200"
    zhong_pattern1 = re.compile(r'([1-4]{3})\s*中?\s*/\s*(\d+)', re.IGNORECASE)
    zhong_pattern2 = re.compile(r'中\s*([1-4]{3})\s*/\s*(\d+)', re.IGNORECASE)

    for match in zhong_pattern1.finditer(message):
        numbers = [int(n) for n in match.group(1)]
        unique_numbers = list(set(numbers))
        # 确保三个不同的数字
        if len(unique_numbers) == 3:
            odds = await get_odds_from_backend(odds_service, 'zhong', game_type=game_type)
            bets.append({
                'type': 'zhong',
                'numbers': sorted(unique_numbers),
                'amount': Decimal(match.group(2)),
                'odds': odds,
                'player': player,
                'raw': match.group(0)
            })

    for match in zhong_pattern2.finditer(message):
        numbers = [int(n) for n in match.group(1)]
        unique_numbers = list(set(numbers))
        if len(unique_numbers) == 3:
            odds = await get_odds_from_backend(odds_service, 'zhong', game_type=game_type)
            bets.append({
                'type': 'zhong',
                'numbers': sorted(unique_numbers),
                'amount': Decimal(match.group(2)),
                'odds': odds,
                'player': player,
                'raw': match.group(0)
            })

    # 8. 单双玩法: "单200" 或 "双150"
    parity_pattern = re.compile(r'(单|双)\s*(\d+)', re.IGNORECASE)

    for match in parity_pattern.finditer(message):
        bet_type = 'odd' if match.group(1) == '单' else 'even'
        odds = await get_odds_from_backend(odds_service, bet_type, game_type=game_type)
        bets.append({
            'type': bet_type,
            'amount': Decimal(match.group(2)),
            'odds': odds,
            'player': player,
            'raw': match.group(0)
        })

    # 9. 特码玩法: "5特20" 或 "2.100" 或 "1.20.10.10.10" 或 "特码5/20"
    tema_pattern1 = re.compile(r'([1-9]|[1-4][0-9])\s*特\s*(\d+)', re.IGNORECASE)
    # 匹配点号分隔的特码，至少有一个点号（保证至少是"X.Y"的形式）
    tema_pattern2 = re.compile(r'([1-9]|[1-4][0-9])(?:\.\d+)*\.\d+(?:\s|$)', re.IGNORECASE)
    tema_pattern3 = re.compile(r'特码\s*([1-9]|[1-4][0-9])\s*/\s*(\d+)', re.IGNORECASE)

    # 处理 "5特20" 格式
    for match in tema_pattern1.finditer(message):
        number = int(match.group(1))
        odds = await get_odds_from_backend(odds_service, 'tema', number, game_type)
        bets.append({
            'type': 'tema',
            'number': number,
            'amount': Decimal(match.group(2)),
            'odds': odds,
            'player': player,
            'raw': match.group(0)
        })

    # 处理 "2.100" 或 "2.10.30.29" 格式
    # 规则：最后一个数字是金额，前面的都是特码号
    for match in tema_pattern2.finditer(message):
        full_match = match.group(0).strip()
        parts = full_match.split('.')

        # 至少需要2个元素（号码.金额）
        if len(parts) >= 2:
            # 最后一个是金额
            amount = Decimal(parts[-1])

            # 前面的都是特码号
            for i in range(len(parts) - 1):
                number = int(parts[i])

                # 注意：这里只做基础范围验证（1-49），具体的澳8（1-20）vs 六合彩（1-49）验证
                # 会在validate_bet函数中根据游戏类型进行
                if 1 <= number <= 49 and amount > 0:
                    odds = await get_odds_from_backend(odds_service, 'tema', number, game_type)
                    bets.append({
                        'type': 'tema',
                        'number': number,
                        'amount': amount,
                        'odds': odds,
                        'player': player,
                        'raw': f"{number}.{amount}"  # 只记录当前号码和金额
                    })

    # 处理 "特码5/20" 格式
    for match in tema_pattern3.finditer(message):
        number = int(match.group(1))
        odds = await get_odds_from_backend(odds_service, 'tema', number, game_type)
        bets.append({
            'type': 'tema',
            'number': number,
            'amount': Decimal(match.group(2)),
            'odds': odds,
            'player': player,
            'raw': match.group(0)
        })

    return bets


def calculate_result(
    bet: Dict[str, Any],
    draw_code: str,
    draw_number: int,
    special_number: Optional[int] = None
) -> Tuple[str, Decimal, Decimal]:
    """
    计算单个下注的结算结果

    Args:
        bet: 下注对象
        draw_code: 开奖号码字符串（如"1,2,3,4,5,6,7,8"）
        draw_number: 开奖番数(1-4)或特码(1-49)
        special_number: 第8位特码号码(1-49)，用于单双和特码判定

    Returns:
        Tuple[str, Decimal, Decimal]: (status, payout, profit)
            - status: 'win' / 'lose' / 'tie'
            - payout: 派彩金额
            - profit: 盈亏金额
    """
    status = 'lose'
    payout = Decimal('0')
    profit = -bet['amount']

    bet_type = bet['type']
    amount = bet['amount']
    odds = bet['odds']

    if bet_type == 'fan':
        # 番：命中即赢
        if bet['number'] == draw_number:
            status = 'win'
            payout = amount * odds
            profit = payout - amount

    elif bet_type == 'zheng':
        # 正：命中赢号赢，命中输号输，其他和局
        lose_number = ZHENG_PAIRS[bet['number']]

        if bet['number'] == draw_number:
            status = 'win'
            payout = amount * odds
            profit = payout - amount
        elif lose_number == draw_number:
            status = 'lose'
        else:
            status = 'tie'
            payout = amount  # 返还本金
            profit = Decimal('0')

    elif bet_type == 'nian':
        # 念：首位赢、次位和局退本金
        if bet['first'] == draw_number:
            status = 'win'
            payout = amount * odds
            profit = payout - amount
        elif bet['second'] == draw_number:
            status = 'tie'
            payout = amount  # 返还本金
            profit = Decimal('0')

    elif bet_type == 'jiao':
        # 角：投注相邻番数，开出其中一个则赢
        if draw_number in bet['numbers']:
            status = 'win'
            payout = amount * odds
            profit = payout - amount

    elif bet_type == 'tong':
        # 通/借：首位赢，末位输，其它和局
        if bet['first'] == draw_number:
            status = 'win'
            payout = amount * odds
            profit = payout - amount
        elif bet['second'] == draw_number:
            status = 'lose'
        else:
            status = 'tie'
            payout = amount  # 返还本金
            profit = Decimal('0')

    elif bet_type == 'zheng_jin':
        # 正（禁号）：指定禁号，命中赢号赢2倍，禁号输，其它退本金
        if bet['number'] == draw_number:
            status = 'win'
            payout = amount * odds
            profit = payout - amount
        elif bet['jin_number'] == draw_number:
            status = 'lose'
        else:
            status = 'tie'
            payout = amount  # 返还本金
            profit = Decimal('0')

    elif bet_type == 'zhong':
        # 中：投注三个番数，开出其中一个则赢
        if draw_number in bet['numbers']:
            status = 'win'
            payout = amount * odds
            profit = payout - amount

    elif bet_type == 'odd':
        # 单：按开奖特码号码（1-49）奇偶判定
        eighth_number = special_number

        # 如果没有提供special_number，尝试从draw_code解析
        if not eighth_number and draw_code:
            try:
                draw_numbers = [int(n.strip()) for n in draw_code.split(',')]
                if len(draw_numbers) >= 8:
                    eighth_number = draw_numbers[7]  # 第8位（索引7）
            except (ValueError, IndexError):
                pass

        if eighth_number and eighth_number % 2 == 1:
            status = 'win'
            payout = amount * odds
            profit = payout - amount

    elif bet_type == 'even':
        # 双：按开奖特码号码（1-49）奇偶判定
        eighth_number = special_number

        # 如果没有提供special_number，尝试从draw_code解析
        if not eighth_number and draw_code:
            try:
                draw_numbers = [int(n.strip()) for n in draw_code.split(',')]
                if len(draw_numbers) >= 8:
                    eighth_number = draw_numbers[7]  # 第8位（索引7）
            except (ValueError, IndexError):
                pass

        if eighth_number and eighth_number % 2 == 0:
            status = 'win'
            payout = amount * odds
            profit = payout - amount

    elif bet_type == 'tema':
        # 特码：第8位特码号码匹配
        eighth_number = special_number

        # 如果没有提供special_number，尝试从draw_code解析
        if not eighth_number and draw_code:
            try:
                draw_numbers = [int(n.strip()) for n in draw_code.split(',')]
                if len(draw_numbers) >= 8:
                    eighth_number = draw_numbers[7]  # 第8位（索引7）
            except (ValueError, IndexError):
                pass

        if eighth_number and bet['number'] == eighth_number:
            status = 'win'
            payout = amount * odds
            profit = payout - amount

    # 保留两位小数
    payout = round(payout, 2)
    profit = round(profit, 2)

    return status, payout, profit


async def validate_bet(
    bet: Dict[str, Any],
    odds_service,
    game_type: str = 'lucky8'
) -> Tuple[bool, Optional[str]]:
    """
    验证下注是否合法

    Args:
        bet: 下注对象
        odds_service: OddsService实例
        game_type: 游戏类型 ('lucky8' 或 'liuhecai')

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    bet_type = bet['type']
    amount = bet['amount']

    # 1. 游戏类型验证：liuhecai只支持tema（特码）
    if game_type == 'liuhecai' and bet_type != 'tema':
        return False, f"❌ 六合彩游戏只支持特码投注，不支持{format_bet_type(bet_type)}玩法"

    # 2. 特码号码范围验证
    if bet_type == 'tema':
        number = bet.get('number')
        if game_type == 'lucky8':
            # 澳洲幸运8特码范围：1-20
            if not (1 <= number <= 20):
                return False, f"❌ 澳洲幸运8特码号码必须在1-20之间，当前号码：{number}"
        elif game_type == 'liuhecai':
            # 六合彩特码范围：1-49
            if not (1 <= number <= 49):
                return False, f"❌ 六合彩特码号码必须在1-49之间，当前号码：{number}"

    # 3. 金额验证
    if amount <= 0:
        return False, "❌ 投注金额必须大于0"

    # 4. 赔率配置验证（检查投注限额）
    validation = await odds_service.validate_bet_amount(bet_type, amount, game_type)
    if not validation['valid']:
        return False, f"❌ {validation['error']}"

    return True, None


def format_bet_summary(bets: List[Dict[str, Any]]) -> str:
    """
    格式化投注摘要

    Args:
        bets: 下注列表

    Returns:
        str: 格式化的摘要文本
    """
    if not bets:
        return "未识别到有效投注"

    total_amount = sum(bet['amount'] for bet in bets)

    lines = [f"📝 共识别到 {len(bets)} 笔投注，总金额 {total_amount}"]

    for i, bet in enumerate(bets, 1):
        bet_type = format_bet_type(bet['type'])
        amount = bet['amount']
        odds = bet['odds']

        if bet['type'] == 'fan':
            lines.append(f"{i}. {bet_type} {bet['number']} - {amount}元 (赔率{odds})")
        elif bet['type'] == 'zheng':
            lines.append(f"{i}. {bet_type} {bet['number']} - {amount}元 (赔率{odds})")
        elif bet['type'] == 'nian':
            lines.append(f"{i}. {bet_type} {bet['first']}念{bet['second']} - {amount}元 (赔率{odds})")
        elif bet['type'] == 'jiao':
            nums = ''.join(map(str, bet['numbers']))
            lines.append(f"{i}. {bet_type} {nums} - {amount}元 (赔率{odds})")
        elif bet['type'] == 'tong':
            lines.append(f"{i}. {bet_type} {bet['first']}通{bet['second']} - {amount}元 (赔率{odds})")
        elif bet['type'] == 'zheng_jin':
            lines.append(f"{i}. {bet_type} {bet['number']}无{bet['jin_number']} - {amount}元 (赔率{odds})")
        elif bet['type'] == 'zhong':
            nums = ''.join(map(str, bet['numbers']))
            lines.append(f"{i}. {bet_type} {nums} - {amount}元 (赔率{odds})")
        elif bet['type'] in ('odd', 'even'):
            lines.append(f"{i}. {bet_type} - {amount}元 (赔率{odds})")
        elif bet['type'] == 'tema':
            lines.append(f"{i}. {bet_type} {bet['number']} - {amount}元 (赔率{odds})")

    return '\n'.join(lines)


def format_bet_type(bet_type: str) -> str:
    """格式化下注类型名称"""
    names = {
        'fan': '番',
        'zheng': '正',
        'nian': '念',
        'jiao': '角',
        'tong': '通/借',
        'zheng_jin': '正（禁号）',
        'zhong': '中',
        'odd': '单',
        'even': '双',
        'tema': '特码'
    }
    return names.get(bet_type, bet_type)


def format_status(status: str) -> str:
    """格式化结算状态"""
    names = {
        'win': '赢',
        'lose': '输',
        'tie': '和'
    }
    return names.get(status, status)


def is_bet_type_supported_by_game_type(game_type: str, bet_type: str) -> bool:
    """
    检查下注玩法是否与游戏种类匹配

    Args:
        game_type: 游戏类型 ('lucky8' 或 'liuhecai')
        bet_type: 下注玩法类型

    Returns:
        bool: 是否支持
    """
    # 定义每个游戏类型支持的玩法
    SUPPORTED_BET_TYPES = {
        'lucky8': ['fan', 'zheng', 'nian', 'jiao', 'tong', 'zheng_jin', 'zhong', 'odd', 'even', 'tema'],
        'liuhecai': ['tema']  # 六合彩专属特码，只支持特码
    }

    supported_types = SUPPORTED_BET_TYPES.get(game_type, [])
    return bet_type in supported_types


def get_game_type_error_message(
    game_type: str,
    bet_type: str,
    bet_raw: str,
    bet_number: Optional[int] = None
) -> str:
    """
    获取不支持的玩法的错误提示

    Args:
        game_type: 游戏类型
        bet_type: 下注类型
        bet_raw: 原始投注字符串
        bet_number: 投注号码（特码时使用）

    Returns:
        str: 错误提示信息
    """
    if bet_type == 'tema':
        if game_type == 'lucky8':
            # 检查澳8特码是否在1-20范围内
            if bet_number and not (1 <= bet_number <= 20):
                return f"❌ 投注失败: 澳洲幸运8特码号码必须在1-20之间（当前: {bet_number}）"
        elif game_type == 'liuhecai':
            # 检查六合彩特码是否在1-49范围内
            if bet_number and not (1 <= bet_number <= 49):
                return f"❌ 投注失败: 六合彩特码号码必须在1-49之间（当前: {bet_number}）"
    else:
        # 非特码玩法在liuhecai中不支持
        if game_type == 'liuhecai':
            return f"❌ 投注失败: 六合彩游戏仅支持特码投注，不支持 {format_bet_type(bet_type)} 玩法（投注内容: {bet_raw}）"

    return f"❌ 投注失败: 不支持的玩法（{bet_raw}）"


def settle_bet(
    bet: Dict[str, Any],
    draw_number: int,
    special_number: Optional[int] = None
) -> Dict[str, Any]:
    """
    结算单个下注（兼容Node.js版本的函数签名）

    Args:
        bet: 下注对象
        draw_number: 开奖番数(1-4)
        special_number: 第8位特码号码(1-49)，用于单双和特码判定

    Returns:
        Dict: 结算结果，包含原始bet数据加上结算信息
    """
    # 调用calculate_result获取结算结果
    status, payout, profit = calculate_result(bet, '', draw_number, special_number)

    # 返回完整的结算对象（与Node.js版本兼容）
    result = {
        **bet,
        'draw_number': draw_number,
        'status': status,
        'payout': payout,
        'profit': profit
    }

    return result


def settle_tema_bet(bet: Dict[str, Any], tema_number: int) -> Dict[str, Any]:
    """
    结算特码下注（使用六合彩开奖数据）

    Args:
        bet: 下注对象
        tema_number: 六合彩特码号码(1-49)

    Returns:
        Dict: 结算结果
    """
    result = {
        **bet,
        'tema_number': tema_number,
        'status': 'lose',
        'payout': Decimal('0'),
        'profit': -bet['amount']
    }

    # 只处理特码类型
    if bet['type'] != 'tema':
        logger.warning(f"⚠️ settle_tema_bet 只能处理特码类型，当前类型: {bet['type']}")
        return result

    # 特码：匹配六合彩特码号码
    if bet['number'] == tema_number:
        result['status'] = 'win'
        result['payout'] = bet['amount'] * bet['odds']
        result['profit'] = result['payout'] - bet['amount']

    # 保留两位小数
    result['payout'] = round(result['payout'], 2)
    result['profit'] = round(result['profit'], 2)

    return result
