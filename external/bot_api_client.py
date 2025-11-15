"""
悦聊Bot API客户端封装
对应 bot-server.js 中的 botApiCall 和 sendMessage 函数
"""
import os
import logging
import aiohttp
import json
import hashlib
import hmac
import time
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class BotApiClient:
    """悦聊Bot API客户端"""

    def __init__(self):
        self.base_url = os.getenv('BOT_API_BASE', 'http://127.0.0.1:65035')
        self.api_key = os.getenv('BOT_API_KEY')
        self.api_secret = os.getenv('BOT_API_SECRET')

        if not self.api_key or not self.api_secret:
            logger.warning("⚠️ BOT_API_KEY 或 BOT_API_SECRET 未配置")

    def _generate_signature(self, data: Dict[str, Any], timestamp: str) -> str:
        """
        生成API签名（与Node.js版本完全一致）

        Args:
            data: 请求数据
            timestamp: 时间戳

        Returns:
            str: HMAC-SHA256签名
        """
        if not self.api_secret:
            logger.error("❌ API Secret未配置，无法生成签名")
            return ""

        from base.json_encoder import safe_json_dumps
        sign_data = safe_json_dumps(data, separators=(',', ':'), ensure_ascii=False) + timestamp
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            sign_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _get_headers(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        获取请求头（与Node.js版本完全一致）

        Args:
            data: 请求数据，用于生成签名

        Returns:
            Dict: 请求头
        """
        if not self.api_key:
            logger.error("❌ API Key未配置")
            return {'Content-Type': 'application/json'}

        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(data, timestamp)

        return {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
            'X-Signature': signature,
            'X-Timestamp': timestamp
        }

    async def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[aiohttp.FormData] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求到悦聊Bot API

        Args:
            method: HTTP方法（GET/POST/PUT/DELETE）
            path: API路径（如 /api/bot/message/{chatId}）
            json_data: JSON数据
            data: FormData数据（用于上传文件）

        Returns:
            Dict: API响应数据
        """
        url = f"{self.base_url}{path}"

        # 准备请求数据（用于生成签名）
        request_data = json_data if json_data else {}

        # 生成认证头
        headers = self._get_headers(request_data)

        # 如果是上传文件，移除Content-Type让aiohttp自动设置
        if data:
            headers.pop('Content-Type', None)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_data = await response.json()

                    if response.status >= 400:
                        logger.error(f"❌ Bot API请求失败: {method} {path}")
                        logger.error(f"   状态码: {response.status}")
                        logger.error(f"   响应: {response_data}")
                        return {'success': False, 'error': response_data}

                    # 兼容不同的响应格式
                    # 如果响应是 {success: true, data: ...} 格式，直接返回
                    # 如果响应只是数据，包装成 {success: true, data: ...}
                    if isinstance(response_data, dict) and 'success' in response_data:
                        return response_data
                    else:
                        return {'success': True, 'data': response_data}

        except aiohttp.ClientError as e:
            logger.error(f"❌ Bot API网络错误: {method} {path} - {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"❌ Bot API未知错误: {method} {path} - {str(e)}")
            return {'success': False, 'error': str(e)}

    async def send_message(self, chat_id: str, content: str) -> Dict[str, Any]:
        """
        发送文本消息到群聊

        Args:
            chat_id: 群聊ID
            content: 消息内容

        Returns:
            Dict: API响应
        """
        logger.info(f"📤 发送消息到群聊 {chat_id}: {content[:50]}...")

        if not self.api_key or not self.api_secret:
            logger.error("❌ Bot API凭证未配置，无法发送消息")
            return {'success': False, 'error': 'Bot API credentials not configured'}

        result = await self._request(
            method='POST',
            path=f'/api/bot/send/{chat_id}',  # 修复：与Node.js版本一致
            json_data={'content': content}
        )

        if result.get('success'):
            logger.info(f"✅ 消息发送成功")
        else:
            logger.error(f"❌ 消息发送失败: {result.get('error')}")

        return result

    async def send_image(
        self,
        chat_id: str,
        image_url: str,
        filename: str = 'image.png'
    ) -> Dict[str, Any]:
        """
        发送图片到群聊（与Node.js版本完全一致）

        Args:
            chat_id: 群聊ID
            image_url: 图片URL（公网可访问）
            filename: 文件名

        Returns:
            Dict: API响应
        """
        logger.info(f"📤 发送图片到群聊 {chat_id}: {filename}")

        # 确定MIME类型
        mime_type = 'image/jpeg' if filename.endswith(('.jpg', '.jpeg')) else 'image/png'

        # 与Node.js版本完全一致的格式
        request_data = {
            'type': 'image',
            'content': '[图片]',
            'media': {
                'url': image_url,
                'filename': filename,
                'mimeType': mime_type
            },
            'status': 'sent'
        }

        result = await self._request(
            method='POST',
            path=f'/api/bot/send/{chat_id}',  # 修复：与Node.js版本一致
            json_data=request_data
        )

        if result.get('success'):
            logger.info(f"✅ 图片发送成功")
        else:
            logger.error(f"❌ 图片发送失败: {result.get('error')}")

        return result

    async def join_chat(self, chat_id: str) -> Dict[str, Any]:
        """
        加入群聊

        Args:
            chat_id: 群聊ID

        Returns:
            Dict: API响应
        """
        logger.info(f"🤝 加入群聊: {chat_id}")

        result = await self._request(
            method='POST',
            path=f'/api/bot/join/{chat_id}'
        )

        if result.get('success'):
            logger.info(f"✅ 已加入群聊 {chat_id}")
        else:
            logger.error(f"❌ 加入群聊失败: {result.get('error')}")

        return result

    async def get_chat_members(self, chat_id: str) -> Dict[str, Any]:
        """
        获取群聊成员列表

        Args:
            chat_id: 群聊ID

        Returns:
            Dict: API响应，包含成员列表
        """
        logger.info(f"👥 获取群聊成员: {chat_id}")

        result = await self._request(
            method='GET',
            path=f'/api/bot/chat/{chat_id}/members'
        )

        if result.get('success'):
            member_count = len(result.get('members', []))
            logger.info(f"✅ 获取群聊成员成功，共 {member_count} 人")
        else:
            logger.error(f"❌ 获取群聊成员失败: {result.get('error')}")

        return result

    async def register_bot(
        self,
        name: str,
        description: str,
        webhook_url: str,
        webhook_secret: str
    ) -> Dict[str, Any]:
        """
        注册机器人

        Args:
            name: 机器人名称
            description: 机器人描述
            webhook_url: Webhook URL
            webhook_secret: Webhook密钥

        Returns:
            Dict: API响应，包含Bot凭证
        """
        logger.info(f"🤖 注册机器人: {name}")

        result = await self._request(
            method='POST',
            path='/api/bot/register',
            json_data={
                'name': name,
                'description': description,
                'developer': {
                    'name': '游戏开发者',
                    'email': 'game@example.com'
                },
                'webhook': {
                    'url': webhook_url,
                    'secret': webhook_secret,
                    'events': ['message.received', 'group.created', 'member.joined']
                },
                'permissions': {
                    'canSendMessage': True,
                    'canReceiveMessage': True,
                    'canAccessUserInfo': True,
                    'canAccessChatHistory': False
                }
            }
        )

        if result.get('success'):
            logger.info(f"✅ 机器人注册成功")
            logger.info(f"   Bot ID: {result.get('bot', {}).get('id')}")
        else:
            logger.error(f"❌ 机器人注册失败: {result.get('error')}")

        return result


# 全局单例
_bot_api_client: Optional[BotApiClient] = None


def get_bot_api_client() -> BotApiClient:
    """获取BotApiClient单例"""
    global _bot_api_client
    if _bot_api_client is None:
        _bot_api_client = BotApiClient()
    return _bot_api_client
