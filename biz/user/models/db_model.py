"""
User数据库表模型
对应 Node.js 中的 users Map
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON


class UserTable(SQLModel, table=True):
    """用户数据库表"""
    __tablename__ = "users"

    id: str = Field(primary_key=True, description="用户ID（悦聊平台ID）")
    username: str = Field(..., description="用户名")
    chat_id: str = Field(..., description="群聊ID", index=True)
    balance: Decimal = Field(default=Decimal("0.00"), description="余额", max_digits=15, decimal_places=2)
    score: int = Field(default=0, description="积分")
    rebate_ratio: Decimal = Field(default=Decimal("0.02"), description="回水比例", max_digits=5, decimal_places=4)
    join_date: datetime = Field(default_factory=datetime.now, description="加入日期")
    status: str = Field(default="活跃", description="状态：活跃/禁用")
    role: str = Field(default="normal", description="角色：normal/admin")
    created_by: str = Field(default="admin", description="创建者")
    is_bot: bool = Field(default=False, description="是否为机器人")
    bot_config: Optional[dict] = Field(default=None, sa_column=Column(JSON), description="机器人配置")
    is_new: bool = Field(default=True, description="是否为新用户")
    marked_read_at: Optional[datetime] = Field(default=None, description="标记已读时间")
    red_packet_settings: Optional[dict] = Field(default=None, sa_column=Column(JSON), description="红包设置")
    report_details: Optional[dict] = Field(default=None, sa_column=Column(JSON), description="报表详情")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
