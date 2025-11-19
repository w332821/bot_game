from fastapi import APIRouter, Depends, Query
from typing import Optional
from dependency_injector.wiring import inject, Provide

from biz.yueliao.service.yueliao_user_service import YueliaoUserService
from biz.containers import Container
from base.api import UnifyResponse
from base.exception import UnifyException
from base.error_codes import ErrorCode

router = APIRouter(prefix="/api/admin/yueliao-users", tags=["悦聊用户管理"])


@router.get("/list", response_class=UnifyResponse)
@inject
async def get_yueliao_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（昵称/手机号/悦聊ID）"),
    service: YueliaoUserService = Depends(Provide[Container.yueliao_user_service])
):
    try:
        result = await service.get_users(
            page=page,
            page_size=page_size,
            search=search
        )
        return result
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.get("/detail/{user_id}", response_class=UnifyResponse)
@inject
async def get_yueliao_user_detail(
    user_id: str,
    service: YueliaoUserService = Depends(Provide[Container.yueliao_user_service])
):
    try:
        user = await service.get_user_detail(user_id)
        if not user:
            raise UnifyException("用户不存在", biz_code=ErrorCode.DATA_NOT_FOUND, http_code=404)
        return user
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.get("/search/phone", response_class=UnifyResponse)
@inject
async def search_by_phone(
    phone: str = Query(..., description="手机号"),
    service: YueliaoUserService = Depends(Provide[Container.yueliao_user_service])
):
    try:
        user = await service.search_user_by_phone(phone)
        if not user:
            raise UnifyException("用户不存在", biz_code=ErrorCode.DATA_NOT_FOUND, http_code=404)
        return user
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.get("/search/yueliao-id", response_class=UnifyResponse)
@inject
async def search_by_yueliao_id(
    yueliao_id: str = Query(..., description="悦聊ID"),
    service: YueliaoUserService = Depends(Provide[Container.yueliao_user_service])
):
    try:
        user = await service.search_user_by_yueliao_id(yueliao_id)
        if not user:
            raise UnifyException("用户不存在", biz_code=ErrorCode.DATA_NOT_FOUND, http_code=404)
        return user
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.get("/statistics", response_class=UnifyResponse)
@inject
async def get_statistics(
    service: YueliaoUserService = Depends(Provide[Container.yueliao_user_service])
):
    try:
        stats = await service.get_user_statistics()
        return stats
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)
