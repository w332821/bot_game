"""代理结算计算器"""
from typing import Dict
from decimal import Decimal


class SettlementCalculator:
    """代理结算计算逻辑"""

    @staticmethod
    def calculate_agent_settlement(
        bet_amount: Decimal,
        win_loss: Decimal,
        rebate: Decimal,
        share_percentage: Decimal,
        earn_rebate_mode: str
    ) -> Dict[str, Decimal]:
        """
        计算代理结算相关字段

        参数:
            bet_amount: 投注金额
            win_loss: 输赢金额（负数表示输）
            rebate: 退水金额
            share_percentage: 占成比例（0-100）
            earn_rebate_mode: 赚水模式 full/partial/none

        返回:
            {
                "receivableDownline": 应收下线,
                "share": 占成比例,
                "actualShareAmount": 实占金额,
                "actualShareWinLoss": 实占输赢,
                "actualShareRebate": 实占退水,
                "earnedRebate": 赚水,
                "profitLoss": 盈亏
            }
        """
        share = share_percentage / Decimal("100")  # 转换为小数

        # 实占金额
        actual_share_amount = bet_amount * share

        # 实占输赢
        actual_share_win_loss = win_loss * share

        # 实占退水
        actual_share_rebate = rebate * share

        # 赚水（根据模式）
        if earn_rebate_mode == "full":
            earned_rebate = rebate  # 全额赚取
        elif earn_rebate_mode == "partial":
            earned_rebate = rebate * share  # 按占成比例赚取
        else:
            earned_rebate = Decimal("0.00")  # 不赚取

        # 应收下线 = 下线输给平台的钱 * 占成比例
        receivable_downline = abs(win_loss) * share if win_loss < 0 else Decimal("0.00")

        # 盈亏 = 实占输赢 + 赚水
        profit_loss = actual_share_win_loss + earned_rebate

        return {
            "receivableDownline": receivable_downline,
            "share": share_percentage,
            "actualShareAmount": actual_share_amount,
            "actualShareWinLoss": actual_share_win_loss,
            "actualShareRebate": actual_share_rebate,
            "earnedRebate": earned_rebate,
            "profitLoss": profit_loss
        }
