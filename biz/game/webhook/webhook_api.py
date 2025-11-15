"""
Webhook API路由
对应 bot-server.js 的 /webhook 和 /api/sync-gametype 接口
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

from biz.game.service.game_service import GameService
from biz.user.service.user_service import UserService
from biz.chat.repo.chat_repo import ChatRepository
from external.bot_api_client import BotApiClient
from biz.game.scheduler import get_scheduler

logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhook"])


# ===== 请求模型 =====

class WebhookRequest(BaseModel):
    """Webhook请求体"""
    event: str
    data: Dict[str, Any]


class SyncGameTypeRequest(BaseModel):
    """同步游戏类型请求"""
    chatId: str
    gameType: str
    oldGameType: str = None


# ===== 依赖注入占位符 =====

def get_game_service() -> GameService:
    """获取GameService（占位，由依赖注入容器提供）"""
    raise NotImplementedError("需要配置依赖注入容器")


def get_user_service() -> UserService:
    """获取UserService（占位，由依赖注入容器提供）"""
    raise NotImplementedError("需要配置依赖注入容器")


def get_chat_repo() -> ChatRepository:
    """获取ChatRepository（占位，由依赖注入容器提供）"""
    raise NotImplementedError("需要配置依赖注入容器")


def get_bot_client() -> BotApiClient:
    """获取BotApiClient（占位，由依赖注入容器提供）"""
    raise NotImplementedError("需要配置依赖注入容器")


# ===== Webhook处理 =====

@router.post('/webhook')
async def webhook(
    request: WebhookRequest,
    game_service: GameService = Depends(get_game_service),
    user_service: UserService = Depends(get_user_service),
    chat_repo: ChatRepository = Depends(get_chat_repo),
    bot_client: BotApiClient = Depends(get_bot_client)
):
    """
    Webhook接口 - 接收悦聊Bot消息
    100%兼容Node.js版本的入参/出参格式

    事件类型:
    - group.created: 群聊创建
    - member.joined: 新成员加入
    - message.received: 接收到消息
    """
    event = request.event
    data = request.data

    try:
        logger.info(f"=== 收到 Webhook 事件 ===")
        logger.info(f"Event: {event}")
        logger.info(f"Data: {data}")

        # 1. 处理群聊创建事件
        if event == 'group.created':
            await handle_group_created(data, chat_repo, bot_client, game_service)

        # 2. 处理新成员加入事件
        elif event == 'member.joined':
            await handle_member_joined(data, user_service)

        # 3. 处理接收到的消息
        elif event == 'message.received':
            await handle_message_received(data, chat_repo, user_service, game_service, bot_client)

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"❌ Webhook处理错误: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}


async def handle_group_created(
    data: Dict[str, Any],
    chat_repo: ChatRepository,
    bot_client: BotApiClient,
    game_service: GameService
):
    """
    处理群聊创建事件

    Args:
        data: 事件数据
        chat_repo: ChatRepository
        bot_client: BotApiClient
        game_service: GameService
    """
    chat = data.get('chat', {})
    chat_id = chat.get('id')
    chat_name = chat.get('name')

    logger.info(f"收到群聊创建事件: {chat_name} ({chat_id})")

    # 1. 自动加入群聊
    join_result = await bot_client.join_chat(chat_id)

    if not join_result.get('success'):
        logger.error(f"❌ 加入群聊失败: {join_result.get('error')}")
        return

    logger.info(f"✅ 已加入群聊: {chat_name}")

    # 2. 创建或更新群聊信息
    existing_chat = await chat_repo.get_by_id(chat_id)
    if not existing_chat:
        await chat_repo.create_chat({
            'id': chat_id,
            'name': chat_name,
            'game_type': 'lucky8',  # 默认游戏类型
            'owner_id': None
        })
        logger.info(f"✅ 创建群聊: {chat_name} ({chat_id})")

    # 3. 启动自动开奖定时器
    scheduler = get_scheduler()
    if scheduler:
        scheduler.start_timer(chat_id, 'lucky8')
        logger.info(f"⏰ 已启动自动开奖定时器: {chat_id}")

    # 4. 同步群聊成员
    try:
        members_result = await bot_client.get_chat_members(chat_id)
        if members_result.get('success'):
            members = members_result.get('members', [])
            logger.info(f"✅ 同步群聊成员: {len(members)} 个")
            # TODO: 批量创建用户
    except Exception as e:
        logger.error(f"⚠️ 同步群聊成员失败: {str(e)}")

    # 5. 发送欢迎消息
    welcome_message = """🎰【澳洲幸运8游戏机器人】🎰

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

    await bot_client.send_message(chat_id, welcome_message)


async def handle_member_joined(
    data: Dict[str, Any],
    user_service: UserService
):
    """
    处理新成员加入事件

    Args:
        data: 事件数据
        user_service: UserService
    """
    member = data.get('member', {})
    chat = data.get('chat', {})

    member_id = member.get('id')
    member_name = member.get('name')
    chat_id = chat.get('id')

    logger.info(f"新成员加入: {member_name} ({member_id}) -> 群 {chat_id}")

    # 创建用户（如果不存在）
    await user_service.get_or_create_user(
        user_id=member_id,
        username=member_name,
        chat_id=chat_id,
        balance=1000
    )

    logger.info(f"✅ 用户已准备: {member_name}")


