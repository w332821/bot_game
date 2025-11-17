"""
GameService 单元测试
测试游戏服务的核心业务逻辑
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from biz.game.service.game_service import GameService


@pytest.fixture
def mock_repos():
    """创建mock repositories"""
    return {
        'user_repo': AsyncMock(),
        'bet_repo': AsyncMock(),
        'chat_repo': AsyncMock(),
        'draw_repo': AsyncMock(),
        'odds_repo': AsyncMock()
    }


@pytest.fixture
def mock_bot_client():
    """创建mock Bot API客户端"""
    client = AsyncMock()
    client.send_message = AsyncMock()
    client.send_image = AsyncMock()
    return client


@pytest.fixture
def game_service(mock_repos, mock_bot_client):
    """创建GameService实例"""
    return GameService(
        user_repo=mock_repos['user_repo'],
        bet_repo=mock_repos['bet_repo'],
        chat_repo=mock_repos['chat_repo'],
        draw_repo=mock_repos['draw_repo'],
        odds_repo=mock_repos['odds_repo'],
        bot_client=mock_bot_client
    )


class TestBetParsing:
    """测试下注指令解析"""

    @pytest.mark.asyncio
    async def test_parse_lucky8_fan_bet(self, game_service):
        """测试澳洲幸运8番下注解析"""
        # 测试格式: "番 3/200"
        result = game_service._parse_bet_message("番 3/200", "lucky8")
        assert result is not None
        assert result['lottery_type'] == 'fan'
        assert result['bet_number'] == 3
        assert result['bet_amount'] == Decimal('200')

        # 测试格式: "3番200"
        result = game_service._parse_bet_message("3番200", "lucky8")
        assert result is not None
        assert result['lottery_type'] == 'fan'
        assert result['bet_number'] == 3
        assert result['bet_amount'] == Decimal('200')

    @pytest.mark.asyncio
    async def test_parse_lucky8_zheng_bet(self, game_service):
        """测试澳洲幸运8正下注解析"""
        # 测试格式: "正1/200"
        result = game_service._parse_bet_message("正1/200", "lucky8")
        assert result is not None
        assert result['lottery_type'] == 'zheng'
        assert result['bet_number'] == 1
        assert result['bet_amount'] == Decimal('200')

        # 测试格式: "1/200" (简写)
        result = game_service._parse_bet_message("1/200", "lucky8")
        assert result is not None
        assert result['lottery_type'] == 'zheng'

    @pytest.mark.asyncio
    async def test_parse_lucky8_dan_shuang(self, game_service):
        """测试澳洲幸运8单双下注解析"""
        # 测试单
        result = game_service._parse_bet_message("单200", "lucky8")
        assert result is not None
        assert result['lottery_type'] == 'dan'
        assert result['bet_amount'] == Decimal('200')

        # 测试双
        result = game_service._parse_bet_message("双150", "lucky8")
        assert result is not None
        assert result['lottery_type'] == 'shuang'
        assert result['bet_amount'] == Decimal('150')

    @pytest.mark.asyncio
    async def test_parse_liuhecai_number_bet(self, game_service):
        """测试六合彩号码下注解析"""
        result = game_service._parse_bet_message("1/200", "liuhecai")
        assert result is not None
        assert result['lottery_type'] == 'number'
        assert result['bet_number'] == 1
        assert result['bet_amount'] == Decimal('200')

    @pytest.mark.asyncio
    async def test_parse_liuhecai_bose_bet(self, game_service):
        """测试六合彩波色下注解析"""
        # 红波
        result = game_service._parse_bet_message("红波200", "liuhecai")
        assert result is not None
        assert result['lottery_type'] == 'hongbo'
        assert result['bet_amount'] == Decimal('200')

        # 蓝波
        result = game_service._parse_bet_message("蓝波150", "liuhecai")
        assert result is not None
        assert result['lottery_type'] == 'lanbo'

        # 绿波
        result = game_service._parse_bet_message("绿波100", "liuhecai")
        assert result is not None
        assert result['lottery_type'] == 'lvbo'


class TestHandleQueryBalance:
    """测试余额查询"""

    @pytest.mark.asyncio
    async def test_query_balance_success(self, game_service, mock_repos, mock_bot_client):
        """测试成功查询余额"""
        # 模拟用户数据
        mock_repos['user_repo'].get_by_id.return_value = {
            'id': 'user_001',
            'username': '张三',
            'balance': Decimal('1500.50')
        }

        await game_service.handle_query_balance('chat_001', {'id': 'user_001'})

        # 验证发送了消息
        mock_bot_client.send_message.assert_called_once()
        call_args = mock_bot_client.send_message.call_args
        assert 'chat_001' in call_args[0]
        assert '1500.50' in call_args[0][1]

    @pytest.mark.asyncio
    async def test_query_balance_user_not_found(self, game_service, mock_repos, mock_bot_client):
        """测试用户不存在"""
        mock_repos['user_repo'].get_by_id.return_value = None

        await game_service.handle_query_balance('chat_001', {'id': 'user_999'})

        # 验证发送了错误消息
        mock_bot_client.send_message.assert_called_once()
        call_args = mock_bot_client.send_message.call_args
        assert '未找到' in call_args[0][1] or '不存在' in call_args[0][1]


class TestHandleBetMessage:
    """测试下注处理"""

    @pytest.mark.asyncio
    async def test_bet_success(self, game_service, mock_repos, mock_bot_client):
        """测试成功下注"""
        # 模拟用户有足够余额
        mock_repos['user_repo'].get_by_id.return_value = {
            'id': 'user_001',
            'username': '张三',
            'balance': Decimal('1000.00')
        }

        # 模拟群聊数据
        mock_repos['chat_repo'].get_by_id.return_value = {
            'id': 'chat_001',
            'game_type': 'lucky8'
        }

        # 模拟赔率数据
        mock_repos['odds_repo'].get_odds.return_value = Decimal('3.00')

        # 模拟创建下注成功
        mock_repos['bet_repo'].create.return_value = {'id': 'bet_001'}

        # 模拟更新余额成功
        mock_repos['user_repo'].update_balance.return_value = True

        await game_service.handle_bet_message(
            'chat_001',
            '番 3/200',
            {'id': 'user_001', 'name': '张三'}
        )

        # 验证创建了下注记录
        mock_repos['bet_repo'].create.assert_called_once()

        # 验证更新了余额
        mock_repos['user_repo'].update_balance.assert_called_once()
        call_args = mock_repos['user_repo'].update_balance.call_args
        assert call_args[0][0] == 'user_001'
        assert call_args[0][1] == Decimal('-200')

        # 验证发送了确认消息
        mock_bot_client.send_message.assert_called()

    @pytest.mark.asyncio
    async def test_bet_insufficient_balance(self, game_service, mock_repos, mock_bot_client):
        """测试余额不足"""
        # 模拟用户余额不足
        mock_repos['user_repo'].get_by_id.return_value = {
            'id': 'user_001',
            'username': '张三',
            'balance': Decimal('100.00')  # 余额不足
        }

        mock_repos['chat_repo'].get_by_id.return_value = {
            'id': 'chat_001',
            'game_type': 'lucky8'
        }

        await game_service.handle_bet_message(
            'chat_001',
            '番 3/200',  # 下注200，但只有100
            {'id': 'user_001', 'name': '张三'}
        )

        # 验证没有创建下注记录
        mock_repos['bet_repo'].create.assert_not_called()

        # 验证发送了余额不足消息
        mock_bot_client.send_message.assert_called()
        call_args = mock_bot_client.send_message.call_args
        assert '余额不足' in call_args[0][1]


class TestHandleCancelBet:
    """测试取消下注"""

    @pytest.mark.asyncio
    async def test_cancel_bet_success(self, game_service, mock_repos, mock_bot_client):
        """测试成功取消下注"""
        # 模拟有pending的下注
        mock_repos['bet_repo'].get_user_pending_bets.return_value = [
            {
                'id': 'bet_001',
                'bet_amount': Decimal('200.00'),
                'status': 'pending'
            },
            {
                'id': 'bet_002',
                'bet_amount': Decimal('150.00'),
                'status': 'pending'
            }
        ]

        # 模拟取消成功
        mock_repos['bet_repo'].update.return_value = True
        mock_repos['user_repo'].update_balance.return_value = True

        await game_service.handle_cancel_bet(
            'chat_001',
            {'id': 'user_001', 'name': '张三'}
        )

        # 验证取消了所有pending下注
        assert mock_repos['bet_repo'].update.call_count == 2

        # 验证退款了
        assert mock_repos['user_repo'].update_balance.call_count == 2

        # 验证发送了确认消息
        mock_bot_client.send_message.assert_called()

    @pytest.mark.asyncio
    async def test_cancel_bet_no_pending(self, game_service, mock_repos, mock_bot_client):
        """测试没有待取消的下注"""
        # 模拟没有pending下注
        mock_repos['bet_repo'].get_user_pending_bets.return_value = []

        await game_service.handle_cancel_bet(
            'chat_001',
            {'id': 'user_001', 'name': '张三'}
        )

        # 验证没有更新操作
        mock_repos['bet_repo'].update.assert_not_called()
        mock_repos['user_repo'].update_balance.assert_not_called()

        # 验证发送了提示消息
        mock_bot_client.send_message.assert_called()


class TestExecuteDraw:
    """测试开奖结算"""

    @pytest.mark.asyncio
    async def test_execute_draw_success(self, game_service, mock_repos, mock_bot_client):
        """测试成功开奖"""
        # 模拟群聊数据
        mock_repos['chat_repo'].get_by_id.return_value = {
            'id': 'chat_001',
            'game_type': 'lucky8'
        }

        # 模拟有待结算的下注
        mock_repos['bet_repo'].get_pending_bets_by_issue.return_value = [
            {
                'id': 'bet_001',
                'user_id': 'user_001',
                'lottery_type': 'fan',
                'bet_number': 3,
                'bet_amount': Decimal('200.00'),
                'odds': Decimal('3.00')
            }
        ]

        # 模拟开奖API返回
        with patch('external.draw_api_client.get_draw_api_client') as mock_draw_api:
            mock_client = AsyncMock()
            mock_client.get_draw_result.return_value = {
                'draw_number': '01,05,12,18,23,30,35,42,45,50,55,60,65,70,72,75,78,80',
                'draw_code': '01,05,12,18,23,30,35,42',
                'special_number': 12
            }
            mock_draw_api.return_value = mock_client

            # 模拟创建开奖记录
            mock_repos['draw_repo'].create.return_value = {'id': 'draw_001'}

            await game_service.execute_draw('chat_001')

            # 验证创建了开奖记录
            mock_repos['draw_repo'].create.assert_called_once()

            # 验证更新了下注状态
            mock_repos['bet_repo'].update.assert_called()

            # 验证发送了开奖公告
            mock_bot_client.send_message.assert_called()


class TestHandleLeaderboard:
    """测试排行榜"""

    @pytest.mark.asyncio
    async def test_leaderboard_display(self, game_service, mock_repos, mock_bot_client):
        """测试排行榜展示"""
        # 模拟排行榜数据
        mock_repos['user_repo'].get_top_users.return_value = [
            {'username': '张三', 'balance': Decimal('5000.00')},
            {'username': '李四', 'balance': Decimal('3000.00')},
            {'username': '王五', 'balance': Decimal('2000.00')}
        ]

        await game_service.handle_leaderboard('chat_001')

        # 验证发送了排行榜消息
        mock_bot_client.send_message.assert_called_once()
        call_args = mock_bot_client.send_message.call_args
        message = call_args[0][1]

        # 验证消息包含用户名和余额
        assert '张三' in message
        assert '5000' in message
        assert '李四' in message


class TestIssueNumberGeneration:
    """测试期号生成"""

    @pytest.mark.asyncio
    async def test_generate_lucky8_issue(self, game_service, mock_repos):
        """测试澳洲幸运8期号生成"""
        # 模拟今日已有期号
        mock_repos['draw_repo'].get_latest_draw_by_date.return_value = {
            'issue': '20250113001'
        }

        issue = await game_service._generate_issue_number('lucky8')

        # 验证期号格式: YYYYMMDD + 序号
        assert len(issue) == 11
        assert issue[:8] == datetime.now().strftime('%Y%m%d')
        assert issue[-3:] == '002'  # 下一期

    @pytest.mark.asyncio
    async def test_generate_lucky8_first_issue(self, game_service, mock_repos):
        """测试澳洲幸运8第一期"""
        # 模拟今日无期号
        mock_repos['draw_repo'].get_latest_draw_by_date.return_value = None

        issue = await game_service._generate_issue_number('lucky8')

        # 验证第一期
        assert issue[-3:] == '001'

    @pytest.mark.asyncio
    async def test_generate_liuhecai_issue(self, game_service):
        """测试六合彩期号生成"""
        issue = await game_service._generate_issue_number('liuhecai')

        # 验证期号格式: YYYYMMDD
        assert len(issue) == 8
        assert issue == datetime.now().strftime('%Y%m%d')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
