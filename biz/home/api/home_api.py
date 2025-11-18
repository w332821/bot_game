from fastapi import APIRouter, Query, Depends
from base.api import UnifyResponse
from base.exception import UnifyException
from dependency_injector.wiring import inject, Provide
from biz.containers import Container
from biz.home.service.home_service import HomeService
from biz.auth.dependencies import get_current_admin
from datetime import datetime

router = APIRouter(prefix="/api/home", tags=["home"]) 


@inject
def get_home_service(service: HomeService = Depends(Provide[Container.home_service])) -> HomeService:
    return service


@router.get("/online-count", response_class=UnifyResponse)
async def online_count(
    windowMinutes: int = Query(5, ge=1, le=60),
    current_admin: dict = Depends(get_current_admin),
    home_service: HomeService = Depends(get_home_service)
):
    try:
        counts = await home_service.get_online_counts(window_minutes=windowMinutes)
        return counts
    except Exception as e:
        raise UnifyException(str(e), biz_code=500, http_code=200)


@router.get("/online-trend", response_class=UnifyResponse)
async def online_trend(
    date: str | None = Query(None),
    current_admin: dict = Depends(get_current_admin),
    home_service: HomeService = Depends(get_home_service)
):
    try:
        metric_date = date or datetime.utcnow().strftime("%Y-%m-%d")
        try:
            datetime.strptime(metric_date, "%Y-%m-%d")
        except Exception:
            raise UnifyException("日期格式错误，应为 YYYY-MM-DD", biz_code=400, http_code=200)
        trend = await home_service.get_online_trend(metric_date)
        return trend
    except UnifyException:
        raise
    except Exception as e:
        raise UnifyException(str(e), biz_code=500, http_code=200)