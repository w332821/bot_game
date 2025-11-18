"""
游戏名称映射工具
支持中文游戏名与内部代码的双向映射
根据 DEV_PLAN.md 规范
"""

# 游戏名称枚举（中文）
VALID_GAMES_CN = ["新奥六合彩", "168澳洲幸运8"]

# 游戏名称映射：中文 -> 内部代码
GAME_NAME_TO_CODE = {
    "新奥六合彩": "liuhecai",
    "168澳洲幸运8": "lucky8",
}

# 游戏名称映射：内部代码 -> 中文
GAME_CODE_TO_NAME = {
    "liuhecai": "新奥六合彩",
    "lucky8": "168澳洲幸运8",
}


def validate_game_name(game_name: str) -> str:
    """
    验证游戏名称是否合法（中文）

    Args:
        game_name: 游戏名称（中文）

    Returns:
        str: 验证通过返回原游戏名

    Raises:
        ValueError: 游戏名称不合法时抛出异常
    """
    if game_name not in VALID_GAMES_CN:
        raise ValueError(f"游戏名称错误，只能是 {VALID_GAMES_CN}")
    return game_name


def game_name_to_code(game_name: str) -> str:
    """
    中文游戏名转换为内部代码

    Args:
        game_name: 游戏名称（中文）

    Returns:
        str: 内部代码

    Raises:
        ValueError: 游戏名称不合法时抛出异常
    """
    validate_game_name(game_name)
    return GAME_NAME_TO_CODE[game_name]


def game_code_to_name(game_code: str) -> str:
    """
    内部代码转换为中文游戏名

    Args:
        game_code: 内部代码

    Returns:
        str: 中文游戏名

    Raises:
        ValueError: 代码不合法时抛出异常
    """
    if game_code not in GAME_CODE_TO_NAME:
        raise ValueError(f"游戏代码错误，只能是 {list(GAME_CODE_TO_NAME.keys())}")
    return GAME_CODE_TO_NAME[game_code]


def validate_game_code(game_code: str) -> str:
    """
    验证游戏代码是否合法

    Args:
        game_code: 游戏代码

    Returns:
        str: 验证通过返回原代码

    Raises:
        ValueError: 代码不合法时抛出异常
    """
    if game_code not in GAME_CODE_TO_NAME:
        raise ValueError(f"游戏代码错误，只能是 {list(GAME_CODE_TO_NAME.keys())}")
    return game_code
