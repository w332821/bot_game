"""
报表模块API测试
测试9个报表接口
"""
import pytest
from httpx import AsyncClient
from biz.application import app
from datetime import datetime, timedelta


class TestFinancialSummary:
    """测试财务总报表接口"""

    @pytest.mark.asyncio
    async def test_financial_summary_success(self, auth_headers):
        """测试财务总报表查询成功"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/financial-summary",
                params={"dateStart": today, "dateEnd": today}
            )

            assert response.status_code == 200
            data = response.json()

            # 验证响应格式
            assert data["code"] == 200
            assert "data" in data

            # 验证数据字段
            expected_fields = [
                "depositAmount", "withdrawalAmount", "bonus", "irregularBet",
                "returnAmount", "handlingFee", "depositWithdrawalFee",
                "winLoss", "profit", "totalBetAmount", "totalRebate"
            ]
            for field in expected_fields:
                assert field in data["data"]

    @pytest.mark.asyncio
    async def test_financial_summary_with_plate(self, auth_headers):
        """测试财务总报表 - 带盘口筛选"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/financial-summary",
                params={
                    "dateStart": today,
                    "dateEnd": today,
                    "plate": "A"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

    @pytest.mark.asyncio
    async def test_financial_summary_invalid_plate(self, auth_headers):
        """测试财务总报表 - 无效盘口"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/financial-summary",
                params={
                    "dateStart": today,
                    "dateEnd": today,
                    "plate": "Z"  # 无效盘口
                }
            )

            # FastAPI验证应该返回422
            assert response.status_code == 422


class TestFinancialReport:
    """测试财务报表接口(含跨页统计)"""

    @pytest.mark.asyncio
    async def test_financial_report_pagination(self, auth_headers):
        """测试财务报表分页"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/financial",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today
                }
            )

            assert response.status_code == 200
            data = response.json()

            # 验证分页响应格式
            assert data["code"] == 200
            assert "list" in data["data"]
            assert "total" in data["data"]
            assert "page" in data["data"]
            assert "pageSize" in data["data"]

            # 验证跨页统计存在
            assert "crossPageStats" in data["data"]

    @pytest.mark.asyncio
    async def test_financial_report_cross_page_stats(self, auth_headers):
        """测试财务报表跨页统计字段"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/financial",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today
                }
            )

            assert response.status_code == 200
            data = response.json()

            # 验证跨页统计包含所有必需字段
            cross_stats = data["data"]["crossPageStats"]
            expected_fields = [
                "totalBetAmount", "totalValidAmount", "totalRebate",
                "totalWinLoss", "totalDeposit", "totalWithdrawal"
            ]
            for field in expected_fields:
                assert field in cross_stats

    @pytest.mark.asyncio
    async def test_financial_report_with_account_filter(self, auth_headers):
        """测试财务报表 - 账号筛选"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/financial",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today,
                    "account": "test_account"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200


class TestWinLossReport:
    """测试输赢报表接口"""

    @pytest.mark.asyncio
    async def test_win_loss_report_basic(self):
        """测试输赢报表基本查询"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/win-loss",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert "list" in data["data"]
            assert "total" in data["data"]

    @pytest.mark.asyncio
    async def test_win_loss_report_with_valid_game_types(self):
        """测试输赢报表 - 有效的游戏类型(中文)"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/win-loss",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today,
                    "gameTypes": ["新奥六合彩", "168澳洲幸运8"]
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

    @pytest.mark.asyncio
    async def test_win_loss_report_with_invalid_game_type(self, auth_headers):
        """测试输赢报表 - 无效的游戏类型(英文)"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/win-loss",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today,
                    "gameTypes": ["liuhecai"]  # 应该是中文
                }
            )

            assert response.status_code == 200
            data = response.json()
            # 应该返回错误
            assert data["code"] == 400


class TestAgentWinLossReport:
    """测试代理输赢报表接口"""

    @pytest.mark.asyncio
    async def test_agent_win_loss_report_basic(self, auth_headers):
        """测试代理输赢报表基本查询"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/agent-win-loss",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200


