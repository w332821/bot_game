"""
Odds模型定义
对应数据库表：odds_config
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class OddsConfig(BaseModel):
    """赔率配置模型（数据库表对应）"""
    bet_type: str = Field(..., description="投注类型：fan/zheng/nian/jiao/tong/tema等")
    odds: Decimal = Field(..., description="赔率")
    min_bet: Decimal = Field(default=Decimal("10.00"), description="最小投注金额")
    max_bet: Decimal = Field(default=Decimal("10000.00"), description="最大投注金额")
    period_max: Decimal = Field(default=Decimal("50000.00"), description="单期最大投注额")
    game_type: str = Field(default="lucky8", description="游戏类型：lucky8/liuhecai")
    description: Optional[str] = Field(None, description="描述")
    tema_odds: Optional[Dict[str, Any]] = Field(None, description="特码赔率配置（JSON）")
    status: str = Field(default="active", description="状态：active/inactive")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class OddsCreate(BaseModel):
    """创建赔率配置请求模型"""
    bet_type: str = Field(..., description="投注类型")
    odds: Decimal = Field(..., description="赔率")
    min_bet: Decimal = Field(default=Decimal("10.00"))
    max_bet: Decimal = Field(default=Decimal("10000.00"))
    period_max: Decimal = Field(default=Decimal("50000.00"))
    game_type: str = Field(default="lucky8")
    description: Optional[str] = None
    tema_odds: Optional[Dict[str, Any]] = None


class OddsUpdate(BaseModel):
    """更新赔率配置请求模型"""
    odds: Optional[Decimal] = None
    min_bet: Optional[Decimal] = None
    max_bet: Optional[Decimal] = None
    period_max: Optional[Decimal] = None
    description: Optional[str] = None
    tema_odds: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class OddsInfo(BaseModel):
    """赔率信息（简化版）"""
    bet_type: str
    odds: Decimal
    min_bet: Decimal
    max_bet: Decimal
    game_type: str

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
