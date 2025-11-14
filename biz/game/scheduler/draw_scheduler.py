"""
自动开奖调度器
对应 bot-server.js 中的 startAutoDrawTimer 和 stopAutoDrawTimer 函数
"""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DrawScheduler:
    """
    自动开奖调度器
    管理每个群聊的自动开奖定时器
    """

    def __init__(self, game_service):
        """
        初始化调度器

        Args:
            game_service: GameService实例
        """
        self.game_service = game_service
        # 存储每个群聊的定时器任务
        self.timers: Dict[str, asyncio.Task] = {}
        # 存储每个群聊的游戏类型和间隔
        self.chat_config: Dict[str, Dict] = {}

    def get_draw_interval(self, game_type: str) -> int:
        """
        获取开奖间隔（秒）

        Args:
            game_type: 游戏类型（lucky8/liuhecai）

        Returns:
            int: 间隔秒数
        """
        if game_type == 'lucky8':
            return 5 * 60  # 5分钟
        elif game_type == 'liuhecai':
            return 24 * 60 * 60  # 1天
        else:
            return 5 * 60  # 默认5分钟

    async def _auto_draw_loop(self, chat_id: str, game_type: str, interval: int):
        """
        自动开奖循环任务

        Args:
            chat_id: 群聊ID
            game_type: 游戏类型
            interval: 开奖间隔（秒）
        """
        logger.info(f"⏰ 启动自动开奖定时器: 群={chat_id}, 游戏={game_type}, 间隔={interval}秒")

        try:
            while True:
                # 等待到下一次开奖时间
                await asyncio.sleep(interval)

                logger.info(f"🎲 定时开奖触发: 群={chat_id}")

                try:
                    # 执行开奖
                    await self.game_service.execute_draw(chat_id)
                    logger.info(f"✅ 定时开奖完成: 群={chat_id}")

                except Exception as e:
                    logger.error(f"❌ 定时开奖失败: 群={chat_id}, 错误={str(e)}", exc_info=True)
                    # 即使失败也继续运行定时器

        except asyncio.CancelledError:
            logger.info(f"⏹️ 定时器已停止: 群={chat_id}")
            raise

    def start_timer(self, chat_id: str, game_type: str = 'lucky8'):
        """
        启动群聊的自动开奖定时器

        Args:
            chat_id: 群聊ID
            game_type: 游戏类型（lucky8/liuhecai）
        """
        # 如果已存在定时器，先停止
        if chat_id in self.timers:
            self.stop_timer(chat_id)

        # 获取开奖间隔
        interval = self.get_draw_interval(game_type)

        # 保存配置
        self.chat_config[chat_id] = {
            'game_type': game_type,
            'interval': interval
        }

        # 创建并启动定时器任务
        task = asyncio.create_task(
            self._auto_draw_loop(chat_id, game_type, interval)
        )
        self.timers[chat_id] = task

        logger.info(f"✅ 定时器已启动: 群={chat_id}, 游戏={game_type}, 间隔={interval}秒 ({interval/60}分钟)")

    def stop_timer(self, chat_id: str):
        """
        停止群聊的自动开奖定时器

        Args:
            chat_id: 群聊ID
        """
        if chat_id not in self.timers:
            logger.warning(f"⚠️ 定时器不存在: 群={chat_id}")
            return

        # 取消任务
        task = self.timers[chat_id]
        task.cancel()

        # 清理
        del self.timers[chat_id]
        if chat_id in self.chat_config:
            del self.chat_config[chat_id]

        logger.info(f"⏹️ 定时器已停止: 群={chat_id}")

    def restart_timer(self, chat_id: str, new_game_type: str):
        """
        重启群聊的定时器（用于切换游戏类型）

        Args:
            chat_id: 群聊ID
            new_game_type: 新的游戏类型
        """
        old_config = self.chat_config.get(chat_id)
        old_game_type = old_config['game_type'] if old_config else 'unknown'

        logger.info(f"🔄 重启定时器: 群={chat_id}, {old_game_type} -> {new_game_type}")

        # 停止旧定时器
        self.stop_timer(chat_id)

        # 启动新定时器
        self.start_timer(chat_id, new_game_type)

        logger.info(f"✅ 定时器重启完成: 群={chat_id}")

    def is_running(self, chat_id: str) -> bool:
        """
        检查群聊的定时器是否运行中

        Args:
            chat_id: 群聊ID

        Returns:
            bool: 是否运行中
        """
        if chat_id not in self.timers:
            return False

        task = self.timers[chat_id]
        return not task.done()

    def get_timer_info(self, chat_id: str) -> Optional[Dict]:
        """
        获取定时器信息

        Args:
            chat_id: 群聊ID

        Returns:
            Dict: 定时器信息，如果不存在返回None
        """
        if chat_id not in self.chat_config:
            return None

        config = self.chat_config[chat_id]
        return {
            'chat_id': chat_id,
            'game_type': config['game_type'],
            'interval': config['interval'],
            'interval_minutes': config['interval'] / 60,
            'is_running': self.is_running(chat_id)
        }

    def get_all_timers(self) -> Dict[str, Dict]:
        """
        获取所有定时器信息

        Returns:
            Dict: 所有定时器信息
        """
        return {
            chat_id: self.get_timer_info(chat_id)
            for chat_id in self.chat_config.keys()
        }

    def stop_all(self):
        """停止所有定时器"""
        logger.info(f"⏹️ 停止所有定时器，共 {len(self.timers)} 个")

        for chat_id in list(self.timers.keys()):
            self.stop_timer(chat_id)

        logger.info(f"✅ 所有定时器已停止")


# 全局调度器实例
_scheduler: Optional[DrawScheduler] = None


def init_scheduler(game_service) -> DrawScheduler:
    """
    初始化全局调度器

    Args:
        game_service: GameService实例

    Returns:
        DrawScheduler: 调度器实例
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = DrawScheduler(game_service)
        logger.info("✅ 开奖调度器已初始化")
    return _scheduler


def get_scheduler() -> Optional[DrawScheduler]:
    """
    获取全局调度器实例

    Returns:
        DrawScheduler: 调度器实例，如果未初始化返回None
    """
    return _scheduler


async def shutdown_scheduler():
    """关闭调度器（应用退出时调用）"""
    global _scheduler
    if _scheduler is not None:
        logger.info("🔴 关闭开奖调度器...")
        _scheduler.stop_all()
        _scheduler = None
        logger.info("✅ 开奖调度器已关闭")
