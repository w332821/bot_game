"""
Bet数据库表模型
对应 Node.js 中的 bets数组
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class BetTable(SQLModel, table=True):
    """投注数据库表"""
    __tablename__ = "bets"

    id: str = Field(primary_key=True, description="投注ID")
    user_id: str = Field(..., description="用户ID", index=True)
    username: str = Field(..., description="用户名")
    chat_id: str = Field(..., description="群聊ID", index=True)
    game_type: str = Field(default="lucky8", description="游戏类型：lucky8/liuhecai")
    lottery_type: str = Field(..., description="投注类型：fan/zheng/nian/jiao/tong/tema等")
    bet_number: Optional[int] = Field(None, description="投注号码")
    bet_amount: Decimal = Field(..., description="投注金额", max_digits=15, decimal_places=2)
    odds: Decimal = Field(..., description="赔率", max_digits=10, decimal_places=2)
    status: str = Field(default="active", description="状态：active/cancelled")
    result: str = Field(default="pending", description="结果：pending/win/lose/tie")
    pnl: Decimal = Field(default=Decimal("0.00"), description="盈亏金额", max_digits=15, decimal_places=2)
    issue: Optional[str] = Field(None, description="期号", index=True)
    draw_number: Optional[int] = Field(None, description="开奖号码")
    draw_code: Optional[str] = Field(None, description="开奖号码串")
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    settled_at: Optional[datetime] = Field(None, description="结算时间")
