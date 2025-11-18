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


# 7. online_status 表
class OnlineStatusTable(SQLModel, table=True):
    """在线状态表：记录用户最近心跳时间"""
    __tablename__ = "online_status"

    id: int = Field(default=None, primary_key=True, description="自增ID")
    user_id: str = Field(..., description="用户ID", index=True)
    platform: str = Field(..., description="平台：web/app", index=True)
    last_seen: datetime = Field(default_factory=datetime.now, description="最近心跳时间", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 8. online_metrics 表
class OnlineMetricsTable(SQLModel, table=True):
    """在线趋势快照：每30分钟汇总一次"""
    __tablename__ = "online_metrics"

    id: int = Field(default=None, primary_key=True, description="自增ID")
    metric_date: date = Field(..., description="日期", index=True)
    time_slot: str = Field(..., description="时间段：HH:MM", index=True)
    web_count: int = Field(default=0, description="Web在线人数")
    app_count: int = Field(default=0, description="App在线人数")
    total_count: int = Field(default=0, description="总在线人数")
    created_at: datetime = Field(default_factory=datetime.now)


# 9. member_profiles 表
class MemberProfileTable(SQLModel, table=True):
    __tablename__ = "member_profiles"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(..., description="用户ID", index=True)
    account: str = Field(..., description="账号", index=True)
    name: Optional[str] = Field(None, description="会员姓名")
    level: int = Field(default=1, description="会员级别", index=True)
    plate: str = Field(default="B", description="盘口 A/B/C/D", index=True)
    superior_account: str | None = Field(default=None, description="上级账号", index=True)
    open_time: datetime = Field(default_factory=datetime.now, description="开户时间", index=True)
    company_remarks: str | None = Field(default=None, sa_column=Column(TEXT))
    created_at: datetime = Field(default_factory=datetime.now)


# 10. login_logs 表
class LoginLogTable(SQLModel, table=True):
    __tablename__ = "login_logs"

    id: int = Field(default=None, primary_key=True)
    account: str = Field(..., description="账号", index=True)
    login_time: datetime = Field(default_factory=datetime.now, description="登录时间", index=True)
    ip_address: str | None = Field(default=None, description="IP地址")
    ip_location: str | None = Field(default=None, description="IP归属地")
    operator: str | None = Field(default=None, description="运营商")
    created_at: datetime = Field(default_factory=datetime.now)


# 11. bet_orders 表（管理后台注单）
class BetOrderTable(SQLModel, table=True):
    """注单表（管理后台）"""
    __tablename__ = "bet_orders"

    id: int = Field(default=None, primary_key=True)
    order_no: str = Field(..., description="注单号", unique=True, index=True)
    user_id: str = Field(..., description="用户ID", index=True)
    bet_time: datetime = Field(default_factory=datetime.now, description="投注时间", index=True)
    settle_time: Optional[datetime] = Field(None, description="结算时间")
    bet_type: str = Field(..., description="彩种，必须是 '新奥六合彩' 或 '168澳洲幸运8'", index=True)
    bet_content: str = Field(..., sa_column=Column(TEXT), description="投注内容")
    bet_amount: Decimal = Field(..., description="投注金额", max_digits=15, decimal_places=2)
    valid_amount: Decimal = Field(default=Decimal("0.00"), description="有效金额", max_digits=15, decimal_places=2)
    rebate: Decimal = Field(default=Decimal("0.00"), description="退水", max_digits=15, decimal_places=2)
    bet_result: Decimal = Field(default=Decimal("0.00"), description="输赢结果（负数为输）", max_digits=15, decimal_places=2)
    status: str = Field(default="unsettled", description="状态: settled/unsettled/cancelled")
    gameplay: Optional[str] = Field(None, description="玩法名称")
    ip_address: Optional[str] = Field(None, description="投注IP")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 12. transactions 表（交易记录）
class TransactionTable(SQLModel, table=True):
    """交易记录表"""
    __tablename__ = "transactions"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(..., description="用户ID", index=True)
    transaction_time: datetime = Field(default_factory=datetime.now, description="交易时间", index=True)
    transaction_type: str = Field(..., description="交易类型: deposit/withdrawal/transfer/recharge/deduction", index=True)
    amount: Decimal = Field(..., description="金额", max_digits=15, decimal_places=2)
    fee: Decimal = Field(default=Decimal("0.00"), description="手续费", max_digits=15, decimal_places=2)
    transaction_info: Optional[str] = Field(None, description="交易信息")
    status: str = Field(default="processing", description="状态: success/failed/processing/cancelled", index=True)
    processor: Optional[str] = Field(None, description="处理人")
    review_comments: Optional[str] = Field(None, sa_column=Column(TEXT), description="审核备注")
    created_at: datetime = Field(default_factory=datetime.now)


# 13. account_changes 表（账变记录）
class AccountChangeTable(SQLModel, table=True):
    """账变记录表"""
    __tablename__ = "account_changes"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(..., description="用户ID", index=True)
    change_time: datetime = Field(default_factory=datetime.now, description="变动时间", index=True)
    change_type: str = Field(..., description="变动类型: deposit/withdrawal/transfer/recharge/deduction/bet/win/rebate", index=True)
    balance_before: Decimal = Field(..., description="变动前余额", max_digits=15, decimal_places=2)
    change_value: Decimal = Field(..., description="变动金额（正数为增加，负数为减少）", max_digits=15, decimal_places=2)
    balance_after: Decimal = Field(..., description="变动后余额", max_digits=15, decimal_places=2)
    operator: Optional[str] = Field(None, description="操作人")
    created_at: datetime = Field(default_factory=datetime.now)


# 14. rebate_settings 表（退水配置）
class RebateSettingTable(SQLModel, table=True):
    """退水配置表"""
    __tablename__ = "rebate_settings"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(..., description="用户ID", unique=True, index=True)
    independent_rebate: bool = Field(default=False, description="是否独立退水")
    earn_rebate: Decimal = Field(default=Decimal("0.000"), description="赚取退水百分比", max_digits=5, decimal_places=3)
    game_settings: Optional[str] = Field(None, sa_column=Column(TEXT), description="游戏退水设置（JSON）")
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)


