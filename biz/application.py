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

    is_testing = os.getenv("PYTEST_CURRENT_TEST") is not None

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

        if not is_testing:
            await draw_client.start_auto_refresh(interval_minutes=5)
            logger.info("✅ 开奖数据自动刷新已启动（间隔5分钟）")

    except Exception as e:
        logger.error(f"❌ 开奖API初始化失败: {str(e)}")
        logger.warning("⚠️ 将使用随机数据作为兜底方案")

    # 初始化开奖调度器
    game_service = container.game_service()
    bot_client = container.bot_api_client()
    scheduler = None
    if not is_testing:
        scheduler = init_scheduler(game_service, bot_client)
        logger.info("✅ 开奖调度器已初始化")

    # 将scheduler保存到container中,供其他服务使用
    container.scheduler_instance = scheduler

    # 自动注册所有已存在的活跃群聊到调度器
    if not is_testing:
        try:
            from biz.chat.repo.chat_repo import ChatRepository
            chat_repo = container.chat_repo()

            active_chats = await chat_repo.get_all_chats(limit=1000, status='active')
            logger.info(f"📊 发现 {len(active_chats)} 个活跃群聊")

            lucky8_count = 0
            liuhecai_count = 0

            for chat in active_chats:
                chat_id = chat['id']
                game_type = chat.get('game_type', 'lucky8')
                scheduler.register_chat_to_global_timer(chat_id, game_type)
                if game_type == 'lucky8':
                    lucky8_count += 1
                elif game_type == 'liuhecai':
                    liuhecai_count += 1

            logger.info(f"✅ 已注册群聊到调度器:")
            logger.info(f"   - 澳洲幸运8: {lucky8_count} 个群聊")
            logger.info(f"   - 六合彩: {liuhecai_count} 个群聊")

        except Exception as e:
            logger.error(f"❌ 自动注册群聊失败: {str(e)}", exc_info=True)
            logger.warning("⚠️ 定时器未启动，需要等待群聊事件触发")

    # 启动历史开奖定期同步（每60分钟一次）
    if not is_testing and scheduler:
        try:
            scheduler.start_history_sync(draw_repo=container.draw_repo(), draw_client=draw_client, interval_minutes=60)
            logger.info("✅ 历史开奖定期同步任务已启动（60分钟）")
        except Exception as e:
            logger.warning(f"⚠️ 历史开奖同步任务启动失败: {str(e)}")

    yield

    # 关闭时
    logger.info("🔴 应用关闭中...")

    # 停止自动刷新
    if not is_testing:
        draw_client.stop_auto_refresh()

    # 关闭调度器
    if scheduler:
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

# 导入路由
from biz.game.webhook import webhook_api
from biz.chat.api import chat_api
from biz.admin.api import admin_api
from biz.draw.api import draw_api
from biz.home.api import home_api
from biz.users.api import members_api, agents_api, rebate_api, personal_api
from biz.roles.api import role_api, subaccount_api
from biz.auth.api import auth_api
from biz.reports.api import report_api

# 使用FastAPI依赖覆盖机制
app.dependency_overrides[webhook_api.get_game_service] = lambda: container.game_service()
app.dependency_overrides[webhook_api.get_user_service] = lambda: container.user_service()
app.dependency_overrides[webhook_api.get_chat_repo] = lambda: container.chat_repo()
app.dependency_overrides[webhook_api.get_bot_client] = lambda: container.bot_api_client()
app.dependency_overrides[admin_api.get_admin_service] = lambda: container.admin_service()
app.dependency_overrides[draw_api.get_draw_service] = lambda: container.draw_service()
app.dependency_overrides[home_api.get_home_service] = lambda: container.home_service()
app.dependency_overrides[members_api.get_member_service] = lambda: container.member_service()
app.dependency_overrides[agents_api.get_agent_service] = lambda: container.agent_service()
app.dependency_overrides[rebate_api.get_rebate_service] = lambda: container.rebate_service()
app.dependency_overrides[personal_api.get_personal_service] = lambda: container.personal_service()
app.dependency_overrides[role_api.get_role_service] = lambda: container.role_service()
app.dependency_overrides[subaccount_api.get_subaccount_service] = lambda: container.subaccount_service()
app.dependency_overrides[auth_api.get_admin_service] = lambda: container.admin_service()
app.dependency_overrides[report_api.get_report_service] = lambda: container.report_service()

# 注册路由
app.include_router(webhook_api.router)  # Webhook路由（不使用前缀）
app.include_router(chat_api.router)  # Chat管理API
app.include_router(admin_api.router)  # 管理后台API
app.include_router(draw_api.router)  # 开奖/彩票API
app.include_router(home_api.router)  # 首页统计API（真实数据）
app.include_router(members_api.router)  # 会员查询API
app.include_router(agents_api.router)  # 代理管理API
app.include_router(rebate_api.router)  # 退水配置API
app.include_router(personal_api.router)  # 个人中心API
app.include_router(role_api.router)  # 角色管理API
app.include_router(subaccount_api.router)  # 子账号管理API
app.include_router(auth_api.router)  # 认证API
app.include_router(report_api.router)  # 报表API

# Wire依赖注入
container.wire(modules=[
    "biz.game.webhook.webhook_api",
    "biz.chat.api.chat_api",
    "biz.admin.api.admin_api",
    "biz.draw.api.draw_api",
    "biz.home.api.home_api",
    "biz.users.api.members_api",
    "biz.users.api.agents_api",
    "biz.users.api.rebate_api",
    "biz.users.api.personal_api",
    "biz.roles.api.role_api",
    "biz.roles.api.subaccount_api",
    "biz.auth.api.auth_api",
    "biz.reports.api.report_api",
])

@app.get("/health")
async def health_check():
    from datetime import datetime
    ts = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
    return {"status": "healthy", "timestamp": ts}


# 测试端点
@app.get("/")
async def root():
    return {
        "message": "Game Bot API",
        "version": "2.0.0",
        "docs": "/docs"
    }


if __name__ == '__main__':
    import sys
    # 确保项目根目录在 sys.path 中
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 生产环境配置
    uvicorn.run(
        'biz.application:app',
        host='0.0.0.0',
        port=3003,  # 使用3003端口，与Node.js版本保持一致
        reload=False,  # 生产环境关闭热重载
        workers=1  # 单worker，避免调度器重复
    )
