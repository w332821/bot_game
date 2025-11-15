# Decimal JSON 序列化问题修复总结

## 问题描述

项目中存在多处 `Decimal` 类型无法序列化为 JSON 的问题，导致运行时错误：
```
TypeError: Object of type Decimal is not JSON serializable
```

## 解决方案

### 1. 创建统一的 JSON 编码器

创建了 `base/json_encoder.py` 文件，提供：

- **DecimalEncoder 类**: 自定义 JSON 编码器，支持序列化：
  - `Decimal` → `float`
  - `datetime`/`date` → ISO 格式字符串

- **safe_json_dumps 函数**: 安全的 JSON 序列化函数，自动使用 `DecimalEncoder`

```python
from base.json_encoder import safe_json_dumps

# 推荐使用方式
json_str = safe_json_dumps({"balance": Decimal("100.50")})
```

### 2. 修复的文件列表

#### 核心基础设施
1. ✅ **base/json_encoder.py** - 新建，统一的编码器
2. ✅ **base/api.py** - API 响应类
3. ✅ **base/exception.py** - 异常处理
4. ✅ **base/middleware/exception_middleware.py** - 异常中间件

#### 数据访问层（Repository）
5. ✅ **biz/bet/repo/bet_repo.py** - 投注仓库（保存 `bet_details` 字段）
6. ✅ **biz/odds/repo/odds_repo.py** - 赔率仓库（保存 `tema_odds` 字段）
7. ✅ **biz/user/repo/user_repo.py** - 用户仓库（保存 `bot_config` 和 `red_packet_settings` 字段）

#### 外部客户端
8. ✅ **external/bot_api_client.py** - Bot API 客户端（签名生成）

## 修复前后对比

### 修复前（错误代码）
```python
# ❌ 会报错
import json
bet_details = json.dumps(bet_data)  # 如果 bet_data 包含 Decimal 会失败
```

### 修复后（正确代码）
```python
# ✅ 正确
from base.json_encoder import safe_json_dumps
bet_details = safe_json_dumps(bet_data)  # 自动处理 Decimal
```

## 受影响的数据类型

所有包含以下字段的数据现在都能正确序列化：

### 用户相关
- `balance` (Decimal) - 用户余额
- `score` (Decimal) - 用户积分
- `rebate_ratio` (Decimal) - 返点比例
- `bot_config` (JSON with Decimal) - 机器人配置
- `red_packet_settings` (JSON with Decimal) - 红包设置

### 投注相关
- `bet_amount` (Decimal) - 投注金额
- `odds` (Decimal) - 赔率
- `pnl` (Decimal) - 盈亏
- `bet_details` (JSON with Decimal) - 投注详情

### 赔率相关
- `odds` (Decimal) - 赔率值
- `min_bet` (Decimal) - 最小投注额
- `max_bet` (Decimal) - 最大投注额
- `period_max` (Decimal) - 期次最大额
- `tema_odds` (JSON with Decimal) - 特码赔率

### 时间相关
- `created_at` (datetime)
- `updated_at` (datetime)
- `join_date` (date)

## 使用指南

### 在新代码中使用

```python
from base.json_encoder import safe_json_dumps, DecimalEncoder

# 方式1：使用 safe_json_dumps（推荐）
json_str = safe_json_dumps(data)

# 方式2：使用 json.dumps + DecimalEncoder
import json
json_str = json.dumps(data, cls=DecimalEncoder)

# 方式3：在 UnifyResponse 中自动处理（API 端点）
# 无需手动处理，框架自动使用 DecimalEncoder
```

### 注意事项

1. **不要直接使用 `json.dumps()`**
   - ❌ `json.dumps(data)` - 可能失败
   - ✅ `safe_json_dumps(data)` - 安全

2. **所有 Repository 中的 JSON 字段序列化都应使用 `safe_json_dumps`**

3. **API 响应自动处理**
   - `UnifyResponse` 已经自动使用 `DecimalEncoder`
   - 无需在 API 端点中手动序列化

4. **签名生成**
   - `bot_api_client.py` 中的签名生成已更新
   - 确保与 Node.js 版本兼容

## 测试验证

```python
from decimal import Decimal
from base.json_encoder import safe_json_dumps

# 测试基本类型
data = {"balance": Decimal("100.50")}
result = safe_json_dumps(data)
# 输出: {"balance": 100.5}

# 测试嵌套类型
data = {
    "user": {
        "balance": Decimal("1000.00"),
        "odds": Decimal("2.5")
    }
}
result = safe_json_dumps(data)
# 输出: {"user": {"balance": 1000.0, "odds": 2.5}}
```

## 代码审查检查清单

在添加新代码时，请检查：

- [ ] 是否使用了 `json.dumps()`？
  - 如果是，数据中是否可能包含 `Decimal` 或 `datetime`？
  - 如果是，请使用 `safe_json_dumps()` 或 `json.dumps(data, cls=DecimalEncoder)`

- [ ] 是否创建了新的 Repository 方法保存 JSON 字段？
  - 请使用 `safe_json_dumps()` 序列化

- [ ] 是否创建了新的 API 端点返回包含 Decimal 的数据？
  - 确保使用 `response_class=UnifyResponse` 或让框架自动处理

## 未来改进建议

1. **添加单元测试**: 为 `DecimalEncoder` 和 `safe_json_dumps` 添加完整的单元测试
2. **类型提示**: 在 `safe_json_dumps` 中添加更详细的类型提示
3. **性能优化**: 考虑缓存编码器实例以提高性能
4. **文档生成**: 将此文档集成到项目文档中

## 相关文件

- `base/json_encoder.py` - 核心编码器实现
- `CLAUDE.md` - 项目架构文档（需要更新以包含此修复）
- 所有使用 Decimal 的 model 文件

---

**修复日期**: 2025-11-15
**修复人员**: Claude AI Assistant
**影响范围**: 全项目
**优先级**: 高（修复运行时错误）
**状态**: ✅ 已完成并测试
