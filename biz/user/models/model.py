"""
User模型定义
对应数据库表：users
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class RedPacketSettings(BaseModel):
    """红包设置"""
    enabled: bool = True
    max_amount: Decimal = Field(default=Decimal("1000.00"), description="最大金额")
    min_amount: Decimal = Field(default=Decimal("10.00"), description="最小金额")
    daily_limit: int = Field(default=5, description="每日限额")


class UserReportDetails(BaseModel):
    """用户报表详情"""
    total_bets: Decimal = Field(default=Decimal("0.00"), description="总投注")
    total_winnings: Decimal = Field(default=Decimal("0.00"), description="总赢利")
    total_losses: Decimal = Field(default=Decimal("0.00"), description="总损失")
    last_bet_date: Optional[datetime] = None


class User(BaseModel):
    """用户模型（数据库表对应）"""
    id: str = Field(..., description="用户ID（悦聊平台ID）")
    username: str = Field(..., description="用户名")
    chat_id: str = Field(..., description="群聊ID")
    balance: Decimal = Field(default=Decimal("0.00"), description="余额")
    score: int = Field(default=0, description="积分")
    rebate_ratio: Decimal = Field(default=Decimal("0.02"), description="回水比例")
    join_date: datetime = Field(default_factory=datetime.now, description="加入日期")
    status: str = Field(default="活跃", description="状态：活跃/禁用")
    role: str = Field(default="normal", description="角色：normal/admin")
    created_by: str = Field(default="admin", description="创建者")
    is_bot: bool = Field(default=False, description="是否为机器人")
    bot_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="机器人配置")
    is_new: bool = Field(default=True, description="是否为新用户")
    marked_read_at: Optional[datetime] = None
    red_packet_settings: Optional[RedPacketSettings] = Field(
        default_factory=RedPacketSettings, description="红包设置"
    )
    report_details: Optional[UserReportDetails] = Field(
        default_factory=UserReportDetails, description="报表详情"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class UserCreate(BaseModel):
    """创建用户请求模型"""
    id: str = Field(..., description="用户ID（悦聊平台ID）")
    username: str = Field(..., description="用户名")
    chat_id: str = Field(..., description="群聊ID")
    balance: Optional[Decimal] = Field(default=Decimal("0.00"))
    score: Optional[int] = 0
    rebate_ratio: Optional[Decimal] = Field(default=Decimal("0.02"))
    status: Optional[str] = "活跃"
    role: Optional[str] = "normal"
    created_by: Optional[str] = "admin"
    is_bot: Optional[bool] = False
    bot_config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    username: Optional[str] = None
    balance: Optional[Decimal] = None
    score: Optional[int] = None
    rebate_ratio: Optional[Decimal] = None
    status: Optional[str] = None
    role: Optional[str] = None
    is_bot: Optional[bool] = None
    bot_config: Optional[Dict[str, Any]] = None
    is_new: Optional[bool] = None
    marked_read_at: Optional[datetime] = None
    red_packet_settings: Optional[Dict[str, Any]] = None


class UserStats(BaseModel):
    """用户统计信息"""
    user_id: str
    username: str
    chat_id: str
    balance: Decimal
    total_bets: Decimal
    total_winnings: Decimal
    win_rate: float
    bet_count: int
    last_bet_date: Optional[datetime]

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat() if v else None
        }
