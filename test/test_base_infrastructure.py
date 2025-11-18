"""
测试基础设施：统一响应、错误码、游戏名映射
"""
import pytest
from base.api import success_response, error_response, paginate_response
from base.error_codes import ErrorCode, get_error_message
from base.game_name_mapper import (
    validate_game_name,
    game_name_to_code,
    game_code_to_name,
    validate_game_code,
    VALID_GAMES_CN
)


class TestUnifiedResponse:
    """测试统一响应格式"""

    def test_success_response(self):
        """测试成功响应"""
        response = success_response({"id": 1, "name": "test"})
        assert response["code"] == 200
        assert response["message"] == "操作成功"
        assert response["data"] == {"id": 1, "name": "test"}

    def test_success_response_custom_message(self):
        """测试自定义消息的成功响应"""
        response = success_response({"id": 1}, message="创建成功")
        assert response["code"] == 200
        assert response["message"] == "创建成功"
        assert response["data"] == {"id": 1}

    def test_error_response(self):
        """测试错误响应"""
        response = error_response(404, "资源不存在")
        assert response["code"] == 404
        assert response["message"] == "资源不存在"
        assert response["data"] is None

    def test_error_response_with_data(self):
        """测试带数据的错误响应"""
        response = error_response(400, "参数错误", data={"field": "account"})
        assert response["code"] == 400
        assert response["message"] == "参数错误"
        assert response["data"] == {"field": "account"}

    def test_paginate_response(self):
        """测试分页响应"""
        data = [{"id": 1}, {"id": 2}]
        response = paginate_response(data, total=10, page=1, page_size=2)

        assert response["code"] == 200
        assert response["message"] == "操作成功"
        assert response["data"]["list"] == data
        assert response["data"]["total"] == 10
        assert response["data"]["page"] == 1
        assert response["data"]["pageSize"] == 2

    def test_paginate_response_empty_list(self):
        """测试空列表的分页响应"""
        response = paginate_response([], total=0, page=1, page_size=10)

        assert response["code"] == 200
        assert response["data"]["list"] == []
        assert response["data"]["total"] == 0

    def test_paginate_response_with_summary(self):
        """测试带汇总的分页响应"""
        data = [{"id": 1}]
        summary = {"totalAmount": 1000.00, "totalCount": 10}
        response = paginate_response(data, 1, 1, 10, summary=summary)

        assert "summary" in response["data"]
        assert response["data"]["summary"] == summary
        assert response["data"]["summary"]["totalAmount"] == 1000.00

    def test_paginate_response_with_cross_page_stats(self):
        """测试带跨页统计的分页响应"""
        data = [{"id": 1}]
        stats = {"depositAmount": 50000.00, "withdrawalAmount": 30000.00}
        response = paginate_response(data, 1, 1, 10, cross_page_stats=stats)

        assert "crossPageStats" in response["data"]
        assert response["data"]["crossPageStats"] == stats
        assert response["data"]["crossPageStats"]["depositAmount"] == 50000.00

    def test_paginate_response_with_both(self):
        """测试同时带汇总和跨页统计的分页响应"""
        data = [{"id": 1}]
        summary = {"totalCount": 5}
        stats = {"total": 100}
        response = paginate_response(data, 1, 1, 10, summary=summary, cross_page_stats=stats)

        assert "summary" in response["data"]
        assert "crossPageStats" in response["data"]


class TestErrorCodes:
    """测试错误码定义"""

    def test_error_code_values(self):
        """测试错误码值正确"""
        assert ErrorCode.SUCCESS == 200
        assert ErrorCode.BAD_REQUEST == 400
        assert ErrorCode.UNAUTHORIZED == 401
        assert ErrorCode.FORBIDDEN == 403
        assert ErrorCode.NOT_FOUND == 404
        assert ErrorCode.INTERNAL_ERROR == 500
        assert ErrorCode.ACCOUNT_OR_PASSWORD_ERROR == 1001
        assert ErrorCode.ACCOUNT_DISABLED == 1003
        assert ErrorCode.ACCOUNT_NOT_EXIST == 1004
        assert ErrorCode.ACCOUNT_ALREADY_EXISTS == 2001
        assert ErrorCode.PASSWORD_FORMAT_ERROR == 2002
        assert ErrorCode.INSUFFICIENT_BALANCE == 2003
        assert ErrorCode.DATA_NOT_FOUND == 3001
        assert ErrorCode.DATA_DELETED == 3002

    def test_get_error_message(self):
        """测试获取错误消息"""
        assert get_error_message(200) == "操作成功"
        assert get_error_message(400) == "请求参数错误"
        assert get_error_message(1001) == "账号或密码错误"
        assert get_error_message(2001) == "账号已存在"
        assert get_error_message(3001) == "数据不存在"
        assert get_error_message(9999, "默认消息") == "默认消息"


class TestGameNameMapper:
    """测试游戏名映射"""

    def test_valid_games_cn_defined(self):
        """测试有效游戏名列表已定义"""
        assert len(VALID_GAMES_CN) == 2
        assert "新奥六合彩" in VALID_GAMES_CN
        assert "168澳洲幸运8" in VALID_GAMES_CN

    def test_validate_game_name_success(self):
        """测试有效游戏名验证通过"""
        assert validate_game_name("新奥六合彩") == "新奥六合彩"
        assert validate_game_name("168澳洲幸运8") == "168澳洲幸运8"

    def test_validate_game_name_failure(self):
        """测试无效游戏名验证失败"""
        with pytest.raises(ValueError, match="游戏名称错误"):
            validate_game_name("无效游戏")

        with pytest.raises(ValueError, match="游戏名称错误"):
            validate_game_name("lucky8")

    def test_game_name_to_code(self):
        """测试中文转代码"""
        assert game_name_to_code("新奥六合彩") == "liuhecai"
        assert game_name_to_code("168澳洲幸运8") == "lucky8"

    def test_game_name_to_code_invalid(self):
        """测试无效中文转代码失败"""
        with pytest.raises(ValueError):
            game_name_to_code("无效游戏")

    def test_game_code_to_name(self):
        """测试代码转中文"""
        assert game_code_to_name("liuhecai") == "新奥六合彩"
        assert game_code_to_name("lucky8") == "168澳洲幸运8"

    def test_game_code_to_name_invalid(self):
        """测试无效代码转中文失败"""
        with pytest.raises(ValueError, match="游戏代码错误"):
            game_code_to_name("invalid_code")

    def test_validate_game_code(self):
        """测试代码验证"""
        assert validate_game_code("liuhecai") == "liuhecai"
        assert validate_game_code("lucky8") == "lucky8"

    def test_validate_game_code_failure(self):
        """测试无效代码验证失败"""
        with pytest.raises(ValueError, match="游戏代码错误"):
            validate_game_code("invalid_code")

    def test_bidirectional_mapping(self):
        """测试双向映射一致性"""
        # 测试：中文 -> 代码 -> 中文
        for game_cn in VALID_GAMES_CN:
            code = game_name_to_code(game_cn)
            assert game_code_to_name(code) == game_cn

        # 测试：代码 -> 中文 -> 代码
        codes = ["liuhecai", "lucky8"]
        for code in codes:
            game_cn = game_code_to_name(code)
            assert game_name_to_code(game_cn) == code