async def handle_message_received(
    data: Dict[str, Any],
    chat_repo: ChatRepository,
    user_service: UserService,
    game_service: GameService,
    bot_client: BotApiClient
):
    """
    处理接收到的消息

    Args:
        data: 事件数据
        chat_repo: ChatRepository
        user_service: UserService
        game_service: GameService
        bot_client: BotApiClient
    """
    message = data.get('message', {})
    if not message:
        logger.error("❌ message 为空")
        return

    chat = message.get('chat', {})
    sender = message.get('sender', {})
    content = message.get('content', '').strip()

    if not chat:
        logger.error("❌ chat 为空")
        return

    if not sender:
        logger.error("❌ sender 为空")
        return

    # 忽略机器人消息
    if sender.get('isBot'):
        logger.info("忽略机器人消息")
        return

    chat_id = chat.get('id')
    sender_id = sender.get('_id') or sender.get('id')
    sender_name = sender.get('name')

    logger.info(f"收到消息: {sender_name} -> {chat.get('name')}: {content}")

    # 1. 确保群聊存在
    existing_chat = await chat_repo.get_by_id(chat_id)
    if not existing_chat:
        await chat_repo.create_chat({
            'id': chat_id,
            'name': chat.get('name'),
            'game_type': 'lucky8',
            'owner_id': None
        })
        logger.info(f"✅ 创建群聊: {chat.get('name')} ({chat_id})")

        # 启动自动开奖定时器
        scheduler = get_scheduler()
        if scheduler:
            scheduler.start_timer(chat_id, 'lucky8')
            logger.info(f"⏰ 已启动自动开奖定时器: {chat_id}")

    # 2. 确保用户存在
    await user_service.get_or_create_user(
        user_id=sender_id,
        username=sender_name,
        chat_id=chat_id,
        balance=1000
    )

    # 3. 根据消息内容分发处理
    if content in ['查', '查询', '余额']:
        await game_service.handle_query_balance(chat_id, sender)

    elif content in ['排行', '排行榜']:
        await game_service.handle_leaderboard(chat_id)

    elif content in ['流水', '历史', '记录']:
        await game_service.handle_bet_history(chat_id, sender)

    elif content == '取消':
        # 检查是否锁定
        scheduler = get_scheduler()
        if scheduler and scheduler.is_bet_locked(chat_id):
            await bot_client.send_message(chat_id, f"@{sender_name} 🔒 已停止下注和取消操作，请等待开奖结果")
            return
        await game_service.handle_cancel_bet(chat_id, sender)

    elif content in ['开奖', '立即开奖']:
        await game_service.execute_draw(chat_id)

    elif content == '开奖历史':
        await game_service.handle_draw_history(chat_id)

    else:
        # 尝试解析为下注指令
        from biz.game.logic import game_logic
        from biz.odds.service.odds_service import OddsService

        # TODO: 从依赖注入获取odds_service
        # 临时创建一个空的service用于解析
        class TempOddsService:
            async def get_odds(self, bet_type, game_type):
                return None

        try:
            bets = await game_logic.parse_bets(
                message=content,
                player=sender_name,
                odds_service=TempOddsService(),
                game_type=existing_chat['game_type'] if existing_chat else 'lucky8'
            )

            if bets:
                # 检查是否锁定
                scheduler = get_scheduler()
                if scheduler and scheduler.is_bet_locked(chat_id):
                    await bot_client.send_message(chat_id, f"@{sender_name} 🔒 已停止下注和取消操作，请等待开奖结果")
                    return

                # 是下注指令
                await game_service.handle_bet_message(chat_id, message, sender)
            else:
                # 无效输入
                await bot_client.send_message(chat_id, f"@{sender_name} 输入无效")

        except Exception as e:
            logger.error(f"❌ 解析消息失败: {str(e)}", exc_info=True)


# ===== 同步游戏类型 =====

@router.post('/api/sync-gametype')
async def sync_game_type(
    request: SyncGameTypeRequest,
    chat_repo: ChatRepository = Depends(get_chat_repo)
):
    """
    同步游戏类型
    当admin-server修改群聊的游戏类型时调用此接口

    Args:
        request: 同步请求

    Returns:
        Dict: 同步结果
    """
    try:
        chat_id = request.chatId
        game_type = request.gameType
        old_game_type = request.oldGameType

        logger.info(f"📢 收到游戏类型同步请求: {chat_id}")
        logger.info(f"   旧类型: {old_game_type} -> 新类型: {game_type}")

        # 更新群聊的游戏类型
        await chat_repo.update_game_type(chat_id, game_type)

        # 更新定时器
        scheduler = get_scheduler()
        if scheduler:
            scheduler.restart_timer(chat_id, game_type)
            logger.info(f"🔄 已重启定时器: {chat_id} -> {game_type}")

        logger.info(f"✅ 游戏类型已同步: {chat_id} -> {game_type}")

        return {"success": True, "message": "游戏彩种已同步"}

    except Exception as e:
        logger.error(f"❌ 同步游戏类型失败: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}
