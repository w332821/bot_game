# 游戏名映射工具使用指南

## 概述

为确保API统一性，所有对外接口必须使用**中文游戏名**，数据库内部可以使用代码。

本指南说明如何使用 `base/game_name_mapper.py` 工具模块来处理游戏名的验证和转换。

## 枚举值

### 中文游戏名（对外API）
- `"新奥六合彩"`
- `"168澳洲幸运8"`

### 内部代码（数据库）
- `"liuhecai"` → 新奥六合彩
- `"lucky8"` → 168澳洲幸运8

## 使用方法

### 1. 验证游戏名（API输入参数验证）

```python
from base.game_name_mapper import validate_game_name
from base.api import error_response

def some_api_function(game_name: str):
    try:
        # 验证游戏名是否合法
        validated_name = validate_game_name(game_name)
        # 验证通过，继续处理...
    except ValueError as e:
        # 游戏名不合法，返回错误
        return error_response(400, str(e))
```

### 2. 中文转代码（存入数据库前）

```python
from base.game_name_mapper import game_name_to_code

# API接收到中文游戏名
game_name = "新奥六合彩"  # 来自请求参数

# 转换为代码，用于数据库查询或存储
game_code = game_name_to_code(game_name)  # 返回 "liuhecai"

# 使用代码查询数据库
results = await db.query("SELECT * FROM bet_orders WHERE game_type = ?", game_code)
```

### 3. 代码转中文（API响应前）

```python
from base.game_name_mapper import game_code_to_name

# 从数据库读取的记录，使用代码
db_record = {
    "id": 1,
    "game_type": "lucky8",  # 数据库中的代码
    "amount": 100.00
}

# 转换为中文返回给API
db_record["game_type"] = game_code_to_name(db_record["game_type"])
# 现在 game_type = "168澳洲幸运8"

# 返回给前端
return success_response(db_record)
```

## 最佳实践

### Service 层完整示例

```python
from base.game_name_mapper import game_name_to_code, game_code_to_name
from base.api import success_response, paginate_response

class MemberService:
    """会员服务"""

    async def get_bet_orders(self, account: str, game_name: str = None, page: int = 1, page_size: int = 20):
        """
        获取会员注单列表

        Args:
            account: 会员账号
            game_name: 游戏名称（中文），可选
            page: 页码
            page_size: 每页数量

        Returns:
            统一响应格式
        """
        # 1. 如果有游戏名参数，先验证并转换为代码
        game_code = None
        if game_name:
            try:
                game_code = game_name_to_code(game_name)
            except ValueError:
                return error_response(400, f"游戏名称错误，只能是 新奥六合彩 或 168澳洲幸运8")

        # 2. 使用代码查询数据库
        orders, total = await self.repo.find_bet_orders(
            account=account,
            game_type=game_code,  # 使用代码查询
            page=page,
            page_size=page_size
        )

        # 3. 将结果中的代码转换为中文
        for order in orders:
            # 转换游戏类型字段
            if 'betType' in order:
                order['betType'] = game_code_to_name(order['betType'])

        # 4. 返回统一格式
        return paginate_response(orders, total, page, page_size)
```

### API 层示例

```python
from fastapi import APIRouter, Query
from base.game_name_mapper import VALID_GAMES_CN

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/members/{account}/bet-orders")
async def get_member_bet_orders(
    account: str,
    game_name: str = Query(None, description=f"游戏名称，可选值: {VALID_GAMES_CN}"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    member_service: MemberService = Depends(get_member_service)
):
    """
    获取会员注单列表

    Query参数:
        - game_name: 游戏名称（中文），可选
        - page: 页码
        - page_size: 每页数量
    """
    return await member_service.get_bet_orders(account, game_name, page, page_size)
```

## Repository 层示例

```python
from base.game_name_mapper import validate_game_code

class BetOrderRepository:
    """注单仓库"""

    async def find_by_game_type(self, game_type: str):
        """
        根据游戏类型查询注单

        Args:
            game_type: 游戏代码（如 "liuhecai", "lucky8"）
        """
        # 验证代码是否合法
        validate_game_code(game_type)

        # 执行查询
        async with self.session() as session:
            result = await session.execute(
                select(BetOrder).where(BetOrder.game_type == game_type)
            )
            return result.scalars().all()
```

