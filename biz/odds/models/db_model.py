"""
Odds数据库表模型
对应 Node.js 中的 odds Map
"""
from datetime import datetime
from decimal import Decimal
from sqlmodel import Field, SQLModel


class OddsTable(SQLModel, table=True):
    """赔率数据库表"""
    __tablename__ = "odds"

    id: int = Field(default=None, primary_key=True, description="自增ID")
    game_type: str = Field(..., description="游戏类型：lucky8/liuhecai", index=True)
    lottery_type: str = Field(..., description="投注类型", index=True)
    odds_value: Decimal = Field(..., description="赔率值", max_digits=10, decimal_places=2)
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
