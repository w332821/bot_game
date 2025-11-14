import yaml
import logging
from sqlalchemy import create_engine, Engine
from sqlmodel import SQLModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

"""
建表
需要在工程根目录下通过 python -m base.init_db 执行
"""

def get_database_uri_from_config() -> str:
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        db_uri = config.get("db", {}).get("sync_database_uri")
        if not db_uri:
            raise ValueError("Database URI ('db.database_uri') not found in config.yaml")
        log.info("Database URI loaded from config.")
        return db_uri

    except (FileNotFoundError, ValueError, yaml.YAMLError) as e:
        log.error(f"Error loading database configuration: {e}")
        raise


def get_mysql_sync_engine(db_uri: str, echo: bool = False) -> Engine:
    """创建MySQL同步引擎

    Args:
        db_uri: 数据库连接URI
        echo: 是否打印SQL语句（默认False，减少启动日志）
    """
    engine = create_engine(db_uri, echo=echo)
    return engine


def init_database(verbose: bool = False):
    """初始化数据库，创建所有定义的 SQLModel 表

    Args:
        verbose: 是否打印详细日志（包括SQL语句）
    """
    log.info("Starting database initialization...")
    try:
        # IMPORTANT: Import all table models first to register them with SQLModel.metadata
        if verbose:
            log.info("Importing database table models...")

        from biz.all_tables import (
            UserTable,
            BetTable,
            ChatTable,
            DrawHistoryTable,
            OddsConfigTable,
            AdminAccountTable
        )

        if verbose:
            log.info(f"All table models imported successfully:")
            log.info(f"  - {UserTable.__tablename__}")
            log.info(f"  - {BetTable.__tablename__}")
            log.info(f"  - {ChatTable.__tablename__}")
            log.info(f"  - {DrawHistoryTable.__tablename__}")
            log.info(f"  - {OddsConfigTable.__tablename__}")
            log.info(f"  - {AdminAccountTable.__tablename__}")

        db_uri = get_database_uri_from_config()
        engine = get_mysql_sync_engine(db_uri, echo=verbose)

        if verbose:
            log.info("Creating tables...")

        # create_all 会自动检查表是否存在，只创建不存在的表
        SQLModel.metadata.create_all(engine)

        log.info("Database tables initialized successfully")

        engine.dispose()

    except Exception as e:
        log.error(f"Database initialization failed: {e}", exc_info=True)
        raise  # 重新抛出异常，让调用方知道失败了


if __name__ == "__main__":
    # 命令行运行时打印详细日志
    init_database(verbose=True)
