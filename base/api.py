import typing
import json
from fastapi.responses import JSONResponse
from base.json_encoder import DecimalEncoder


class UnifyResponse(JSONResponse):
    """
    统一的 API 响应类
    自动处理 Decimal、datetime 等类型的序列化
    """

    def render(self, content: typing.Any) -> bytes:
        new_content = {
            "code": 200,
            "message": '操作成功',
            "data": content
        }
        # Use custom encoder to handle Decimal and datetime types
        return json.dumps(
            new_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=DecimalEncoder
        ).encode("utf-8")


def success_response(data, message: str = '操作成功'):
    return {
        'code': 200,
        'message': message,
        'data': data
    }


def error_response(code: int, message: str, data=None):
    return {
        'code': code,
        'message': message,
        'data': data if data is not None else None
    }


def paginate_response(list_data, total, page, page_size, message: str = '操作成功', summary=None, cross_page_stats=None):
    """
    分页响应封装

    Args:
        list_data: 列表数据
        total: 总记录数
        page: 当前页码
        page_size: 每页数量
        message: 提示消息
        summary: 当前页汇总（如注单、交易记录）
        cross_page_stats: 跨页统计（如财务报表）

    Returns:
        dict: 统一的分页响应格式
    """
    result = {
        'code': 200,
        'message': message,
        'data': {
            'list': list_data or [],
            'total': total or 0,
            'page': page or 1,
            'pageSize': page_size or 20
        }
    }
    # 添加当前页汇总（如注单、交易记录）
    if summary is not None:
        result['data']['summary'] = summary
    # 添加跨页统计（如财务报表）
    if cross_page_stats is not None:
        result['data']['crossPageStats'] = cross_page_stats
    return result
