#!/bin/bash

# Webhook测试脚本
# 用于快速测试App端的Webhook功能

BASE_URL="http://localhost:3003"

echo "🧪 Game Bot Webhook 测试脚本"
echo "=============================="
echo ""
echo "请确保服务已启动: ./start.sh"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4

    echo -e "${YELLOW}测试: ${name}${NC}"
    echo "端点: ${method} ${endpoint}"

    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "${BASE_URL}${endpoint}")
    else
        response=$(curl -s -w "\n%{http_code}" -X "${method}" \
            -H "Content-Type: application/json" \
            -d "${data}" \
            "${BASE_URL}${endpoint}")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ 成功 (HTTP $http_code)${NC}"
        echo "响应: $body"
    else
        echo -e "${RED}❌ 失败 (HTTP $http_code)${NC}"
        echo "响应: $body"
    fi
    echo ""
}

# 1. 测试健康检查
test_endpoint "健康检查" "GET" "/health" ""

# 2. 测试群聊创建
test_endpoint "群聊创建事件" "POST" "/webhook" '{
  "event": "group.created",
  "data": {
    "chat": {
      "id": "test_chat_001",
      "name": "测试群聊",
      "type": "group"
    }
  }
}'

# 3. 测试成员加入
test_endpoint "成员加入事件" "POST" "/webhook" '{
  "event": "member.joined",
  "data": {
    "member": {
      "id": "test_user_001",
      "name": "测试用户",
      "isBot": false
    },
    "chat": {
      "id": "test_chat_001",
      "name": "测试群聊"
    }
  }
}'

# 4. 测试查询余额
test_endpoint "查询余额消息" "POST" "/webhook" '{
  "event": "message.received",
  "data": {
    "message": {
      "id": "msg_001",
      "content": "查",
      "chat": {
        "id": "test_chat_001",
        "name": "测试群聊"
      },
      "sender": {
        "_id": "test_user_001",
        "id": "test_user_001",
        "name": "测试用户",
        "isBot": false
      }
    }
  }
}'

# 5. 测试下注
test_endpoint "下注消息(番 3/200)" "POST" "/webhook" '{
  "event": "message.received",
  "data": {
    "message": {
      "id": "msg_002",
      "content": "番 3/200",
      "chat": {
        "id": "test_chat_001",
        "name": "测试群聊"
      },
      "sender": {
        "_id": "test_user_001",
        "id": "test_user_001",
        "name": "测试用户",
        "isBot": false
      }
    }
  }
}'

# 6. 测试排行榜
test_endpoint "排行榜消息" "POST" "/webhook" '{
  "event": "message.received",
  "data": {
    "message": {
      "id": "msg_003",
      "content": "排行",
      "chat": {
        "id": "test_chat_001",
        "name": "测试群聊"
      },
      "sender": {
        "_id": "test_user_001",
        "id": "test_user_001",
        "name": "测试用户",
        "isBot": false
      }
    }
  }
}'

# 7. 测试游戏类型同步
test_endpoint "同步游戏类型" "POST" "/api/sync-gametype" '{
  "chatId": "test_chat_001",
  "gameType": "liuhecai",
  "oldGameType": "lucky8"
}'

echo -e "${GREEN}=============================="
echo "测试完成！"
echo -e "==============================${NC}"
echo ""
echo "提示："
echo "1. 某些测试可能需要真实的Bot API配置才能完全成功"
echo "2. 检查服务日志查看详细信息"
echo "3. 访问 http://localhost:3003/docs 查看完整API文档"
