"""
自动开奖调度器
对应 bot-server.js 中的全局定时器机制（line 36-1009）
实现功能：
1. 全局定时器：按游戏类型统一开奖（所有相同游戏类型的群聊同时开奖）
2. 倒计时提示：开奖前90秒发送警告
3. 下注锁定：开奖前60秒禁止下注和取消操作
"""
import asyncio
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DrawScheduler:
    """
    自动开奖调度器
    完全对应 Node.js 的全局定时器机制
    """

    def __init__(self, game_service, bot_client):
        """
        初始化调度器

        Args:
            game_service: GameService实例
            bot_client: BotApiClient实例
        """
        self.game_service = game_service
        self.bot_client = bot_client

        # 全局定时器（按游戏类型）
        # 对应 Node.js: globalGameTimers = { lucky8: null, liuhecai: null }
        self.global_game_timers: Dict[str, Optional[asyncio.Task]] = {
            'lucky8': None,
            'liuhecai': None
        }

        # 跟踪哪些群聊已注册到全局定时器
        # 对应 Node.js: registeredChatsForGameType = { lucky8: Set(), liuhecai: Set() }
        self.registered_chats_for_game_type: Dict[str, Set[str]] = {
            'lucky8': set(),
            'liuhecai': set()
        }

        # 倒计时定时器（用于在开奖前提示和限制操作）
        # 对应 Node.js: countdownTimers = { lucky8: {}, liuhecai: {} }
        self.countdown_timers: Dict[str, Dict[str, Dict[str, asyncio.Task]]] = {
            'lucky8': {},
            'liuhecai': {}
        }

        # 跟踪群聊的下注锁定状态（开奖前60秒锁定）
        # 对应 Node.js: betLockStatus = {}
        self.bet_lock_status: Dict[str, bool] = {}

        # 群聊游戏类型映射
        self.chat_game_types: Dict[str, str] = {}

        # 历史开奖同步任务
        self._history_sync_task: Optional[asyncio.Task] = None
        self._history_sync_interval_minutes: int = 60

    def start_history_sync(self, draw_repo, draw_client, interval_minutes: int = 60):
        """
        启动历史开奖定期同步任务（按游戏类型补齐缺口并重试）

        Args:
            draw_repo: DrawRepository 实例
            draw_client: DrawApiClient 实例
            interval_minutes: 同步间隔（分钟）
        """
        if self._history_sync_task is not None:
            logger.warning("⚠️ 历史同步任务已运行，跳过重复启动")
            return

        self._history_sync_interval_minutes = interval_minutes

        async def _loop():
            # 首次延迟，避免与应用启动阶段竞争资源
            await asyncio.sleep(self._history_sync_interval_minutes * 60)
            while True:
                try:
                    await self._history_sync_once(draw_repo, draw_client)
                except Exception as e:
                    logger.error(f"❌ 历史开奖同步失败: {str(e)}", exc_info=True)
                finally:
                    await asyncio.sleep(self._history_sync_interval_minutes * 60)

        self._history_sync_task = asyncio.create_task(_loop())
        logger.info(f"🔄 历史开奖同步任务已启动（间隔 {interval_minutes} 分钟）")

    async def _history_sync_once(self, draw_repo, draw_client):
        """
        执行一次历史开奖同步：对 lucky8 和 liuhecai 分别补齐最近记录
        """
        for game_type in ['lucky8', 'liuhecai']:
            try:
                # 刷新外部数据缓存
                if game_type == 'lucky8':
                    await draw_client.fetch_lucky8_results()
                else:
                    await draw_client.fetch_draw_results()

                recent = await draw_client.get_recent_draws(game_type, limit=50)
                if not recent:
                    logger.warning(f"⚠️ 无{game_type}历史数据可同步")
                    continue

                inserted = 0
                for item in recent:
                    issue = item.get('issue')
                    if not issue:
                        continue

                    # 仅使用系统级别历史（避免为每个群重复写入）
                    exists = await draw_repo.exists_issue(issue, game_type=game_type, chat_id='system')
                    if exists:
                        continue

                    # 构造写入数据
                    draw_data = {
                        'chat_id': 'system',
                        'game_type': game_type,
                        'issue': issue,
                        # lucky8: draw_number 是番数；liuhecai: draw_number 是特码
                        'draw_number': int(str(item.get('draw_number'))) if item.get('draw_number') is not None else None,
                        'draw_code': item.get('draw_code'),
                        'special_number': item.get('special_number'),
                        'draw_time': datetime.now()
                    }

                    try:
                        await draw_repo.create(draw_data)
                        inserted += 1
                    except Exception as e:
                        logger.warning(f"写入{game_type}历史失败(issue={issue}): {str(e)}")

                logger.info(f"📚 {game_type} 历史同步完成，本次新增 {inserted} 条")

            except Exception as e:
                logger.error(f"❌ {game_type} 历史同步异常: {str(e)}", exc_info=True)

    def get_draw_interval(self, game_type: str) -> int:
        """
        获取开奖间隔（秒）
        对应 Node.js: line 856

        Args:
            game_type: 游戏类型（lucky8/liuhecai）

        Returns:
            int: 间隔秒数
        """
        if game_type == 'liuhecai':
            return 86400  # 24小时 = 86400秒
        else:  # lucky8
            return 300  # 5分钟 = 300秒

    def is_bet_locked(self, chat_id: str) -> bool:
        """
        检查群聊是否被锁定（开奖前60秒禁止下注）
        对应 Node.js: betLockStatus[chatId]

        Args:
            chat_id: 群聊ID

        Returns:
            bool: 是否锁定
        """
        return self.bet_lock_status.get(chat_id, False)

    def register_chat_to_global_timer(self, chat_id: str, game_type: str = 'lucky8'):
        """
        为群聊注册到全局开奖定时器
        确保同一游戏类型的所有群聊共享同一个全局定时器
        对应 Node.js: registerChatToGlobalTimer() line 827-843

        Args:
            chat_id: 群聊ID
            game_type: 游戏类型
        """
        # 保存游戏类型
        self.chat_game_types[chat_id] = game_type

        # 如果已注册，直接返回
        if chat_id in self.registered_chats_for_game_type[game_type]:
            logger.info(f"⚠️ 群聊 {chat_id} ({game_type}) 已注册到全局定时器")
            return

        # 标记为已注册
        self.registered_chats_for_game_type[game_type].add(chat_id)
        logger.info(f"📍 群聊 {chat_id} ({game_type}) 已注册到全局定时器")

        # 如果该游戏类型的全局定时器还没启动，就启动它
        if self.global_game_timers[game_type] is None:
            self.start_global_game_timer(game_type)

    def start_global_game_timer(self, game_type: str):
        """
        启动按游戏类型的全局定时器
        所有相同游戏类型的群聊共享同一个定时器，确保同时开奖
        对应 Node.js: startGlobalGameTimer() line 849-920

        Args:
            game_type: 游戏类型
        """
        if self.global_game_timers[game_type] is not None:
            logger.warning(f"⚠️ 游戏 {game_type} 的全局定时器已存在，跳过重复创建")
            return

        # 根据游戏类型确定开奖间隔
        draw_interval = self.get_draw_interval(game_type)
        interval_minutes = draw_interval / 60

        logger.info(f"🎯 启动游戏 \"{game_type}\" 的全局开奖定时器 (间隔: {interval_minutes}分钟)")

        # 创建并启动定时器任务
        task = asyncio.create_task(
            self._global_draw_loop(game_type, draw_interval)
        )
        self.global_game_timers[game_type] = task

        logger.info(f"✅ 游戏 \"{game_type}\" 全局定时器启动成功，将在 {interval_minutes} 分钟后执行第一次开奖")

    async def _global_draw_loop(self, game_type: str, draw_interval: int):
        """
        全局开奖循环
        对应 Node.js: runGlobalDraw() 和 scheduleNextGlobalDraw() line 862-918

        Args:
            game_type: 游戏类型
            draw_interval: 开奖间隔（秒）
        """
        try:
            while True:
                # 先调度倒计时（在开奖前执行）
                await self._schedule_next_global_draw(game_type, draw_interval)

                # 等待到开奖时间
                await asyncio.sleep(draw_interval)

                # 执行开奖
                await self._run_global_draw(game_type)

        except asyncio.CancelledError:
            logger.info(f"⏹️ 游戏 {game_type} 的全局定时器已停止")
            raise

    async def _run_global_draw(self, game_type: str):
        """
        执行全局开奖
        对应 Node.js: runGlobalDraw() line 862-893

        Args:
            game_type: 游戏类型
        """
        try:
            registered_chats = list(self.registered_chats_for_game_type[game_type])

            if len(registered_chats) == 0:
                logger.warning(f"⚠️ 游戏 {game_type} 没有注册的群聊，跳过本次开奖")
                return

            logger.info(f"\n🔔 全局开奖触发: {game_type} ({len(registered_chats)}个群聊)")
            logger.info(f"   群聊列表: {', '.join(registered_chats)}")

            # 为所有注册的群聊执行开奖
            for chat_id in registered_chats:
                try:
                    logger.info(f"  ↳ 执行开奖: {chat_id}")
                    await self.game_service.execute_draw(chat_id)

                    # 🔥 开奖完成后，解除下注锁定
                    self.bet_lock_status[chat_id] = False
                    logger.info(f"🔓 群聊 {chat_id} 下注锁定已解除")

                except Exception as error:
                    logger.error(f"  ❌ 群聊 {chat_id} 开奖出错: {str(error)}", exc_info=True)

        except Exception as error:
            logger.error(f"❌ 全局开奖执行出错: {str(error)}", exc_info=True)

    async def _schedule_next_global_draw(self, game_type: str, draw_interval: int):
        """
        调度下一次开奖（清理旧定时器并设置倒计时）
        对应 Node.js: scheduleNextGlobalDraw() line 896-915

        Args:
            game_type: 游戏类型
            draw_interval: 开奖间隔（秒）
        """
        # 清除旧的倒计时定时器
        if game_type in self.countdown_timers:
            for chat_id in list(self.countdown_timers[game_type].keys()):
                timers = self.countdown_timers[game_type][chat_id]
                if 'warning_timer' in timers and timers['warning_timer']:
                    timers['warning_timer'].cancel()
                if 'lock_timer' in timers and timers['lock_timer']:
                    timers['lock_timer'].cancel()
            self.countdown_timers[game_type] = {}

        # 🔥 在开奖前90秒和60秒时进行提示和锁定
        registered_chats = list(self.registered_chats_for_game_type[game_type])
        if len(registered_chats) > 0:
            await self._schedule_draw_countdown(game_type, registered_chats, draw_interval)

    async def _schedule_draw_countdown(self, game_type: str, registered_chats: list, draw_interval: int):
        """
        调度开奖倒计时（90秒和60秒提示及锁定）
        对应 Node.js: scheduleDrawCountdown() line 925-967

        Args:
            game_type: 游戏类型
            registered_chats: 注册的群聊列表
            draw_interval: 开奖间隔（秒）
        """
        # 初始化该游戏类型的倒计时定时器对象（如果还不存在）
        if game_type not in self.countdown_timers:
            self.countdown_timers[game_type] = {}

        # 在开奖前90秒发送警告提示
        warning_delay = draw_interval - 90  # 提前90秒
        if warning_delay > 0:
            warning_timer = asyncio.create_task(
                self._send_warning_countdown(game_type, registered_chats, warning_delay)
            )
        else:
            warning_timer = None

        # 在开奖前60秒锁定下注和取消操作
        lock_delay = draw_interval - 60  # 提前60秒
        if lock_delay > 0:
            lock_timer = asyncio.create_task(
                self._lock_betting(game_type, registered_chats, lock_delay)
            )
        else:
            lock_timer = None

        # 保存定时器ID，以便后续需要时清除
        for chat_id in registered_chats:
            self.countdown_timers[game_type][chat_id] = {
                'warning_timer': warning_timer,
                'lock_timer': lock_timer
            }

    async def _send_warning_countdown(self, game_type: str, registered_chats: list, delay: int):
        """
        发送开奖前90秒警告
        对应 Node.js: line 932-943

        Args:
            game_type: 游戏类型
            registered_chats: 注册的群聊列表
            delay: 延迟时间（秒）
        """
        try:
            await asyncio.sleep(delay)

            logger.info(f"\n⏰ 开奖前90秒警告: {game_type}")

            from biz.game.templates.message_templates import GameMessageTemplates
            warning_message = GameMessageTemplates.get_countdown_warning(game_type)

            for chat_id in registered_chats:
                try:
                    result = await self.bot_client.send_message(
                        chat_id,
                        warning_message
                    )

                    # 如果返回403错误（机器人不在群里），自动注销该群聊
                    if not result.get('success') and result.get('status_code') == 403:
                        logger.warning(f"  ⚠️ 机器人不在群聊 {chat_id}，自动注销")
                        self.unregister_chat_from_global_timer(chat_id)
                    else:
                        logger.info(f"  ↳ 已发送90秒警告: {chat_id}")
                except Exception as error:
                    logger.error(f"  ❌ 发送90秒警告失败 {chat_id}: {str(error)}")

        except asyncio.CancelledError:
            logger.debug(f"警告定时器已取消: {game_type}")
            raise

    async def _lock_betting(self, game_type: str, registered_chats: list, delay: int):
        """
        开奖前60秒锁定下注
        对应 Node.js: line 946-958

        Args:
            game_type: 游戏类型
            registered_chats: 注册的群聊列表
            delay: 延迟时间（秒）
        """
        try:
            await asyncio.sleep(delay)

            logger.info(f"\n🔒 开奖前60秒锁定: {game_type}")

            from biz.game.templates.message_templates import GameMessageTemplates
            lock_message = GameMessageTemplates.get_lock_message(game_type)

            for chat_id in registered_chats:
                try:
                    self.bet_lock_status[chat_id] = True  # 锁定该群聊
                    result = await self.bot_client.send_message(
                        chat_id,
                        lock_message
                    )

                    # 如果返回403错误（机器人不在群里），自动注销该群聊
                    if not result.get('success') and result.get('status_code') == 403:
                        logger.warning(f"  ⚠️ 机器人不在群聊 {chat_id}，自动注销")
                        self.unregister_chat_from_global_timer(chat_id)
                    else:
                        logger.info(f"  ↳ 已锁定下注: {chat_id}")
                except Exception as error:
                    logger.error(f"  ❌ 发送锁定提示失败 {chat_id}: {str(error)}")

        except asyncio.CancelledError:
            logger.debug(f"锁定定时器已取消: {game_type}")
            raise

    def stop_global_game_timer(self, game_type: str):
        """
        停止按游戏类型的全局定时器
        对应 Node.js: stopGlobalGameTimer() line 972-979

        Args:
            game_type: 游戏类型
        """
        if self.global_game_timers[game_type]:
            task = self.global_game_timers[game_type]
            task.cancel()
            self.global_game_timers[game_type] = None
            self.registered_chats_for_game_type[game_type].clear()
            logger.info(f"⏹️ 已停止游戏 {game_type} 的全局定时器")

    def unregister_chat_from_global_timer(self, chat_id: str):
        """
        从全局定时器中移除群聊
        对应 Node.js: unregisterChatFromGlobalTimer() line 984-995

        Args:
            chat_id: 群聊ID
        """
        # 🔥 修复: 从所有游戏类型中移除该群聊(因为可能已经改了游戏类型)
        removed_from = []
        for game_type in ['lucky8', 'liuhecai']:
            if chat_id in self.registered_chats_for_game_type[game_type]:
                self.registered_chats_for_game_type[game_type].remove(chat_id)
                removed_from.append(game_type)
                logger.info(f"🔌 群聊 {chat_id} 已从 {game_type} 全局定时器移除")

                # 如果该游戏类型没有其他群聊了，可以停止定时器（可选）
                if len(self.registered_chats_for_game_type[game_type]) == 0:
                    logger.info(f"   该游戏类型 {game_type} 没有其他群聊了")

        if not removed_from:
            logger.warning(f"⚠️ 群聊 {chat_id} 未在任何游戏类型定时器中注册")

        # 清理锁定状态
        if chat_id in self.bet_lock_status:
            del self.bet_lock_status[chat_id]

        # 清理游戏类型映射
        if chat_id in self.chat_game_types:
            del self.chat_game_types[chat_id]

    # ==================== 兼容旧接口 ====================

    def start_timer(self, chat_id: str, game_type: str = 'lucky8'):
        """
        启动群聊的自动开奖定时器（兼容旧代码）
        新逻辑：只需将群聊注册到全局定时器即可
        对应 Node.js: startAutoDrawTimer() line 1001-1004

        Args:
            chat_id: 群聊ID
            game_type: 游戏类型（lucky8/liuhecai）
        """
        self.register_chat_to_global_timer(chat_id, game_type)

    def stop_timer(self, chat_id: str):
        """
        停止群聊的自动开奖定时器（兼容旧代码）
        对应 Node.js: stopAutoDrawTimer() line 1009

        Args:
            chat_id: 群聊ID
        """
        self.unregister_chat_from_global_timer(chat_id)

    def restart_timer(self, chat_id: str, game_type: str):
        """
        重启群聊的定时器（用于切换游戏类型）
        对应 Node.js: 修改游戏类型后的逻辑 (admin-server.js line 1240-1244)

        Args:
            chat_id: 群聊ID
            game_type: 新的游戏类型
        """
        logger.info(f"🔄 重启定时器: {chat_id} -> {game_type}")

        # 1. 从旧的全局定时器中注销
        self.unregister_chat_from_global_timer(chat_id)

        # 2. 注册到新的全局定时器
        self.register_chat_to_global_timer(chat_id, game_type)

        logger.info(f"✅ 定时器已重启: {chat_id} 已切换到 {game_type}")

    def is_running(self, chat_id: str) -> bool:
        """
        检查群聊的定时器是否运行中

        Args:
            chat_id: 群聊ID

        Returns:
            bool: 是否运行中
        """
        game_type = self.chat_game_types.get(chat_id, 'lucky8')
        return chat_id in self.registered_chats_for_game_type[game_type]

    def get_timer_info(self, chat_id: str) -> Optional[Dict]:
        """
        获取定时器信息

        Args:
            chat_id: 群聊ID

        Returns:
            Dict: 定时器信息，如果不存在返回None
        """
        game_type = self.chat_game_types.get(chat_id)
        if not game_type:
            return None

        is_registered = chat_id in self.registered_chats_for_game_type[game_type]
        if not is_registered:
            return None

        interval = self.get_draw_interval(game_type)
        return {
            'chat_id': chat_id,
            'game_type': game_type,
            'interval': interval,
            'interval_minutes': interval / 60,
            'is_running': True,
            'is_locked': self.is_bet_locked(chat_id),
            'global_timer_active': self.global_game_timers[game_type] is not None
        }

    def get_all_timers(self) -> Dict[str, Dict]:
        """
        获取所有定时器信息

        Returns:
            Dict: 所有定时器信息
        """
        result = {}
        for game_type in ['lucky8', 'liuhecai']:
            for chat_id in self.registered_chats_for_game_type[game_type]:
                result[chat_id] = self.get_timer_info(chat_id)
        return result

    def stop_all(self):
        """停止所有定时器"""
        total_chats = sum(len(chats) for chats in self.registered_chats_for_game_type.values())
        logger.info(f"⏹️ 停止所有定时器，共 {total_chats} 个群聊")

        # 停止所有全局定时器
        for game_type in ['lucky8', 'liuhecai']:
            self.stop_global_game_timer(game_type)

        # 清理所有状态
        self.bet_lock_status.clear()
        self.chat_game_types.clear()

        # 停止历史同步
        if self._history_sync_task:
            try:
                self._history_sync_task.cancel()
            except Exception:
                pass
            self._history_sync_task = None

        logger.info(f"✅ 所有定时器已停止")


# 全局调度器实例
_scheduler: Optional[DrawScheduler] = None


def init_scheduler(game_service, bot_client) -> DrawScheduler:
    """
    初始化全局调度器

    Args:
        game_service: GameService实例
        bot_client: BotApiClient实例

    Returns:
        DrawScheduler: 调度器实例
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = DrawScheduler(game_service, bot_client)
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