class TestDepositWithdrawalReport:
    """测试存取款报表接口"""

    @pytest.mark.asyncio
    async def test_deposit_withdrawal_report_all(self, auth_headers):
        """测试存取款报表 - 全部"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/deposit-withdrawal",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

    @pytest.mark.asyncio
    async def test_deposit_withdrawal_report_deposit_only(self):
        """测试存取款报表 - 仅存款"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/deposit-withdrawal",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today,
                    "transactionType": "deposit"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

    @pytest.mark.asyncio
    async def test_deposit_withdrawal_report_withdrawal_only(self):
        """测试存取款报表 - 仅取款"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/deposit-withdrawal",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today,
                    "transactionType": "withdrawal"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200


class TestCategoryReport:
    """测试分类报表接口"""

    @pytest.mark.asyncio
    async def test_category_report_basic(self):
        """测试分类报表基本查询"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/category",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

    @pytest.mark.asyncio
    async def test_category_report_with_lottery_type(self):
        """测试分类报表 - 指定彩种"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/category",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today,
                    "lotteryType": "新奥六合彩"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

    @pytest.mark.asyncio
    async def test_category_report_invalid_lottery_type(self, auth_headers):
        """测试分类报表 - 无效彩种"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/category",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "dateStart": today,
                    "dateEnd": today,
                    "lotteryType": "invalid_game"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 400


class TestDownlineDetailsReport:
    """测试下线明细报表接口"""

    @pytest.mark.asyncio
    async def test_downline_details_special_structure(self):
        """测试下线明细报表 - 特殊结构"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            response = await client.get(
                "/api/reports/downline-details",
                params={
                    "page": 1,
                    "pageSize": 20,
                    "account": "test_account"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

            # 验证特殊结构: members + agents
            assert "members" in data["data"]
            assert "agents" in data["data"]

            # 验证members结构
            members = data["data"]["members"]
            assert "list" in members
            assert "total" in members
            assert "page" in members
            assert "pageSize" in members

            # 验证agents结构
            agents = data["data"]["agents"]
            assert "list" in agents
            assert "total" in agents
            assert "page" in agents
            assert "pageSize" in agents


class TestRecalculateFinancialSummary:
    """测试重新统计财务总报表接口"""

    @pytest.mark.asyncio
    async def test_recalculate_success(self):
        """测试重新统计成功"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.post(
                "/api/reports/financial-summary/recalculate",
                json={
                    "dateStart": today,
                    "dateEnd": today
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert "重新统计" in data["message"] or "启动" in data["message"]


class TestExportCSV:
    """测试CSV导出接口"""

    @pytest.mark.asyncio
    async def test_export_financial_csv(self, auth_headers):
        """测试导出财务报表CSV"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/export/financial",
                params={
                    "dateStart": today,
                    "dateEnd": today
                }
            )

            assert response.status_code == 200
            # 验证CSV响应头
            assert "text/csv" in response.headers.get("content-type", "")
            assert "Content-Disposition" in response.headers
            assert "financial_" in response.headers["Content-Disposition"]

    @pytest.mark.asyncio
    async def test_export_win_loss_csv(self, auth_headers):
        """测试导出输赢报表CSV"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/export/win-loss",
                params={
                    "dateStart": today,
                    "dateEnd": today
                }
            )

            assert response.status_code == 200
            assert "text/csv" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_export_invalid_type(self, auth_headers):
        """测试导出无效类型"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await client.get(
                "/api/reports/export/invalid_type",
                params={
                    "dateStart": today,
                    "dateEnd": today
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 400


class TestReportResponseFormat:
    """测试报表接口响应格式一致性"""

    @pytest.mark.asyncio
    async def test_all_reports_use_unified_response_format(self, auth_headers):
        """测试所有报表使用统一响应格式"""
        async with AsyncClient(app=app, base_url="http://test", headers=auth_headers) as client:
            today = datetime.now().strftime("%Y-%m-%d")

            # 测试所有非导出接口
            endpoints = [
                "/api/reports/financial-summary",
                "/api/reports/financial",
                "/api/reports/win-loss",
                "/api/reports/agent-win-loss",
                "/api/reports/deposit-withdrawal",
                "/api/reports/category",
                "/api/reports/downline-details",
            ]

            for endpoint in endpoints:
                params = {
                    "dateStart": today,
                    "dateEnd": today
                }
                if "financial-summary" not in endpoint and "downline-details" not in endpoint:
                    params["page"] = 1
                    params["pageSize"] = 20
                if "downline-details" in endpoint:
                    params["account"] = "test"

                response = await client.get(endpoint, params=params)
                data = response.json()

                # 验证统一响应格式
                assert "code" in data, f"{endpoint} missing 'code'"
                assert "message" in data, f"{endpoint} missing 'message'"
                assert "data" in data, f"{endpoint} missing 'data'"
