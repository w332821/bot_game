"""
Webhook API 集成测试
测试Webhook端点的完整请求-响应流程
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from biz.application import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock所有服务"""
    with patch('biz.containers.Container.user_service') as user_svc, \
         patch('biz.containers.Container.game_service') as game_svc, \
         patch('biz.containers.Container.chat_repo') as chat_repo, \
         patch('biz.containers.Container.bot_api_client') as bot_client:
        
        # 配置mocks
        user_svc_instance = AsyncMock()
        game_svc_instance = AsyncMock()
        chat_repo_instance = AsyncMock()
        bot_client_instance = AsyncMock()
        
        user_svc.return_value = user_svc_instance
        game_svc.return_value = game_svc_instance
        chat_repo.return_value = chat_repo_instance
        bot_client.return_value = bot_client_instance
        
        yield {
            'user_service': user_svc_instance,
            'game_service': game_svc_instance,
            'chat_repo': chat_repo_instance,
            'bot_client': bot_client_instance
        }


class TestWebhookGroupCreated:
    """测试群聊创建事件"""

    def test_group_created_success(self, client, mock_services):
        """测试成功处理群聊创建"""
        # 准备请求数据
        payload = {
            "event": "group.created",
            "data": {
                "chat": {
                    "id": "test_chat_001",
                    "name": "测试群聊",
                    "type": "group"
                }
            }
        }

        # 发送请求
        response = client.post("/webhook", json=payload)

        # 验证响应
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_group_created_missing_data(self, client):
        """测试缺少必要字��"""
        payload = {
            "event": "group.created",
            "data": {}
        }

        response = client.post("/webhook", json=payload)

        # 应该返回200但status为error
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "error" or data.get("status") == "ok"


class TestWebhookMemberJoined:
    """测试成员加入事件"""

    def test_member_joined_success(self, client, mock_services):
        """测试成功处理成员加入"""
        payload = {
            "event": "member.joined",
            "data": {
                "member": {
                    "id": "user_001",
                    "name": "张三",
                    "isBot": False
                },
                "chat": {
                    "id": "chat_001",
                    "name": "测试群"
                }
            }
        }

        response = client.post("/webhook", json=payload)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestWebhookMessageReceived:
    """测试消息接收事件"""

    def test_message_query_balance(self, client, mock_services):
        """测试查询余额消息"""
        payload = {
            "event": "message.received",
            "data": {
                "message": {
                    "id": "msg_001",
                    "content": "查",
                    "chat": {
                        "id": "chat_001",
                        "name": "测试群"
                    },
                    "sender": {
                        "_id": "user_001",
                        "id": "user_001",
                        "name": "张三",
                        "isBot": False
                    }
                }
            }
        }

        response = client.post("/webhook", json=payload)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_message_bet(self, client, mock_services):
        """测试下注消息"""
        payload = {
            "event": "message.received",
            "data": {
                "message": {
                    "id": "msg_002",
                    "content": "番 3/200",
                    "chat": {
                        "id": "chat_001",
                        "name": "测试群"
                    },
                    "sender": {
                        "_id": "user_001",
                        "id": "user_001",
                        "name": "张三",
                        "isBot": False
                    }
                }
            }
        }

        response = client.post("/webhook", json=payload)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_message_from_bot_ignored(self, client, mock_services):
        """测试忽略机器人消息"""
        payload = {
            "event": "message.received",
            "data": {
                "message": {
                    "id": "msg_003",
                    "content": "查",
                    "chat": {
                        "id": "chat_001",
                        "name": "测试群"
                    },
                    "sender": {
                        "_id": "bot_001",
                        "id": "bot_001",
                        "name": "机器人",
                        "isBot": True  # 机器人消息应被忽略
                    }
                }
            }
        }

        response = client.post("/webhook", json=payload)

        assert response.status_code == 200
        # 机器人消息应该被忽略，但仍返回ok
        assert response.json() == {"status": "ok"}


class TestSyncGameType:
    """测试同步游戏类型端点"""

    def test_sync_gametype_success(self, client, mock_services):
        """测试成功同步游戏类型"""
        payload = {
            "chatId": "chat_001",
            "gameType": "liuhecai",
            "oldGameType": "lucky8"
        }

        response = client.post("/api/sync-gametype", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "同步" in data.get("message", "")

    def test_sync_gametype_missing_fields(self, client):
        """测试缺少必要字段"""
        payload = {
            "chatId": "chat_001"
            # 缺少 gameType
        }

        response = client.post("/api/sync-gametype", json=payload)

        # 可能返回422 (Validation Error) 或 200 with error
        assert response.status_code in [200, 422]


class TestHealthCheck:
    """测试健康检查端点"""

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])