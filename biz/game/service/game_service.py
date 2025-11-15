"""
游戏业务逻辑服务
对应 bot-server.js 中的各个 handler 函数
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4

from biz.user.service.user_service import UserService
from biz.user.repo.user_repo import UserRepository
from biz.bet.repo.bet_repo import BetRepository
from biz.chat.repo.chat_repo import ChatRepository
from biz.draw.repo.draw_repo import DrawRepository
from biz.odds.service.odds_service import OddsService
from biz.game.logic import game_logic
from external.bot_api_client import BotApiClient
from external.draw_api_client import get_draw_api_client

logger = logging.getLogger(__name__)


class GameService:
    """游戏业务逻辑服务"""

    def __init__(
        self,
        user_service: UserService,
        user_repo: UserRepository,
        bet_repo: BetRepository,
        chat_repo: ChatRepository,
        draw_repo: DrawRepository,
        odds_service: OddsService,
        bot_api_client: BotApiClient
    ):
        self.user_service = user_service
        self.user_repo = user_repo
        self.bet_repo = bet_repo
        self.chat_repo = chat_repo
        self.draw_repo = draw_repo
        self.odds_service = odds_service
        self.bot_client = bot_api_client

    async def handle_bet_message(
        self,
        chat_id: str,
        message: Dict[str, Any],
        sender: Dict[str, Any]
    ) -> None:
        """
        处理下注消息
        对应 bot-server.js 的 handleBetMessage 函数

        Args:
            chat_id: 群聊ID
            message: 消息对象
            sender: 发送者信息
        """
        try:
            content = message.get('content', '').strip()
            sender_id = sender.get('_id') or sender.get('id')
            sender_name = sender.get('name')

            logger.info(f"📝 处理下注: 用户={sender_name}, 群={chat_id}, 内容={content}")

            # 获取群聊信息和游戏类型
            chat = await self.chat_repo.get_by_id(chat_id)
            if not chat:
                logger.error(f"❌ 群聊不存在: {chat_id}")
                return

            game_type = chat.get('game_type', 'lucky8') if isinstance(chat, dict) else chat.game_type

            # 解析下注指令
            bets = await game_logic.parse_bets(
                message=content,
                player=sender_name,
                odds_service=self.odds_service,
                game_type=game_type
            )

            if not bets:
                await self.bot_client.send_message(
                    chat_id,
                    f"@{sender_name} 输入无效"
                )
                return

            # 验证每个下注
            valid_bets = []
            error_messages = []

            for bet in bets:
                is_valid, error_msg = await game_logic.validate_bet(
                    bet=bet,
                    odds_service=self.odds_service,
                    game_type=game_type
                )

                if is_valid:
                    valid_bets.append(bet)
                else:
                    error_messages.append(error_msg)

            # 如果有错误，返回错误消息
            if error_messages:
                await self.bot_client.send_message(
                    chat_id,
                    '\n'.join(error_messages)
                )
                return

            if not valid_bets:
                await self.bot_client.send_message(
                    chat_id,
                    f"@{sender_name} 没有有效的下注"
                )
                return

            # 计算总金额
            total_amount = sum(bet['amount'] for bet in valid_bets)

            # 检查用户余额
            user = await self.user_repo.get_user_in_chat(sender_id, chat_id)
            if not user:
                # 创建用户
                user = await self.user_service.get_or_create_user(
                    user_id=sender_id,
                    username=sender_name,
                    chat_id=chat_id,
                    balance=Decimal('1000')
                )

            if user['balance'] < total_amount:
                await self.bot_client.send_message(
                    chat_id,
                    f"@{sender_name} ❌ 下注失败: 余额不足（当前余额: {user['balance']:.2f}，需要: {total_amount:.2f}）"
                )
                return

            # 扣除余额
            updated_user = await self.user_repo.subtract_balance(sender_id, chat_id, total_amount)
            if updated_user is None:
                await self.bot_client.send_message(
                    chat_id,
                    f"@{sender_name} ❌ 下注失败: 余额扣除失败"
                )
                return

            # 获取新余额
            new_balance = updated_user['balance']

            # 🔥 CRITICAL: 获取当前期号用于显示
            # 从第三方API获取最新期号，用于下注确认消息
            # 但结算时会结算所有pending的投注（不限期号）
            try:
                draw_result = await self._fetch_draw_result(game_type)
                current_issue = draw_result.get('issue', 'unknown') if draw_result else 'unknown'
            except Exception as e:
                logger.warning(f"⚠️ 获取期号失败，使用占位符: {str(e)}")
                current_issue = "待开奖"

            # 保存下注记录
            bet_ids = []
            for bet in valid_bets:
                bet_record = await self.bet_repo.create({
                    'user_id': sender_id,
                    'chat_id': chat_id,
                    'game_type': game_type,
                    'bet_type': bet['type'],
                    'amount': bet['amount'],
                    'odds': bet['odds'],
                    'status': 'pending',
                    'draw_issue': current_issue,  # 使用占位符，开奖时更新
                    'bet_details': bet  # 保存完整的下注详情
                })
                bet_ids.append(bet_record['id'])

            # 生成确认消息
            response = f"📝 下注成功！\n\n"
            response += game_logic.format_bet_summary(valid_bets)
            response += f"\n\n总金额: {float(total_amount):.2f}元"
            response += f"\n余额: {float(new_balance):.2f}"
            response += f"\n期号: {current_issue}"

            await self.bot_client.send_message(chat_id, response)

            logger.info(f"✅ 下注成功: 用户={sender_name}, 期号={current_issue}, 注单数={len(bet_ids)}")

        except Exception as e:
            logger.error(f"❌ 处理下注失败: {str(e)}", exc_info=True)
            await self.bot_client.send_message(
                chat_id,
                f"@{sender.get('name')} ❌ 下注失败: 系统错误"
            )

    async def handle_query_balance(
        self,
        chat_id: str,
        sender: Dict[str, Any]
    ) -> None:
        """
        处理余额查询
        对应 bot-server.js 的 handleQueryBalance 函数

        Args:
            chat_id: 群聊ID
            sender: 发送者信息
        """
        try:
            sender_id = sender.get('_id') or sender.get('id')
            sender_name = sender.get('name')

            logger.info(f"💰 查询余额: 用户={sender_name}, 群={chat_id}")

            # 获取用户
            user = await self.user_repo.get_user_in_chat(sender_id, chat_id)

            if not user:
                # 创建用户
                user = await self.user_service.get_or_create_user(
                    user_id=sender_id,
                    username=sender_name,
                    chat_id=chat_id,
                    balance=Decimal('1000')
                )

            balance = user['balance']
            response = f"@{sender_name} 余额: {balance:.2f}"

            await self.bot_client.send_message(chat_id, response)

        except Exception as e:
            logger.error(f"❌ 查询余额失败: {str(e)}", exc_info=True)

    async def handle_leaderboard(self, chat_id: str) -> None:
        """
        处理排行榜查询
        对应 bot-server.js 的 handleLeaderboard 函数

        Args:
            chat_id: 群聊ID
        """
        try:
            logger.info(f"🏆 查询排行榜: 群={chat_id}")

            # 获取群内所有用户
            users = await self.user_repo.get_chat_users(chat_id)

            if not users:
                await self.bot_client.send_message(chat_id, "暂无用户数据")
                return

            # 计算盈亏（初始余额1000）
            user_stats = []
            for user in users:
                balance = float(user['balance'])
                profit = balance - 1000.0
                user_stats.append({
                    'name': user['username'],
                    'balance': balance,
                    'profit': profit
                })

            # 按余额降序排序
            user_stats.sort(key=lambda x: x['balance'], reverse=True)

            # 生成排行榜消息
            response = '【排行榜】\n'
            for i, entry in enumerate(user_stats, 1):
                profit_sign = '+' if entry['profit'] >= 0 else ''
                response += f"{i}. {entry['name']} - {entry['balance']:.2f} ({profit_sign}{entry['profit']:.2f})\n"

            await self.bot_client.send_message(chat_id, response)

        except Exception as e:
            logger.error(f"❌ 查询排行榜失败: {str(e)}", exc_info=True)

    async def handle_bet_history(
        self,
        chat_id: str,
        sender: Dict[str, Any]
    ) -> None:
        """
        处理流水记录查询
        对应 bot-server.js 的 handleBetHistory 函数

        Args:
            chat_id: 群聊ID
            sender: 发送者信息
        """
        try:
            sender_id = sender.get('_id') or sender.get('id')
            sender_name = sender.get('name')

            logger.info(f"📊 查询流水: 用户={sender_name}, 群={chat_id}")

            # 获取今日起始时间
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            # 获取今日下注记录
            today_bets = await self.bet_repo.get_user_bets_since(
                user_id=sender_id,
                chat_id=chat_id,
                since_time=today_start
            )

            # 统计今日流水和盈亏
            total_bet = Decimal('0')
            total_profit = Decimal('0')

            for bet in today_bets:
                total_bet += bet['amount']
                if bet.get('profit'):
                    total_profit += bet['profit']

            profit_sign = '+' if total_profit >= 0 else ''
            response = f"@{sender_name}\n今日流水：{total_bet:.2f}，今日盈亏：{profit_sign}{total_profit:.2f}"

            await self.bot_client.send_message(chat_id, response)

        except Exception as e:
            logger.error(f"❌ 查询流水失败: {str(e)}", exc_info=True)

    async def handle_cancel_bet(
        self,
        chat_id: str,
        sender: Dict[str, Any]
    ) -> None:
        """
        处理取消下注
        对应 bot-server.js 的 handleCancelBet 函数

        Args:
            chat_id: 群聊ID
            sender: 发送者信息
        """
        try:
            sender_id = sender.get('_id') or sender.get('id')
            sender_name = sender.get('name')

            logger.info(f"🚫 取消下注: 用户={sender_name}, 群={chat_id}")

            # 🔥 CRITICAL: 取消用户所有pending的下注（不限期号）
            # 对应 Node.js: session.pendingBets.filter(b => b.playerId === senderId)
            pending_bets = await self.bet_repo.get_user_all_pending_bets(
                user_id=sender_id,
                chat_id=chat_id
            )

            if not pending_bets:
                await self.bot_client.send_message(
                    chat_id,
                    f"@{sender_name}\n当前没有下注"
                )
                return

            # 计算退还金额
            refund_amount = sum(bet['bet_amount'] for bet in pending_bets)

            # 退还余额
            await self.user_repo.add_balance(sender_id, chat_id, refund_amount)

            # 取消所有下注
            for bet in pending_bets:
                await self.bet_repo.cancel_bet(bet['id'])

            # 对应 Node.js: "@sender.name\n取消成功"
            response = f"@{sender_name}\n取消成功"

            await self.bot_client.send_message(chat_id, response)

            logger.info(f"✅ 取消下注成功: 用户={sender_name}, 退还={refund_amount}")

        except Exception as e:
            logger.error(f"❌ 取消下注失败: {str(e)}", exc_info=True)

    async def execute_draw(self, chat_id: str) -> None:
        """
        执行开奖
        对应 bot-server.js 的 executeDraw 函数 (line 554-817)

        完全按照Node.js版本的逻辑实现，包括发送以下6条消息：
        1. 开奖信息
        2. 中奖名单
        3. 开奖图片
        4. 历史宝路（仅澳洲幸运8）
        5. 积分名单
        6. 下注速查指南

        Args:
            chat_id: 群聊ID
        """
        try:
            logger.info(f"🎲 执行开奖: 群={chat_id}")

            # 获取群聊信息
            chat = await self.chat_repo.get_by_id(chat_id)
            if not chat:
                logger.error(f"❌ 群聊不存在: {chat_id}")
                return

            game_type = chat.get('game_type', 'lucky8') if isinstance(chat, dict) else chat.game_type

            # 获取开奖号码（从第三方API）
            draw_result = await self._fetch_draw_result(game_type)
            if not draw_result:
                logger.error(f"❌ 获取开奖号码失败: game_type={game_type}")
                await self.bot_client.send_message(chat_id, "❌ 开奖失败: 无法获取开奖号码")
                return

            draw_number = draw_result['draw_number']
            draw_code = draw_result['draw_code']
            special_number = draw_result.get('special_number')

            # 🔥 CRITICAL: 使用第三方API返回的期号，而不是自己生成
            # 对应 Node.js: drawInfo.issue (来自 latestLucky8Draw.preDrawIssue)
            issue = draw_result.get('issue', 'unknown')

            # 添加调试日志
            logger.info(f"🎲 开奖数据: game_type={game_type}, draw_number={draw_number}, special_number={special_number}, draw_code={draw_code}")

            # 计算大小单双（仅用于幸运8）- 对应 bot-server.js line 595-601
            size_type = ''
            parity_type = ''
            if special_number and game_type == 'lucky8':
                size_type = '大' if special_number > 24 else '小'
                parity_type = '单' if special_number % 2 == 1 else '双'

            # 保存开奖记录
            await self.draw_repo.create({
                'chat_id': chat_id,
                'game_type': game_type,
                'issue': issue,
                'draw_number': draw_number,
                'draw_code': draw_code,
                'special_number': special_number,
                'draw_time': datetime.now()
            })

            # 获取所有pending的投注
            # 🔥 CRITICAL: 结算所有pending的投注（不管期号），与Node.js逻辑一致
            # Node.js使用 session.pendingBets（不限期号）
            pending_bets = await self.bet_repo.get_all_pending_bets(chat_id)

            # 结算所有投注 - 对应 bot-server.js line 604-658
            results = []
            if pending_bets:
                for bet in pending_bets:
                    # 解析 bet_details（如果是 JSON 字符串）
                    import json
                    bet_details = bet.get('bet_details')
                    if bet_details and isinstance(bet_details, str):
                        try:
                            bet_details = json.loads(bet_details)
                        except:
                            bet_details = None

                    # 如果没有 bet_details，使用 bet 本身
                    if not bet_details:
                        bet_details = bet

                    # 计算结果
                    status, payout, profit = game_logic.calculate_result(
                        bet=bet_details,
                        draw_code=draw_code,
                        draw_number=draw_number,
                        special_number=special_number
                    )

                    # 更新投注记录（包括期号）
                    await self.bet_repo.settle_bet(
                        bet_id=bet['id'],
                        result=status,
                        pnl=profit,
                        draw_number=draw_number,
                        draw_code=draw_code,
                        issue=issue  # 更新为实际的期号
                    )

                    # 更新用户余额
                    if payout > 0:
                        await self.user_repo.add_balance(bet['user_id'], chat_id, payout)

                    # 获取用户信息
                    user = await self.user_repo.get_user_in_chat(bet['user_id'], chat_id)

                    # 保存结果信息（用于后续消息生成）
                    bet_type = bet_details.get('type') or bet_details.get('bet_type') or bet.get('lottery_type') or bet.get('bet_type')
                    amount = bet.get('bet_amount') or bet.get('amount', 0)

                    results.append({
                        'playerId': bet['user_id'],
                        'playerName': user['username'],
                        'type': bet_type,
                        'number': bet_details.get('number'),
                        'first': bet_details.get('first'),
                        'second': bet_details.get('second'),
                        'numbers': bet_details.get('numbers'),
                        'jinNumber': bet_details.get('jinNumber'),
                        'amount': float(amount),
                        'status': status,
                        'profit': float(profit)
                    })

            # ==================== 消息1: 开奖信息 ====================
            # 对应 bot-server.js line 660-673
            game_name = '澳洲幸运8' if game_type == 'lucky8' else '新澳'
            message = f"{game_name}\n\n第{issue}期\n\n开奖号码：\n{draw_code}\n\n"

            if special_number:
                message += f"开奖结果：{str(special_number).zfill(2)}({draw_number}){size_type}{parity_type}"
            else:
                if game_name == '新澳':
                    message += f"开奖结果：{draw_number}特"
                else:
                    message += f"开奖结果：{draw_number}番"

            await self.bot_client.send_message(chat_id, message)

            # ==================== 消息2: 中奖名单 ====================
            # 对应 bot-server.js line 676-718
            winning_list_message = f"{issue}期中奖名单"

            if results:
                has_winners = False

                # 按玩家分组
                player_results = {}
                for result in results:
                    player_name = result['playerName']
                    if player_name not in player_results:
                        player_results[player_name] = []
                    player_results[player_name].append(result)

                # 为每个玩家的每个获胜下注单独成行
                for player_name, player_bets in player_results.items():
                    for result in player_bets:
                        if result['status'] == 'win':
                            # 格式化下注描述
                            bet_desc = self._format_bet_description(result)
                            winning_list_message += f"\n@{player_name} {bet_desc}{result['amount']:.0f}={result['profit']:.2f}"
                            has_winners = True

                # 如果没有中奖者
                if not has_winners:
                    winning_list_message += '\n\n本期无中奖用户'

            await self.bot_client.send_message(chat_id, winning_list_message)

            # ==================== 消息3: 开奖图片 ====================
            # 对应 bot-server.js line 720-768
            try:
                # 获取历史开奖记录用于生成图片
                draw_history = await self.draw_repo.get_recent_draws(chat_id, limit=15)

                if draw_history:
                    from utils import get_draw_image_generator
                    import os

                    image_generator = get_draw_image_generator()
                    image_path = image_generator.generate_image(game_type, draw_history)

                    if image_path:
                        filename = os.path.basename(image_path)
                        # 对应 Node.js: publicUrl = `/uploads/${filename}`
                        public_url = f"/uploads/{filename}"

                        # 对应 Node.js: buildImageUrl(result.publicUrl)
                        image_host = os.getenv('IMAGE_HOST', 'myrepdemo.top')
                        image_port = os.getenv('IMAGE_PORT', '65035')
                        full_url = f"http://{image_host}:{image_port}{public_url}"

                        await self.bot_client.send_image(chat_id, full_url, filename=filename)
                        logger.info(f"✅ 已发送开奖图片: {full_url}")
            except Exception as e:
                logger.error(f"⚠️ 发送开奖图片失败: {str(e)}")

            # ==================== 消息4: 历史宝路 (仅澳洲幸运8) ====================
            # 对应 bot-server.js line 772-779
            if game_type == 'lucky8':
                try:
                    # 获取最近30期开奖记录
                    from external.draw_api_client import get_draw_api_client
                    draw_client = get_draw_api_client()
                    recent_draws = await draw_client.get_recent_draws(game_type, limit=30)

                    if recent_draws:
                        # 反向排列，最新的在前
                        baolu_results = '-'.join([str(d['draw_number']) for d in reversed(recent_draws)])
                        baolu_message = f"历史宝路\n{baolu_results}"
                        await self.bot_client.send_message(chat_id, baolu_message)
                        logger.info(f"✅ 已发送历史宝路")
                except Exception as e:
                    logger.error(f"⚠️ 发送历史宝路失败: {str(e)}")

            # ==================== 消息5: 积分名单 ====================
            # 对应 bot-server.js line 782-792
            try:
                # 获取群内所有用户
                all_users = await self.user_repo.get_chat_users(chat_id)

                # 按余额降序排列
                all_users.sort(key=lambda u: u['balance'], reverse=True)

                score_message = f"{game_name}\n\n第{issue}期积分名单\n\n上下分请联系财务\n\n======积分排行======\n\n🔥玩家 💰积分\n\n"

                for user in all_users:
                    score_message += f"{user['username']}:{user['balance']:.2f}\n"

                await self.bot_client.send_message(chat_id, score_message)
                logger.info(f"✅ 已发送积分名单")
            except Exception as e:
                logger.error(f"⚠️ 发送积分名单失败: {str(e)}")

            # ==================== 消息6: 下注速查指南 ====================
            # 对应 bot-server.js line 795-813
            bet_guide_message = """番：3番300 → 命中结果号

