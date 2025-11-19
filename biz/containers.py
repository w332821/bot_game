from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
import yaml

# Import repositories
from biz.user.repo.user_repo import UserRepository
from biz.bet.repo.bet_repo import BetRepository
from biz.chat.repo.chat_repo import ChatRepository
from biz.draw.repo.draw_repo import DrawRepository
from biz.odds.repo.odds_repo import OddsRepository
from biz.admin.repo.admin_repo import AdminRepository

# Import services
from biz.user.service.user_service import UserService
from biz.odds.service.odds_service import OddsService
from biz.game.service.game_service import GameService
from biz.chat.service.chat_service import ChatService
from biz.admin.service.admin_service import AdminService
from biz.draw.service.draw_service import DrawService
from biz.home.repo.home_repo import HomeRepository
from biz.home.service.home_service import HomeService
from biz.users.repo.member_repo import MemberRepository
from biz.users.service.member_service import MemberService
from biz.users.repo.agent_repo import AgentRepository
from biz.users.service.agent_service import AgentService
from biz.users.repo.rebate_repo import RebateRepository
from biz.users.service.rebate_service import RebateService
from biz.users.repo.personal_repo import PersonalRepository
from biz.users.service.personal_service import PersonalService
from biz.roles.repo.role_repo import RoleRepository
from biz.roles.service.role_service import RoleService
from biz.roles.repo.subaccount_repo import SubAccountRepository
from biz.roles.service.subaccount_service import SubAccountService
from biz.reports.repo.report_repo import ReportRepository
from biz.reports.service.report_service import ReportService
from biz.users.service.bot_user_service import BotUserService

# Import external clients
from external.bot_api_client import BotApiClient


class Container(containers.DeclarativeContainer):
    """
    依赖注入容器
    """

    config = providers.Configuration()
    with open("config.yaml", "r") as f:
        config.from_dict(yaml.safe_load(f))

    # 数据库引擎和会话工厂（单例）
    db_engine = providers.Singleton(
        create_async_engine,
        url=config.db.database_uri,
        echo=config.db.echo
    )

    db_session_factory = providers.Singleton(
        sessionmaker,
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    # ===== Repository 层 =====

    user_repo = providers.Factory(
        UserRepository,
        session_factory=db_session_factory
    )

    bet_repo = providers.Factory(
        BetRepository,
        session_factory=db_session_factory
    )

    chat_repo = providers.Factory(
        ChatRepository,
        session_factory=db_session_factory
    )

    draw_repo = providers.Factory(
        DrawRepository,
        session_factory=db_session_factory
    )

    odds_repo = providers.Factory(
        OddsRepository,
        session_factory=db_session_factory
    )

    admin_repo = providers.Factory(
        AdminRepository,
        session_factory=db_session_factory
    )

    # ===== Service 层 =====

    user_service = providers.Factory(
        UserService,
        user_repo=user_repo
    )

    odds_service = providers.Factory(
        OddsService,
        odds_repo=odds_repo
    )

    chat_service = providers.Factory(
        ChatService,
        chat_repo=chat_repo,
        scheduler=None
    )

    # 管理员服务
    admin_service = providers.Factory(
        AdminService,
        admin_repo=admin_repo
    )

    draw_service = providers.Factory(
        DrawService,
        draw_repo=draw_repo
    )

    home_repo = providers.Factory(
        HomeRepository,
        session_factory=db_session_factory
    )

    home_service = providers.Factory(
        HomeService,
        home_repo=home_repo
    )

    member_repo = providers.Factory(
        MemberRepository,
        session_factory=db_session_factory
    )

    member_service = providers.Factory(
        MemberService,
        member_repo=member_repo
    )

    agent_repo = providers.Factory(
        AgentRepository,
        session_factory=db_session_factory
    )

    agent_service = providers.Factory(
        AgentService,
        agent_repo=agent_repo
    )

    rebate_repo = providers.Factory(
        RebateRepository,
        session_factory=db_session_factory
    )

    rebate_service = providers.Factory(
        RebateService,
        rebate_repo=rebate_repo
    )

    personal_repo = providers.Factory(
        PersonalRepository,
        session_factory=db_session_factory
    )

    personal_service = providers.Factory(
        PersonalService,
        personal_repo=personal_repo
    )

    role_repo = providers.Factory(
        RoleRepository,
        session_factory=db_session_factory
    )

    role_service = providers.Factory(
        RoleService,
        role_repo=role_repo
    )

    subaccount_repo = providers.Factory(
        SubAccountRepository,
        session_factory=db_session_factory
    )

    subaccount_service = providers.Factory(
        SubAccountService,
        subaccount_repo=subaccount_repo
    )

    report_repo = providers.Factory(
        ReportRepository,
        session_factory=db_session_factory
    )

    report_service = providers.Factory(
        ReportService,
        report_repo=report_repo
    )

    bot_user_service = providers.Factory(
        BotUserService,
        user_repo=user_repo,
        session_factory=db_session_factory
    )

    # ===== External Clients =====

    bot_api_client = providers.Singleton(
        BotApiClient
    )

    # ===== Game Service =====

    game_service = providers.Factory(
        GameService,
        user_service=user_service,
        user_repo=user_repo,
        bet_repo=bet_repo,
        chat_repo=chat_repo,
        draw_repo=draw_repo,
        odds_service=odds_service,
        bot_api_client=bot_api_client
    )
