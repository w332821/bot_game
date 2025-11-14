"""
Chat数据库表模型
对应 Node.js 中的 chats Map
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class ChatTable(SQLModel, table=True):
    """群聊数据库表"""
    __tablename__ = "chats"

    id: str = Field(primary_key=True, description="群聊ID")
    name: str = Field(..., description="群聊名称")
    game_type: str = Field(default="lucky8", description="游戏类型：lucky8/liuhecai")
    owner_id: Optional[str] = Field(None, description="所属分销商ID")
    auto_draw: bool = Field(default=True, description="是否自动开奖")
    bet_lock_time: int = Field(default=60, description="封盘时间（秒）")
    member_count: int = Field(default=0, description="成员数量")
    total_bets: int = Field(default=0, description="总投注次数")
    total_volume: Decimal = Field(default=Decimal("0.00"), description="总投注额", max_digits=15, decimal_places=2)
    status: str = Field(default="active", description="状态：active/inactive")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
