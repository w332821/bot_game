"""
Bet模型定义
对应数据库表：bets
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class Bet(BaseModel):
    """投注模型（数据库表对应）"""
    id: str = Field(..., description="投注ID")
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    chat_id: str = Field(..., description="群聊ID")
    game_type: str = Field(default="lucky8", description="游戏类型：lucky8/liuhecai")
    lottery_type: str = Field(..., description="投注类型：fan/zheng/nian/jiao/tong/tema等")
    bet_number: Optional[int] = Field(None, description="投注号码")
    bet_amount: Decimal = Field(..., description="投注金额")
    odds: Decimal = Field(..., description="赔率")
    status: str = Field(default="active", description="状态：active/cancelled")
    result: str = Field(default="pending", description="结果：pending/win/lose/tie")
    pnl: Decimal = Field(default=Decimal("0.00"), description="盈亏金额")
    issue: Optional[str] = Field(None, description="期号")
    draw_number: Optional[int] = Field(None, description="开奖号码")
    draw_code: Optional[str] = Field(None, description="开奖号码串")
    created_at: datetime = Field(default_factory=datetime.now)
    settled_at: Optional[datetime] = Field(None, description="结算时间")

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class BetCreate(BaseModel):
    """创建投注请求模型"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    chat_id: str = Field(..., description="群聊ID")
    game_type: str = Field(default="lucky8", description="游戏类型")
    lottery_type: str = Field(..., description="投注类型")
    bet_number: Optional[int] = None
    bet_amount: Decimal = Field(..., description="投注金额")
    odds: Decimal = Field(..., description="赔率")
    issue: Optional[str] = None


class BetUpdate(BaseModel):
    """更新投注请求模型"""
    status: Optional[str] = None
    result: Optional[str] = None
    pnl: Optional[Decimal] = None
    draw_number: Optional[int] = None
    draw_code: Optional[str] = None
    settled_at: Optional[datetime] = None


class BetSettleResult(BaseModel):
    """投注结算结果"""
    bet_id: str
    user_id: str
    username: str
    chat_id: str
    old_balance: Decimal
    new_balance: Decimal
    result: str
    pnl: Decimal
    settled_at: datetime

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