# 15. roles 表（角色）
class RoleTable(SQLModel, table=True):
    """角色表"""
    __tablename__ = "roles"

    id: int = Field(default=None, primary_key=True)
    role_name: str = Field(..., description="角色名称", unique=True)
    role_code: str = Field(..., description="角色编码", unique=True)
    remarks: Optional[str] = Field(None, sa_column=Column(TEXT), description="备注")
    status: str = Field(default="启用", description="状态: 启用/禁用")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 16. role_permissions 表（角色权限）
class RolePermissionTable(SQLModel, table=True):
    """角色权限表"""
    __tablename__ = "role_permissions"

    id: int = Field(default=None, primary_key=True)
    role_id: int = Field(..., description="角色ID", index=True)
    permission_code: str = Field(..., description="权限编码，如 personal-basic-1")
    created_at: datetime = Field(default_factory=datetime.now)


# 17. sub_accounts 表（子账号）
class SubAccountTable(SQLModel, table=True):
    """子账号表"""
    __tablename__ = "sub_accounts"

    id: int = Field(default=None, primary_key=True)
    parent_user_id: str = Field(..., description="主账号ID", index=True)
    account: str = Field(..., description="子账号", unique=True)
    password: str = Field(..., description="登录密码（加密）")
    payment_password: Optional[str] = Field(None, description="支付密码（加密）")
    account_name: str = Field(..., description="账户名称")
    role_id: int = Field(..., description="角色ID")
    status: str = Field(default="启用", description="状态: 启用/禁用")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 18. lottery_rebate_config 表（彩票退水配置）
class LotteryRebateConfigTable(SQLModel, table=True):
    """彩票退水配置表"""
    __tablename__ = "lottery_rebate_config"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(..., description="用户ID", unique=True, index=True)
    config_data: str = Field(..., sa_column=Column(TEXT), description="退水配置JSON数据")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 19. agent_profiles 表（代理专属信息）
class AgentProfileTable(SQLModel, table=True):
    """代理配置表"""
    __tablename__ = "agent_profiles"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(..., description="用户ID（关联users表）", unique=True, index=True)
    account: str = Field(..., description="代理账号", unique=True, index=True)
    name: Optional[str] = Field(None, description="代理姓名")
    level: int = Field(default=1, description="代理级别", index=True)
    plate: str = Field(default="B", description="主盘口 A/B/C", index=True)
    open_plate: str = Field(default='["A","B","C"]', sa_column=Column(TEXT), description="开放盘口JSON数组，如 [\"A\",\"B\"]")
    earn_rebate: str = Field(default="partial", description="赚取退水: full/partial/none")
    subordinate_transfer: str = Field(default="enable", description="下级转账: enable/disable")
    default_rebate_plate: str = Field(default="A", description="新会员默认退水盘口: A/B/C/D")
    invite_code: str = Field(..., description="邀请码（8位唯一）", unique=True, index=True)
    promotion_domains: str = Field(default='[]', sa_column=Column(TEXT), description="推广域名JSON数组")
    superior_account: Optional[str] = Field(None, description="上级账号", index=True)
    company_remarks: Optional[str] = Field(None, sa_column=Column(TEXT), description="公司备注")
    open_time: datetime = Field(default_factory=datetime.now, description="开户时间", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 20. agent_settlement_config 表（代理结算配置）
class AgentSettlementConfigTable(SQLModel, table=True):
    """代理结算配置表"""
    __tablename__ = "agent_settlement_config"

    id: int = Field(default=None, primary_key=True)
    agent_user_id: str = Field(..., description="代理用户ID", unique=True, index=True)
    share_percentage: Decimal = Field(
        default=Decimal("0.00"),
        description="占成比例 0-100",
        max_digits=5,
        decimal_places=2
    )
    earn_rebate_mode: str = Field(
        default="none",
        description="赚水模式: full(全额)/partial(部分)/none(不赚)"
    )
    can_collect_downline: bool = Field(
        default=True,
        description="是否可以收取下线盈利"
    )
    settlement_cycle: str = Field(
        default="daily",
        description="结算周期: daily/weekly/monthly"
    )
    remarks: Optional[str] = Field(
        None,
        sa_column=Column(TEXT),
        description="备注"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
