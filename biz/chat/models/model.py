"""
Chat模型定义
对应数据库表：chats
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class Chat(BaseModel):
    """群聊模型（数据库表对应）"""
    id: str = Field(..., description="群聊ID")
    name: str = Field(..., description="群聊名称")
    game_type: str = Field(default="lucky8", description="游戏类型：lucky8/liuhecai")
    owner_id: Optional[str] = Field(None, description="所属分销商ID")
    auto_draw: bool = Field(default=True, description="是否自动开奖")
    bet_lock_time: int = Field(default=60, description="封盘时间（秒）")
    member_count: int = Field(default=0, description="成员数量")
    total_bets: int = Field(default=0, description="总投注次数")
    total_volume: Decimal = Field(default=Decimal("0.00"), description="总投注额")
    status: str = Field(default="active", description="状态：active/inactive")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class ChatCreate(BaseModel):
    """创建群聊请求模型"""
    id: str = Field(..., description="群聊ID")
    name: str = Field(..., description="群聊名称")
    game_type: str = Field(default="lucky8", description="游戏类型")
    owner_id: Optional[str] = None
    auto_draw: bool = Field(default=True)
    bet_lock_time: int = Field(default=60)


class ChatUpdate(BaseModel):
    """更新群聊请求模型"""
    name: Optional[str] = None
    game_type: Optional[str] = None
    owner_id: Optional[str] = None
    auto_draw: Optional[bool] = None
    bet_lock_time: Optional[int] = None
    status: Optional[str] = None


class ChatStats(BaseModel):
    """群聊统计信息"""
    chat_id: str
    name: str
    member_count: int
    total_bets: int
    total_volume: Decimal
    active_users: int
    game_type: str

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
