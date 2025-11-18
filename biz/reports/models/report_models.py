"""
报表模块数据模型
定义所有报表的请求和响应模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from base.game_name_mapper import VALID_GAMES_CN, validate_game_name


# ===== 财务总报表模型 =====

class FinancialSummaryResponse(BaseModel):
    """财务总报表响应"""
    depositAmount: Decimal = Field(..., description="存款金额")
    withdrawalAmount: Decimal = Field(..., description="取款金额")
    bonus: Decimal = Field(..., description="优惠金额")
    irregularBet: Decimal = Field(..., description="异常注单金额")
    returnAmount: Decimal = Field(..., description="返还金额")
    handlingFee: Decimal = Field(..., description="手续费")
    depositWithdrawalFee: Decimal = Field(..., description="存取款手续费")
    winLoss: Decimal = Field(..., description="输赢金额")
    profit: Decimal = Field(..., description="利润")
    totalBetAmount: Decimal = Field(..., description="总投注金额")
    totalRebate: Decimal = Field(..., description="总退水金额")


# ===== 财务报表模型 =====

class FinancialReportItem(BaseModel):
    """财务报表列表项"""
    account: str = Field(..., description="账号")
    accountName: str = Field(..., description="账户名称")
    gameType: str = Field(..., description="游戏类型(中文)")
    betAmount: Decimal = Field(..., description="投注金额")
    validAmount: Decimal = Field(..., description="有效金额")
    rebate: Decimal = Field(..., description="退水")
    winLoss: Decimal = Field(..., description="输赢")
    depositAmount: Decimal = Field(default=Decimal("0.00"), description="存款金额")
    withdrawalAmount: Decimal = Field(default=Decimal("0.00"), description="取款金额")


class CrossPageStats(BaseModel):
    """跨页统计（计算所有页的汇总）"""
    totalBetAmount: Decimal = Field(..., description="总投注金额")
    totalValidAmount: Decimal = Field(..., description="总有效金额")
    totalRebate: Decimal = Field(..., description="总退水")
    totalWinLoss: Decimal = Field(..., description="总输赢")
    totalDeposit: Decimal = Field(..., description="总存款")
    totalWithdrawal: Decimal = Field(..., description="总取款")


# ===== 输赢报表模型 =====

class WinLossReportItem(BaseModel):
    """输赢报表列表项"""
    account: str = Field(..., description="账号")
    accountName: str = Field(..., description="账户名称")
    gameType: str = Field(..., description="游戏类型(中文)")
    betAmount: Decimal = Field(..., description="投注金额")
    validAmount: Decimal = Field(..., description="有效金额")
    rebate: Decimal = Field(..., description="退水")
    winLoss: Decimal = Field(..., description="输赢")

    @validator('gameType')
    def validate_game_type(cls, v):
        """验证游戏名称必须是中文"""
        if v and v not in VALID_GAMES_CN:
            raise ValueError(f"游戏类型必须是{VALID_GAMES_CN}之一")
        return v


# ===== 代理输赢报表模型 =====

class AgentWinLossReportItem(BaseModel):
    """代理输赢报表列表项"""
    account: str = Field(..., description="代理账号")
    accountName: str = Field(..., description="代理名称")
    gameType: str = Field(..., description="游戏类型(中文)")
    betAmount: Decimal = Field(..., description="投注金额")
    validAmount: Decimal = Field(..., description="有效金额")
    rebate: Decimal = Field(..., description="退水")
    winLoss: Decimal = Field(..., description="输赢")
    subordinateCount: int = Field(default=0, description="下级人数")

    @validator('gameType')
    def validate_game_type(cls, v):
        """验证游戏名称必须是中文"""
        if v and v not in VALID_GAMES_CN:
            raise ValueError(f"游戏类型必须是{VALID_GAMES_CN}之一")
        return v


# ===== 存取款报表模型 =====

class DepositWithdrawalReportItem(BaseModel):
    """存取款报表列表项"""
    account: str = Field(..., description="账号")
    accountName: str = Field(..., description="账户名称")
    transactionTime: str = Field(..., description="交易时间 YYYY-MM-DD HH:mm:ss")
    transactionType: str = Field(..., description="交易类型: deposit/withdrawal")
    amount: Decimal = Field(..., description="金额")
    fee: Decimal = Field(default=Decimal("0.00"), description="手续费")
    status: str = Field(..., description="状态: success/failed/processing/cancelled")
    processor: Optional[str] = Field(None, description="处理人")


# ===== 分类报表模型 =====

class CategoryReportItem(BaseModel):
    """分类报表列表项"""
    lotteryType: str = Field(..., description="彩种(中文)")
    gameplay: str = Field(..., description="玩法名称")
    betCount: int = Field(..., description="注单数量")
    betAmount: Decimal = Field(..., description="投注金额")
    validAmount: Decimal = Field(..., description="有效金额")
    winLoss: Decimal = Field(..., description="输赢")

    @validator('lotteryType')
    def validate_lottery_type(cls, v):
        """验证彩种名称必须是中文"""
        if v and v not in VALID_GAMES_CN:
            raise ValueError(f"彩种必须是{VALID_GAMES_CN}之一")
        return v


# ===== 下线明细报表模型 =====

class DownlineMemberItem(BaseModel):
    """下线会员列表项"""
    account: str = Field(..., description="账号")
    accountName: str = Field(..., description="账户名称")
    level: int = Field(..., description="级别")
    openTime: str = Field(..., description="开户时间 YYYY-MM-DD HH:mm:ss")
    betAmount: Decimal = Field(default=Decimal("0.00"), description="投注金额")
    winLoss: Decimal = Field(default=Decimal("0.00"), description="输赢")


class DownlineAgentItem(BaseModel):
    """下线代理列表项"""
    account: str = Field(..., description="账号")
    accountName: str = Field(..., description="账户名称")
    level: int = Field(..., description="级别")
    openTime: str = Field(..., description="开户时间 YYYY-MM-DD HH:mm:ss")
    subordinateCount: int = Field(default=0, description="下级人数")
    betAmount: Decimal = Field(default=Decimal("0.00"), description="投注金额")
    winLoss: Decimal = Field(default=Decimal("0.00"), description="输赢")


class DownlineDetailsResponse(BaseModel):
    """下线明细报表响应（特殊结构）"""
    members: dict = Field(..., description="会员列表 {list, total, page, pageSize}")
    agents: dict = Field(..., description="代理列表 {list, total, page, pageSize}")


# ===== 重新统计请求模型 =====

class RecalculateRequest(BaseModel):
    """重新统计请求"""
    dateStart: str = Field(..., description="开始日期 YYYY-MM-DD")
    dateEnd: str = Field(..., description="结束日期 YYYY-MM-DD")
