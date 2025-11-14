"""
Draw模型定义
对应数据库表：draw_history
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DrawHistory(BaseModel):
    """开奖历史模型（数据库表对应）"""
    id: int = Field(..., description="主键ID")
    draw_number: int = Field(..., description="开奖号码")
    issue: str = Field(..., description="期号")
    draw_code: str = Field(..., description="开奖号码串")
    game_type: str = Field(default="lucky8", description="游戏类型：lucky8/liuhecai")
    is_random: bool = Field(default=False, description="是否为随机开奖")
    chat_id: str = Field(default="system", description="群聊ID（system为官方开奖）")
    bet_count: int = Field(default=0, description="投注数量")
    timestamp: datetime = Field(..., description="开奖时间")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DrawCreate(BaseModel):
    """创建开奖记录请求模型"""
    draw_number: int = Field(..., description="开奖号码")
    issue: str = Field(..., description="期号")
    draw_code: str = Field(..., description="开奖号码串")
    game_type: str = Field(default="lucky8", description="游戏类型")
    is_random: bool = Field(default=False, description="是否为随机开奖")
    chat_id: str = Field(default="system", description="群聊ID")
    bet_count: int = Field(default=0, description="投注数量")
    timestamp: datetime = Field(default_factory=datetime.now, description="开奖时间")


class DrawInfo(BaseModel):
    """开奖信息（简化版）"""
    issue: str
    draw_number: int
    draw_code: str
    game_type: str
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
