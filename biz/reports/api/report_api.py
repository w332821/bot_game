"""
报表API路由
实现9个报表接口
"""
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel, Field
from base.api import success_response, error_response, paginate_response
from base.error_codes import ErrorCode
from base.game_name_mapper import validate_game_name, VALID_GAMES_CN

from biz.reports.service.report_service import ReportService
from biz.reports.models.report_models import RecalculateRequest
from dependency_injector.wiring import inject, Provide
from biz.containers import Container

router = APIRouter(prefix="/api/reports", tags=["reports"])


# ===== 依赖注入 =====

@inject
def get_report_service(service: ReportService = Depends(Provide[Container.report_service])) -> ReportService:
    return service


# ===== 1. 财务总报表 =====

@router.get("/financial-summary")
async def get_financial_summary(
    dateStart: str = Query(..., description="开始日期 YYYY-MM-DD"),
    dateEnd: str = Query(..., description="结束日期 YYYY-MM-DD"),
    plate: Optional[str] = Query(None, pattern="^[ABCD]$", description="盘口"),
    report_service: ReportService = Depends(get_report_service)
):
    """
    财务总报表

    返回指定日期范围内的财务汇总数据
    """
    try:
        result = await report_service.get_financial_summary(dateStart, dateEnd, plate)
        return success_response(data=result, message="查询成功")
    except Exception as e:
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"查询失败: {str(e)}",
            data=None
        )


# ===== 2. 财务报表（含跨页统计） =====

@router.get("/financial")
async def get_financial_report(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    dateStart: str = Query(..., description="开始日期 YYYY-MM-DD"),
    dateEnd: str = Query(..., description="结束日期 YYYY-MM-DD"),
    account: Optional[str] = Query(None, description="账号"),
    report_service: ReportService = Depends(get_report_service)
):
    """
    财务报表

    返回分页的财务明细数据,包含跨页统计(crossPageStats)
    """
    try:
        result = await report_service.get_financial_report(page, pageSize, dateStart, dateEnd, account)

        return paginate_response(
            list_data=result["list"],
            total=result["total"],
            page=page,
            page_size=pageSize,
            message="查询成功",
            cross_page_stats=result.get("cross_page_stats")
        )
    except Exception as e:
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"查询失败: {str(e)}",
            data=None
        )


# ===== 3. 输赢报表 =====

@router.get("/win-loss")
async def get_win_loss_report(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    dateStart: str = Query(..., description="开始日期 YYYY-MM-DD"),
    dateEnd: str = Query(..., description="结束日期 YYYY-MM-DD"),
    gameTypes: Optional[List[str]] = Query(None, description="游戏类型(中文)"),
    account: Optional[str] = Query(None, description="账号"),
    report_service: ReportService = Depends(get_report_service)
):
    """
    输赢报表

    支持按游戏类型筛选(必须是中文名称)
    """
    try:
        # 验证游戏类型
        if gameTypes:
            for gt in gameTypes:
                if gt not in VALID_GAMES_CN:
                    return error_response(
                        code=ErrorCode.BAD_REQUEST,
                        message=f"游戏类型错误,只能是{VALID_GAMES_CN}",
                        data=None
                    )

        result = await report_service.get_win_loss_report(page, pageSize, dateStart, dateEnd, gameTypes, account)

        return paginate_response(
            list_data=result["list"],
            total=result["total"],
            page=page,
            page_size=pageSize,
            message="查询成功"
        )
    except Exception as e:
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"查询失败: {str(e)}",
            data=None
        )


# ===== 4. 代理输赢报表 =====

@router.get("/agent-win-loss")
async def get_agent_win_loss_report(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    dateStart: str = Query(...),
    dateEnd: str = Query(...),
    gameTypes: Optional[List[str]] = Query(None),
    account: Optional[str] = Query(None),
    report_service: ReportService = Depends(get_report_service)
):
    """
    代理输赢报表

    与会员输赢报表类似,但仅显示代理数据
    """
    try:
        if gameTypes:
            for gt in gameTypes:
                if gt not in VALID_GAMES_CN:
                    return error_response(
                        code=ErrorCode.BAD_REQUEST,
                        message=f"游戏类型错误,只能是{VALID_GAMES_CN}",
                        data=None
                    )

        result = await report_service.get_agent_win_loss_report(page, pageSize, dateStart, dateEnd, gameTypes, account)

        return paginate_response(
            list_data=result["list"],
            total=result["total"],
            page=page,
            page_size=pageSize,
            message="查询成功"
        )
    except Exception as e:
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"查询失败: {str(e)}",
            data=None
        )


