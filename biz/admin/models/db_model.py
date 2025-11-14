"""
Admin数据库表模型
对应 Node.js 中的 adminAccounts Map 和 adminBalances Map
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class AdminTable(SQLModel, table=True):
    """管理员数据库表"""
    __tablename__ = "admins"

    id: str = Field(primary_key=True, description="管理员ID")
    username: str = Field(..., description="管理员用户名", unique=True)
    password_hash: str = Field(..., description="密码哈希")
    role: str = Field(default="admin", description="角色：admin/super_admin")
    balance: Decimal = Field(default=Decimal("0.00"), description="余额（回水抽成）", max_digits=15, decimal_places=2)
    permissions: Optional[str] = Field(None, description="权限列表（逗号分隔）")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
