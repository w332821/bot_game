"""
所有数据库表的定义
根据实际Repository中的SQL语句整理
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON, TEXT


# 1. users表
class UserTable(SQLModel, table=True):
    """用户表"""
    __tablename__ = "users"

    id: str = Field(primary_key=True, description="用户ID（悦聊平台ID）")
    chat_id: str = Field(primary_key=True, description="群聊ID", index=True)
    username: str = Field(..., description="用户名")
    balance: Decimal = Field(default=Decimal("0.00"), description="余额", max_digits=15, decimal_places=2)
    score: int = Field(default=0, description="积分")
    rebate_ratio: Decimal = Field(default=Decimal("0.02"), description="回水比例", max_digits=5, decimal_places=4)
    join_date: date = Field(default_factory=date.today, description="加入日期")
    status: str = Field(default="活跃", description="状态：活跃/禁用")
    role: str = Field(default="normal", description="角色：normal/admin")
    created_by: str = Field(default="admin", description="创建者")
    is_bot: bool = Field(default=False, description="是否为机器人")
    bot_config: Optional[str] = Field(default=None, sa_column=Column(TEXT), description="机器人配置JSON")
    is_new: bool = Field(default=True, description="是否为新用户")
    marked_read_at: Optional[datetime] = Field(default=None, description="标记已读时间")
    red_packet_settings: Optional[str] = Field(default=None, sa_column=Column(TEXT), description="红包设置JSON")
    report_details: Optional[str] = Field(default=None, sa_column=Column(TEXT), description="报表详情JSON")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 2. bets表
class BetTable(SQLModel, table=True):
    """投注表"""
    __tablename__ = "bets"

    id: str = Field(primary_key=True, description="投注ID")
    user_id: str = Field(..., description="用户ID", index=True)
    username: str = Field(..., description="用户名")
    chat_id: str = Field(..., description="群聊ID", index=True)
    game_type: str = Field(default="lucky8", description="游戏类型：lucky8/liuhecai")
    lottery_type: str = Field(..., description="投注类型：fan/zheng/nian/jiao/tong/tema等")
    bet_number: Optional[int] = Field(None, description="投注号码")
    bet_amount: Decimal = Field(..., description="投注金额", max_digits=15, decimal_places=2)
    odds: Decimal = Field(..., description="赔率", max_digits=10, decimal_places=2)
    status: str = Field(default="active", description="状态：active/cancelled")
    result: str = Field(default="pending", description="结果：pending/win/lose/tie")
    pnl: Decimal = Field(default=Decimal("0.00"), description="盈亏金额", max_digits=15, decimal_places=2)
    issue: Optional[str] = Field(None, description="期号", index=True)
    draw_number: Optional[int] = Field(None, description="开奖号码")
    draw_code: Optional[str] = Field(None, description="开奖号码串")
    bet_details: Optional[str] = Field(None, sa_column=Column(TEXT), description="投注详情JSON")
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    settled_at: Optional[datetime] = Field(None, description="结算时间")


# 3. chats表
class ChatTable(SQLModel, table=True):
    """群聊表"""
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


# 4. draw_history表
class DrawHistoryTable(SQLModel, table=True):
    """开奖历史表"""
    __tablename__ = "draw_history"

    id: int = Field(default=None, primary_key=True, description="自增ID")
    draw_number: int = Field(..., description="开奖号码（主号码）")
    issue: str = Field(..., description="期号", index=True)
    draw_code: str = Field(..., description="开奖号码串（完整）")
    game_type: str = Field(default="lucky8", description="游戏类型：lucky8/liuhecai", index=True)
    is_random: bool = Field(default=False, description="是否随机开奖")
    chat_id: str = Field(default="system", description="群聊ID")
    bet_count: int = Field(default=0, description="投注数量")
    timestamp: datetime = Field(default_factory=datetime.now, description="开奖时间", index=True)
    special_number: Optional[int] = Field(None, description="特殊号码（六合彩特码）")
    created_at: datetime = Field(default_factory=datetime.now)


# 5. odds_config表
class OddsConfigTable(SQLModel, table=True):
    """赔率配置表"""
    __tablename__ = "odds_config"

    id: int = Field(default=None, primary_key=True, description="自增ID")
    bet_type: str = Field(..., description="投注类型", index=True)
    odds: Decimal = Field(..., description="赔率", max_digits=10, decimal_places=2)
    min_bet: Decimal = Field(default=Decimal("10.00"), description="最小投注额", max_digits=15, decimal_places=2)
    max_bet: Decimal = Field(default=Decimal("10000.00"), description="最大投注额", max_digits=15, decimal_places=2)
    period_max: Decimal = Field(default=Decimal("50000.00"), description="单期最大投注额", max_digits=15, decimal_places=2)
    game_type: str = Field(default="lucky8", description="游戏类型", index=True)
    description: Optional[str] = Field(None, description="描述")
    tema_odds: Optional[str] = Field(None, sa_column=Column(TEXT), description="特码赔率JSON")
    status: str = Field(default="active", description="状态：active/inactive")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 6. admin_accounts表
class AdminAccountTable(SQLModel, table=True):
    """管理员账户表"""
    __tablename__ = "admin_accounts"

    id: str = Field(primary_key=True, description="管理员ID")
    username: str = Field(..., description="用户名", unique=True)
    password: str = Field(..., description="密码（加密）")
    role: str = Field(default="distributor", description="角色：admin/distributor")
    managed_chat_id: Optional[str] = Field(None, description="管理的群聊ID")
    balance: Decimal = Field(default=Decimal("0.00"), description="余额", max_digits=15, decimal_places=2)
    total_rebate_collected: Decimal = Field(default=Decimal("0.00"), description="累计回水", max_digits=15, decimal_places=2)
    status: str = Field(default="active", description="状态：active/inactive")
    description: Optional[str] = Field(None, description="描述")
    created_date: date = Field(default_factory=date.today, description="创建日期")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
