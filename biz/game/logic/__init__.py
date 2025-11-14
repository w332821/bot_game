"""
Game logic module - 游戏逻辑模块
处理下注解析、结算计算、玩法验证等核心游戏规则
"""

from .game_logic import (
    parse_bets,
    calculate_result,
    validate_bet,
    format_bet_summary,
    get_odds_from_backend,
    format_bet_type,
    format_status,
    ZHENG_PAIRS
)

__all__ = [
    'parse_bets',
    'calculate_result',
    'validate_bet',
    'format_bet_summary',
    'get_odds_from_backend',
    'format_bet_type',
    'format_status',
    'ZHENG_PAIRS'
]
