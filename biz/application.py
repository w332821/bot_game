import logging
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from biz.containers import Container
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from base.middleware import (
    LoggingMiddleware,
    RequestIDMiddleware,
    exception_handler,
)
from base.exception import UnifyException
from biz.game.scheduler import init_scheduler, shutdown_scheduler

# 加载环境变量（必须在其他模块导入前执行）
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 初始化依赖注入容器（需要在应用创建前初始化）
container = Container()

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger = logging.getLogger(__name__)
    logger.info("🚀 应用启动中...")

    # 1. 自动初始化数据库表
    logger.info("📊 检查数据库表...")
    try:
        from base.init_db import init_database
        init_database()
        logger.info("✅ 数据库表检查完成")
    except Exception as e:
        logger.error(f"❌ 数据库表初始化失败: {str(e)}")
        logger.warning("⚠️ 请手动运行: python -m base.init_db")

    # 2. 初始化开奖API数据（与Node.js版本相同）
    from external import get_draw_api_client
    draw_client = get_draw_api_client()

    try:
        logger.info("📡 初始化开奖API数据...")
        result = await draw_client.initialize_draw_data()

        if result['lucky8_success']:
            logger.info("✅ 澳门快乐十分开奖数据已加载")
        else:
            logger.warning("⚠️ 澳门快乐十分开奖数据加载失败，将使用随机数兜底")

        if result['draw_success']:
            logger.info("✅ 澳门六合彩开奖数据已加载")
        else:
            logger.warning("⚠️ 澳门六合彩开奖数据加载失败")

        # 启动自动刷新（每5分钟）
        await draw_client.start_auto_refresh(interval_minutes=5)
        logger.info("✅ 开奖数据自动刷新已启动（间隔5分钟）")

    except Exception as e:
        logger.error(f"❌ 开奖API初始化失败: {str(e)}")
        logger.warning("⚠️ 将使用随机数据作为兜底方案")

    # 初始化开奖调度器
    game_service = container.game_service()
    scheduler = init_scheduler(game_service)
    logger.info("✅ 开奖调度器已初始化")

    yield

    # 关闭时
    logger.info("🔴 应用关闭中...")

    # 停止自动刷新
    draw_client.stop_auto_refresh()

    # 关闭调度器
    await shutdown_scheduler()

    logger.info("✅ 应用已关闭")

# API 路由前缀
api_prefix = "/api"

# 创建 FastAPI 应用（使用lifespan管理生命周期）
app = FastAPI(
    title="Game Bot API",
    description="澳洲幸运8/六合彩游戏机器人后端API",
    version="2.0.0",
    lifespan=lifespan
)

# 注册全局异常处理器
app.add_exception_handler(UnifyException, exception_handler)
app.add_exception_handler(Exception, exception_handler)

# 添加中间件（注意顺序：先添加的后执行）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# 初始化依赖注入容器
container = Container()

# 导入Webhook路由
from biz.game.webhook import webhook_api

# 使用FastAPI依赖覆盖机制
app.dependency_overrides[webhook_api.get_game_service] = lambda: container.game_service()
app.dependency_overrides[webhook_api.get_user_service] = lambda: container.user_service()
app.dependency_overrides[webhook_api.get_chat_repo] = lambda: container.chat_repo()
app.dependency_overrides[webhook_api.get_bot_client] = lambda: container.bot_api_client()

# 注册Webhook路由（不使用前缀，因为webhook路径是固定的）
app.include_router(webhook_api.router)

# Wire依赖注入
container.wire(modules=[
    "biz.game.webhook.webhook_api",
])

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "game-bot"}


# 测试端点
@app.get("/")
async def root():
    return {
        "message": "Game Bot API",
        "version": "2.0.0",
        "docs": "/docs"
    }


if __name__ == '__main__':
    # 开发环境使用 reload，生产环境使用 workers
    uvicorn.run(
        'biz.application:app',
        host='0.0.0.0',
        port=3003,  # 使用3003端口，与Node.js版本保持一致
        reload=True  # 生产环境改为 False，并设置 workers=2
    )
