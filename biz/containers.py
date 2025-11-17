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
        scheduler=providers.Callable(lambda: getattr(container, 'scheduler_instance', None))
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
