"""
游戏消息模板管理
根据game_type返回不同的机器人话术
"""


class GameMessageTemplates:
    """游戏消息模板"""

    @staticmethod
    def get_welcome_message(game_type: str) -> str:
        """
        获取欢迎消息

        Args:
            game_type: 游戏类型（lucky8/liuhecai）

        Returns:
            str: 欢迎消息文本
        """
        if game_type == 'liuhecai':
            return """🎰【六合彩游戏机器人】🎰

欢迎使用！初始余额: 1000

📋 玩法说明:
• 特码: "特码8/100" (下注特码8，金额100元)
• 特码范围: 1-49
• 赔率: 1:40

🔍 查询指令:
• "查" - 查询余额
• "排行" - 查看排行榜

⏰ 每24小时自动开奖
💰 这是虚拟货币游戏，仅供娱乐！"""
        else:  # lucky8
            return """🎰【澳洲幸运8游戏机器人】🎰

欢迎使用！初始余额: 1000

📋 玩法说明:
• 番: "番 3/200" 或 "3番200" (赔率3倍)
• 正: "正1/200" 或 "1/200" (赔率2倍)
• 单双: "单200" 或 "双150" (赔率2倍)

🔍 查询指令:
• "查" - 查询余额
• "排行" - 查看排行榜

⏰ 每5分钟自动开奖
💰 这是虚拟货币游戏，仅供娱乐！"""

    @staticmethod
    def get_countdown_warning(game_type: str) -> str:
        """
        获取90秒倒计时警告

        Args:
            game_type: 游戏类型（lucky8/liuhecai）

        Returns:
            str: 倒计时警告文本
        """
        if game_type == 'liuhecai':
            return "⏰ 提示：距离开奖还剩90秒，准备停止下注"
        else:
            return "⏰ 提示：还剩30秒停止下注\n\n距离开奖还剩：90秒"

    @staticmethod
    def get_lock_message(game_type: str) -> str:
        """
        获取60秒锁定消息

        Args:
            game_type: 游戏类型（lucky8/liuhecai）

        Returns:
            str: 锁定消息文本
        """
        return "🔒 已停止下注和取消操作，请等待开奖结果\n\n距离开奖还剩：60秒"

    @staticmethod
    def get_game_name(game_type: str) -> str:
        """
        获取游戏名称

        Args:
            game_type: 游戏类型（lucky8/liuhecai）

        Returns:
            str: 游戏名称
        """
        return '六合彩' if game_type == 'liuhecai' else '澳洲幸运8'

    @staticmethod
    def get_game_interval_text(game_type: str) -> str:
        """
        获取开奖间隔描述

        Args:
            game_type: 游戏类型（lucky8/liuhecai）

        Returns:
            str: 开奖间隔描述
        """
        return '24小时' if game_type == 'liuhecai' else '5分钟'