念：1念2/300 → 首位赢、次位和局退本金

角：12/200或12角200 → 两个结果号任意命中

借：13借4/120 → 首位赢、末位和、其他输

正(禁号)：3无4/220 → 指定禁号、命中赢、禁号输、其他退本金

三码(中)：123/500 → 覆盖3个结果号赢、其他输

单双：单200/双150 → 按开奖号码(1-20)奇偶判定

特码：5特20或5.6/60 → 命中开奖号码1-20

关键词：查(积分+流水)、流水(今日+累计盈亏)、取消(封盘前撤单)"""

            await self.bot_client.send_message(chat_id, bet_guide_message)
            logger.info(f"✅ 已发送下注速查指南")

            logger.info(f"✅ 开奖完成: 期号={issue}, 中奖={len([r for r in results if r['status'] == 'win'])}, 所有6条消息已发送")

        except Exception as e:
            logger.error(f"❌ 开奖失败: {str(e)}", exc_info=True)
            await self.bot_client.send_message(chat_id, "❌ 开奖失败: 系统错误")

    def _format_bet_description(self, result: Dict[str, Any]) -> str:
        """
        格式化下注描述
        对应 bot-server.js line 694-704

        Args:
            result: 结算结果

        Returns:
            str: 格式化的下注描述
        """
        bet_type = result['type']

        if bet_type == 'fan':
            return f"{result['number']}番"
        elif bet_type == 'zheng':
            return f"{result['number']}正"
        elif bet_type == 'tema':
            return f"{result['number']}特"
        elif bet_type == 'nian':
            return f"{result['first']}念{result['second']}"
        elif bet_type == 'jiao':
            numbers = result.get('numbers', [])
            return f"{''.join(map(str, numbers))}角"
        elif bet_type == 'tong':
            return f"{result['first']}{result['second']}通"
        elif bet_type == 'zheng_jin':
            return f"{result['number']}无{result['jinNumber']}"
        elif bet_type == 'zhong':
            numbers = result.get('numbers', [])
            return f"{''.join(map(str, numbers))}中"
        elif bet_type == 'odd':
            return '单'
        elif bet_type == 'even':
            return '双'
        else:
            return game_logic.format_bet_type(bet_type)

    async def handle_draw_history(self, chat_id: str) -> None:
        """
        处理开奖历史查询
        对应 bot-server.js 的 handleDrawHistory 函数

        Args:
            chat_id: 群聊ID
        """
        try:
            logger.info(f"📜 查询开奖历史: 群={chat_id}")

            # 获取最近15期开奖记录
            draws = await self.draw_repo.get_recent_draws(chat_id, limit=15)

            if not draws:
                await self.bot_client.send_message(chat_id, "暂无开奖记录")
                return

            # 获取群聊游戏类型
            chat = await self.chat_repo.get_by_id(chat_id)
            game_type = chat.get('game_type', 'lucky8') if chat else 'lucky8'

            # 生成开奖历史图片
            from utils import get_draw_image_generator
            import os

            image_generator = get_draw_image_generator()
            image_path = image_generator.generate_image(game_type, draws)

            if image_path:
                # 构建图片URL（与Node.js版本一致）
                filename = os.path.basename(image_path)
                # 假设图片在 /public/images/ 目录下
                public_url = f"/public/images/{filename}"

                # 构建完整URL
                image_host = os.getenv('IMAGE_HOST', 'myrepdemo.top')
                image_port = os.getenv('IMAGE_PORT', '65035')
                full_url = f"http://{image_host}:{image_port}{public_url}"

                # 发送图片
                await self.bot_client.send_image(chat_id, full_url, filename=f"draw_history_{game_type}.png")
                logger.info(f"✅ 已发送开奖历史图片: {full_url}")
            else:
                # 图片生成失败，发送文本
                response = "【开奖历史】\n"
                for draw in draws:
                    response += f"期号: {draw['issue']}, 号码: {draw['draw_number']}"
                    if draw.get('special_number'):
                        response += f", 特码: {draw['special_number']}"
                    response += "\n"
                await self.bot_client.send_message(chat_id, response)

        except Exception as e:
            logger.error(f"❌ 查询开奖历史失败: {str(e)}", exc_info=True)

    async def _generate_issue_number(self, game_type: str) -> str:
        """
        生成期号

        Args:
            game_type: 游戏类型

        Returns:
            str: 期号
        """
        now = datetime.now()

        if game_type == 'lucky8':
            # 澳洲幸运8: YYYYMMDD + 三位序号
            date_str = now.strftime('%Y%m%d')
            # 获取今日最新期号
            latest = await self.draw_repo.get_latest_draw_by_date(date_str, game_type)
            if latest:
                last_seq = int(latest['issue'][-3:])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            return f"{date_str}{new_seq:03d}"
        else:
            # 六合彩: YYYYMMDD
            return now.strftime('%Y%m%d')

    async def _fetch_draw_result(self, game_type: str) -> Optional[Dict[str, Any]]:
        """
        从第三方API获取开奖结果

        Args:
            game_type: 游戏类型

        Returns:
            Dict: 开奖结果
        """
        # 使用第三方开奖API客户端
        draw_client = get_draw_api_client()
        result = await draw_client.get_draw_result(game_type)

        if not result:
            logger.error(f"❌ 获取开奖数据失败: game_type={game_type}")
            return None

        return {
            'draw_number': result.get('draw_number'),
            'draw_code': result.get('draw_code'),
            'special_number': result.get('special_number'),
            'issue': result.get('issue', 'unknown')  # 返回第三方API的期号
        }
