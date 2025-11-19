from typing import Optional
from fastapi import APIRouter, Query, Depends
from base.api import UnifyResponse
from base.exception import UnifyException
from dependency_injector.wiring import inject, Provide
from biz.containers import Container
from biz.users.service.bot_user_service import BotUserService
from biz.auth.dependencies import get_current_admin

router = APIRouter(prefix="/api/bot-users", tags=["bot-users"])


@inject
def get_bot_user_service(service: BotUserService = Depends(Provide[Container.bot_user_service])) -> BotUserService:
    return service


@router.get("", response_class=UnifyResponse)
async def list_bot_users(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    chatId: Optional[str] = Query(None),
    hasMemberProfile: Optional[bool] = Query(None),
    username: Optional[str] = Query(None),
    current_admin: dict = Depends(get_current_admin),
    service: BotUserService = Depends(get_bot_user_service)
):
    try:
        result = await service.list_bot_users(
            page=page,
            page_size=pageSize,
            chat_id=chatId,
            has_member_profile=hasMemberProfile,
            username=username
        )
        return {
            "list": result["list"],
            "total": result["total"],
            "page": page,
            "pageSize": pageSize
        }
    except Exception as e:
        raise UnifyException(str(e), biz_code=500, http_code=500)


@router.get("/chats", response_class=UnifyResponse)
async def list_bot_chats(
    current_admin: dict = Depends(get_current_admin),
    service: BotUserService = Depends(get_bot_user_service)
):
    try:
        chats = await service.list_bot_chats()
        return {"list": chats}
    except Exception as e:
        raise UnifyException(str(e), biz_code=500, http_code=500)