## 涉及游戏名的字段

根据 DEV_PLAN.md 规范，以下字段必须使用中文游戏名：

| 字段名 | 所在表/模块 | 说明 |
|--------|------------|------|
| `betType` | 注单表 | 投注类型/游戏类型 |
| `lotteryType` | 开奖表 | 彩种类型 |
| `game` | 退水配置 | 游戏名称 |
| `gameTypes` | 报表查询参数 | 游戏类型数组 |

## 注意事项

### ✅ 正确做法

```python
# 1. API参数使用中文
@router.get("/api/lottery/results")
async def get_results(game_type: str = "新奥六合彩"):
    ...

# 2. API响应返回中文
response = {
    "lotteryType": "168澳洲幸运8",  # ✅ 正确
    "numbers": [1, 2, 3]
}

# 3. 查询参数验证
game_name = validate_game_name(request.game_type)

# 4. 数据库查询前转换
game_code = game_name_to_code(game_name)
results = await repo.find_by_game(game_code)

# 5. 返回前转换回中文
for result in results:
    result['game'] = game_code_to_name(result['game'])
```

### ❌ 错误做法

```python
# 1. API响应返回英文代码
response = {
    "lotteryType": "lucky8",  # ❌ 错误！应返回 "168澳洲幸运8"
    "numbers": [1, 2, 3]
}

# 2. 直接使用未验证的游戏名
game_type = request.game_type  # ❌ 未验证
results = await repo.find(game_type)

# 3. 混用中英文
if game == "lucky8" or game == "新奥六合彩":  # ❌ 不一致
    ...
```

## 常见问题

### Q1: 数据库应该存储中文还是代码？

**A:** 建议存储代码（如 `liuhecai`, `lucky8`），原因：
- 代码更短，节省存储空间
- 代码是英文，便于索引和查询
- 转换为中文显示由映射工具处理

### Q2: 如果需要支持新游戏怎么办？

**A:** 修改 `base/game_name_mapper.py`：
```python
# 1. 添加到枚举列表
VALID_GAMES_CN = ["新奥六合彩", "168澳洲幸运8", "新游戏名称"]

# 2. 添加映射关系
GAME_NAME_TO_CODE = {
    "新奥六合彩": "liuhecai",
    "168澳洲幸运8": "lucky8",
    "新游戏名称": "new_game"  # 添加
}

GAME_CODE_TO_NAME = {
    "liuhecai": "新奥六合彩",
    "lucky8": "168澳洲幸运8",
    "new_game": "新游戏名称"  # 添加
}
```

### Q3: 如何处理数组类型的游戏名参数？

**A:** 逐个验证和转换：
```python
from base.game_name_mapper import game_name_to_code

# 请求参数: gameTypes = ["新奥六合彩", "168澳洲幸运8"]
game_types_cn = request.gameTypes

# 转换为代码数组
game_codes = []
for game_cn in game_types_cn:
    try:
        game_codes.append(game_name_to_code(game_cn))
    except ValueError:
        return error_response(400, f"游戏名称 '{game_cn}' 不合法")

# 使用代码数组查询
results = await repo.find_by_games(game_codes)
```

## 测试

可以运行测试验证映射工具：

```bash
pytest test/test_base_infrastructure.py::TestGameNameMapper -v
```

测试覆盖：
- ✅ 游戏名验证
- ✅ 中文转代码
- ✅ 代码转中文
- ✅ 双向映射一致性
- ✅ 异常处理

## 相关文档

- [DEV_PLAN.md](./DEV_PLAN.md) - 开发计划和规范
- [API_DOCS(3).md](./API_DOCS(3).md) - API接口文档
- [base/error_codes.py](../base/error_codes.py) - 错误码定义
- [base/api.py](../base/api.py) - 统一响应封装

---

**最后更新**: 2025-11-18
**版本**: 1.0.0
