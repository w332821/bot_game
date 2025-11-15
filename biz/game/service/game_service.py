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

            # 获取当前期号
            current_issue = await self._generate_issue_number(game_type)

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
                    'draw_issue': current_issue,
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

            # 获取当前期号
            chat = await self.chat_repo.get_by_id(chat_id)
            if not chat:
                return

            game_type = chat.get('game_type', 'lucky8') if isinstance(chat, dict) else chat.game_type
            current_issue = await self._generate_issue_number(game_type)

            # 获取当前期所有pending的下注
            pending_bets = await self.bet_repo.get_user_pending_bets(
                user_id=sender_id,
                chat_id=chat_id,
                issue=current_issue
            )

            if not pending_bets:
                await self.bot_client.send_message(
                    chat_id,
                    f"@{sender_name} 本期没有待结算的下注"
                )
                return

            # 计算退还金额
            refund_amount = sum(bet['amount'] for bet in pending_bets)

            # 退还余额
            await self.user_repo.add_balance(sender_id, chat_id, refund_amount)

            # 取消所有下注
            for bet in pending_bets:
                await self.bet_repo.cancel_bet(bet['id'])

            # 获取新余额
            user = await self.user_repo.get_user_in_chat(sender_id, chat_id)
            new_balance = user['balance']

            response = f"✅ 已取消本期所有下注，退还金额: {refund_amount:.2f}\n当前余额: {new_balance:.2f}"

            await self.bot_client.send_message(chat_id, response)

            logger.info(f"✅ 取消下注成功: 用户={sender_name}, 退还={refund_amount}")

        except Exception as e:
            logger.error(f"❌ 取消下注失败: {str(e)}", exc_info=True)

    async def execute_draw(self, chat_id: str) -> None:
        """
        执行开奖
        对应 bot-server.js 的 executeDraw 函数

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

            # 生成期号
            issue = await self._generate_issue_number(game_type)

            # 获取开奖号码（从第三方API）
            draw_result = await self._fetch_draw_result(game_type)
            if not draw_result:
                logger.error(f"❌ 获取开奖号码失败: game_type={game_type}")
                await self.bot_client.send_message(chat_id, "❌ 开奖失败: 无法获取开奖号码")
                return

            draw_number = draw_result['draw_number']
            draw_code = draw_result['draw_code']
            special_number = draw_result.get('special_number')

            # 添加调试日志
            logger.info(f"🎲 开奖数据: game_type={game_type}, draw_number={draw_number}, special_number={special_number}, draw_code={draw_code}")

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
            pending_bets = await self.bet_repo.get_pending_bets_by_issue(chat_id, issue)

            if not pending_bets:
                # 没有投注，只发送开奖结果
                response = f"🎉【第{issue}期开奖】🎉\n\n"
                if game_type == 'lucky8':
                    response += f"开奖号码: {draw_number}\n"
                    response += f"特码: {special_number}\n"
                else:
                    response += f"开奖号码: {special_number}\n"
                response += "\n本期无投注"

                await self.bot_client.send_message(chat_id, response)
                return

            # 结算所有投注
            winners = []
            losers = []
            ties = []

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

                # 更新投注记录
                await self.bet_repo.settle_bet(
                    bet_id=bet['id'],
                    result=status,
                    pnl=profit,
                    draw_number=draw_number,
                    draw_code=draw_code
                )

                # 更新用户余额
                if payout > 0:
                    await self.user_repo.add_balance(bet['user_id'], chat_id, payout)

                # 分类统计
                user = await self.user_repo.get_user_in_chat(bet['user_id'], chat_id)
                # bet_type可能在bet_details中，也可能在bet中的lottery_type字段
                bet_type = bet_details.get('bet_type') or bet.get('lottery_type') or bet.get('bet_type')
                bet_type_name = game_logic.format_bet_type(bet_type)
                # amount字段可能叫bet_amount或amount
                amount = bet.get('bet_amount') or bet.get('amount', 0)
                result_item = {
                    'username': user['username'],
                    'bet_type': bet_type_name,
                    'amount': float(amount),
                    'profit': float(profit)
                }

                if status == 'win':
                    winners.append(result_item)
                elif status == 'lose':
                    losers.append(result_item)
                else:
                    ties.append(result_item)

            # 生成开奖消息
            response = f"🎉【第{issue}期开奖】🎉\n\n"

            if game_type == 'lucky8':
                response += f"开奖号码: {draw_number}\n"
                response += f"特码: {special_number}\n\n"
            else:
                response += f"开奖号码: {special_number}\n\n"

            if winners:
                response += "中奖用户：\n"
                for w in winners:
                    response += f"• {w['username']} - {w['bet_type']} 赢 +{w['profit']:.2f}\n"
                response += "\n"

            if ties:
                response += "和局用户：\n"
                for t in ties:
                    response += f"• {t['username']} - {t['bet_type']} 和 +0.00\n"
                response += "\n"

            if losers:
                response += "未中奖用户：\n"
                for l in losers:
                    response += f"• {l['username']} - {l['bet_type']} 输 {l['profit']:.2f}\n"

            await self.bot_client.send_message(chat_id, response)

            logger.info(f"✅ 开奖完成: 期号={issue}, 中奖={len(winners)}, 未中奖={len(losers)}")

        except Exception as e:
            logger.error(f"❌ 开奖失败: {str(e)}", exc_info=True)
            await self.bot_client.send_message(chat_id, "❌ 开奖失败: 系统错误")

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
            'special_number': result.get('special_number')
        }