# ===== 5. 存取款报表 =====

@router.get("/deposit-withdrawal")
async def get_deposit_withdrawal_report(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    dateStart: str = Query(...),
    dateEnd: str = Query(...),
    transactionType: Optional[str] = Query(None, description="交易类型: deposit/withdrawal"),
    report_service: ReportService = Depends(get_report_service)
):
    """
    存取款报表

    查询存款和取款记录
    """
    try:
        result = await report_service.get_deposit_withdrawal_report(page, pageSize, dateStart, dateEnd, transactionType)

        return paginate_response(
            list_data=result["list"],
            total=result["total"],
            page=page,
            page_size=pageSize,
            message="查询成功"
        )
    except Exception as e:
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"查询失败: {str(e)}",
            data=None
        )


# ===== 6. 分类报表 =====

@router.get("/category")
async def get_category_report(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    dateStart: str = Query(...),
    dateEnd: str = Query(...),
    lotteryType: Optional[str] = Query(None, description="彩种(中文)"),
    report_service: ReportService = Depends(get_report_service)
):
    """
    分类报表

    按玩法分类统计
    """
    try:
        if lotteryType and lotteryType not in VALID_GAMES_CN:
            return error_response(
                code=ErrorCode.BAD_REQUEST,
                message=f"彩种错误,只能是{VALID_GAMES_CN}",
                data=None
            )

        result = await report_service.get_category_report(page, pageSize, dateStart, dateEnd, lotteryType)

        return paginate_response(
            list_data=result["list"],
            total=result["total"],
            page=page,
            page_size=pageSize,
            message="查询成功"
        )
    except Exception as e:
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"查询失败: {str(e)}",
            data=None
        )


# ===== 7. 下线明细报表（特殊结构） =====

@router.get("/downline-details")
async def get_downline_details(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    account: str = Query(..., description="上级账号"),
    report_service: ReportService = Depends(get_report_service)
):
    """
    下线明细报表

    返回特殊结构: { members: {...}, agents: {...} }
    """
    try:
        result = await report_service.get_downline_details(page, pageSize, account)

        return success_response(data=result, message="查询成功")
    except Exception as e:
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"查询失败: {str(e)}",
            data=None
        )


# ===== 8. 重新统计财务总报表 =====

@router.post("/financial-summary/recalculate")
async def recalculate_financial_summary(
    request: RecalculateRequest,
    report_service: ReportService = Depends(get_report_service)
):
    """
    重新统计财务总报表

    异步任务,立即返回成功
    """
    try:
        result = await report_service.recalculate_financial_summary(request.dateStart, request.dateEnd)

        return success_response(data=None, message="重新统计任务已启动")
    except Exception as e:
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"任务启动失败: {str(e)}",
            data=None
        )


# ===== 9. 导出CSV =====

@router.get("/export/{type}")
async def export_report(
    type: str,
    dateStart: str = Query(...),
    dateEnd: str = Query(...),
    account: Optional[str] = Query(None),
    report_service: ReportService = Depends(get_report_service)
):
    """
    导出报表为CSV

    支持类型: financial, win-loss, agent-win-loss, deposit-withdrawal, category
    """
    try:
        # 根据类型获取数据
        if type == "financial":
            result = await report_service.get_financial_report(1, 10000, dateStart, dateEnd, account)
        elif type == "win-loss":
            result = await report_service.get_win_loss_report(1, 10000, dateStart, dateEnd, None, account)
        elif type == "agent-win-loss":
            result = await report_service.get_agent_win_loss_report(1, 10000, dateStart, dateEnd, None, account)
        elif type == "deposit-withdrawal":
            result = await report_service.get_deposit_withdrawal_report(1, 10000, dateStart, dateEnd, None)
        elif type == "category":
            result = await report_service.get_category_report(1, 10000, dateStart, dateEnd, None)
        else:
            return error_response(
                code=ErrorCode.BAD_REQUEST,
                message=f"不支持的导出类型: {type}",
                data=None
            )

        # 生成CSV
        csv_content = report_service.generate_csv_content(type, result["list"])

        # 返回流式响应
        filename = f"{type}_{dateStart}_{dateEnd}.csv"
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"导出失败: {str(e)}",
            data=None
        )
