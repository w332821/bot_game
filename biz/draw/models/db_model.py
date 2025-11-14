"""
Draw数据库表模型
对应 Node.js 中的 drawHistory数组
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON


class DrawTable(SQLModel, table=True):
    """开奖数据库表"""
    __tablename__ = "draws"

    id: int = Field(default=None, primary_key=True, description="自增ID")
    issue: str = Field(..., description="期号", index=True, unique=True)
    game_type: str = Field(default="lucky8", description="游戏类型：lucky8/liuhecai", index=True)
    draw_time: datetime = Field(..., description="开奖时间", index=True)
    numbers: list = Field(default=[], sa_column=Column(JSON), description="开奖号码数组")
    draw_code: Optional[str] = Field(None, description="开奖号码串（逗号分隔）")
    result_summary: Optional[dict] = Field(default=None, sa_column=Column(JSON), description="开奖结果汇总")
    source: str = Field(default="auto", description="来源：auto/manual/api")
    created_at: datetime = Field(default_factory=datetime.now)
    image_path: Optional[str] = Field(None, description="开奖图片路径")
