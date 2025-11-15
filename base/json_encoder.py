"""
统一的 JSON 编码器
用于处理 Decimal、datetime 等 Python 标准 JSON 编码器不支持的类型
"""
import json
from decimal import Decimal
from datetime import datetime, date


class DecimalEncoder(json.JSONEncoder):
    """
    自定义 JSON 编码器，处理 Decimal、datetime 和 date 类型

    用法:
        json.dumps(data, cls=DecimalEncoder)
    """

    def default(self, obj):
        """
        重写 default 方法以支持自定义类型序列化

        Args:
            obj: 需要序列化的对象

        Returns:
            序列化后的值
        """
        if isinstance(obj, Decimal):
            # 将 Decimal 转换为 float 用于 JSON 序列化
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            # 将 datetime/date 转换为 ISO 格式字符串
            return obj.isoformat()
        return super().default(obj)


def safe_json_dumps(obj, **kwargs):
    """
    安全的 JSON 序列化函数，自动使用 DecimalEncoder

    Args:
        obj: 需要序列化的对象
        **kwargs: 传递给 json.dumps 的其他参数

    Returns:
        str: JSON 字符串

    用法:
        from base.json_encoder import safe_json_dumps
        json_str = safe_json_dumps({"balance": Decimal("100.50")})
    """
    # 强制使用 DecimalEncoder，即使用户传入了其他 cls
    kwargs['cls'] = DecimalEncoder
    return json.dumps(obj, **kwargs)
