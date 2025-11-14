"""
Admin模型定义
对应数据库表：admin_accounts
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class AdminAccount(BaseModel):
    """管理员账户模型（数据库表对应）"""
    id: str = Field(..., description="管理员ID")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码哈希")
    role: str = Field(default="distributor", description="角色：superadmin/distributor")
    managed_chat_id: Optional[str] = Field(None, description="管理的群聊ID（分销商专用）")
    balance: Decimal = Field(default=Decimal("0.00"), description="余额（回水账户）")
    total_rebate_collected: Decimal = Field(default=Decimal("0.00"), description="累计回水收入")
    status: str = Field(default="active", description="状态：active/inactive")
    description: Optional[str] = Field(None, description="描述")
    created_date: date = Field(default_factory=date.today, description="创建日期")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class AdminCreate(BaseModel):
    """创建管理员请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    role: str = Field(default="distributor", description="角色")
    managed_chat_id: Optional[str] = None
    description: Optional[str] = None


class AdminLogin(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class AdminUpdate(BaseModel):
    """更新管理员请求模型"""
    password: Optional[str] = None
    role: Optional[str] = None
    managed_chat_id: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None


class AdminInfo(BaseModel):
    """管理员信息（不含密码）"""
    id: str
    username: str
    role: str
    managed_chat_id: Optional[str]
    balance: Decimal
    total_rebate_collected: Decimal
    status: str
    description: Optional[str]
    created_date: date
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
