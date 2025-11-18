# 管理后台开发计划（后端）

## 总体原则

- 不使用令牌与登录态：所有管理端接口暂不做认证与权限校验。
- 统一响应：所有接口返回 `200`，用 `code/message/data` 表示结果，错误通过 `code!=200` 表示。
- 路由前缀：管理端统一挂载在 `/api/*`，与机器人服务路由分离。
- 游戏名映射：响应字段统一使用中文值 `"新奥六合彩"`、`"168澳洲幸运8"`，内部值做双向映射。
- 一致性：分页统一返回 `data.list/total/page/pageSize`，时间格式 `YYYY-MM-DD HH:mm:ss`。

## 响应封装与错误处理

### 统一响应函数（Python示例）

```python
def success_response(data, message='操作成功'):
    """成功响应封装"""
    return {
        'code': 200,
        'message': message,
        'data': data
    }

def error_response(code, message, data=None):
    """错误响应封装"""
    return {
        'code': code,
        'message': message,
        'data': data
    }

def paginate_response(list_data, total, page, page_size, message='操作成功', summary=None, cross_page_stats=None):
    """分页响应封装"""
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
```

### 错误码常量定义

| 错误码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | 成功 | 所有成功请求 |
| 400 | 请求参数错误 | 参数验证失败、格式错误 |
| 401 | 未授权 | 需要认证的接口（预留） |
| 403 | 无权限访问 | 权限校验失败（预留） |
| 404 | 资源不存在 | 查询的数据不存在 |
| 500 | 服务器内部错误 | 未预期的异常 |
| 1001 | 账号或密码错误 | 登录失败 |
| 1003 | 账号已被禁用 | 账号状态异常 |
| 1004 | 账号不存在 | 查询账号不存在 |
| 2001 | 账号已存在 | 创建时账号重复 |
| 2002 | 密码格式不正确 | 密码不符合规则 |
| 2003 | 余额不足 | 账户余额不足 |
| 3001 | 数据不存在 | 通用数据不存在 |
| 3002 | 数据已被删除 | 数据已删除 |

### 响应格式检查清单

开发时确保：
- [ ] HTTP 状态码统一返回 200
- [ ] 响应体包含 code、message、data 三个字段
- [ ] code 为数字类型，200 表示成功
- [ ] message 为字符串类型，不能为空
- [ ] data 不能为 undefined，无数据时使用 null
- [ ] 列表接口包含 list、total、page、pageSize
- [ ] 错误响应时 data 必须为 null
- [ ] 所有字段类型正确，符合 JSON 规范

## 数据验证规则

### 游戏名称验证（重要！）

**枚举值**：`["新奥六合彩", "168澳洲幸运8"]`

**涉及字段**：
- `betType`（注单表）
- `lotteryType`（开奖表、报表）
- `game`（退水配置）
- `gameTypes`（报表查询参数）

**验证方式**：
```python
VALID_GAMES = ["新奥六合彩", "168澳洲幸运8"]

def validate_game_name(game_name):
    if game_name not in VALID_GAMES:
        raise ValueError(f"游戏名称错误，只能是 {VALID_GAMES}")
    return game_name
```

**注意**：
- 所有涉及游戏名的接口都必须严格校验
- 响应中必须返回中文游戏名，不能使用英文或代码
- 数据库存储可以用代码，但响应时必须映射为中文

### 盘口验证

**枚举值**：`["A", "B", "C", "D"]`

**涉及字段**：
- `plate`（用户盘口）
- `affiliatedPlate`（所属盘口）
- `defaultRebate`（默认退水盘口）
- `openPlate`（代理开放盘口，数组类型）

**验证方式**：白名单校验

### 金额格式

- **类型**：`number`（数字类型，非字符串）
- **精度**：保留 2 位小数
- **负数**：表示支出或亏损（允许负数）
- **示例**：`1000.00`、`-200.00`、`0.50`

### 时间与日期格式

- **时间格式**：`YYYY-MM-DD HH:mm:ss`（如 `2025-11-10 15:30:00`）
- **日期格式**：`YYYY-MM-DD`（如 `2025-11-10`）
- **字段示例**：
  - `openTime`、`loginTime`、`betTime`、`settleTime` 等使用完整时间
  - `lotteryDate`、`dateStart`、`dateEnd` 等使用日期

### 账号与密码格式

- **账号**：
  - 长度：6-20 位
  - 字符：支持字母、数字、下划线
  - 唯一性：必须全局唯一
  - 大小写：建议统一转小写存储

- **密码**：
  - 长度：6-20 位
  - 存储：使用 bcrypt 加密，salt rounds 10+
  - 传输：前端传输时已加密或使用 HTTPS

### 用户类型

**枚举值**：
- `admin`：管理员
- `agent`：代理
- `member`：会员
- `general`：总代
- `shareholder`：股东

### 状态值

**账号状态**：`["正常", "冻结", "禁用"]`

**启用状态**：`["启用", "禁用"]`

**注单状态**：`["settled", "unsettled", "cancelled"]`

**交易状态**：`["success", "failed", "processing", "cancelled"]`

## 复杂数据结构

### 退水配置 JSON 结构

**完整结构示例**：
```json
{
  "independentRebate": false,
  "settings": {
    "earnRebate": 0.00,
    "gameSettings": [
      {
        "game": "新奥六合彩",
        "categories": [
          {
            "type": "1-10车号",
            "bPlate": 0.500,
            "maxRebate": 1
          }
        ]
      },
      {
        "game": "168澳洲幸运8",
        "categories": [
          {
            "type": "豹子",
            "bPlate": 1.000
          }
        ]
      }
    ]
  }
}
```

**字段说明**：
- `independentRebate` (boolean)：是否使用独立退水设置
  - `false`：继承上级退水配置
  - `true`：使用独立配置
- `settings.earnRebate` (number)：赚取退水百分比（代理专用）
- `settings.gameSettings` (array)：游戏退水设置
  - `game` (string)：游戏名称，必须是 "新奥六合彩" 或 "168澳洲幸运8"
  - `categories` (array)：玩法分类退水
    - `type` (string)：玩法名称
    - `bPlate` (number)：B盘退水百分比（保留3位小数）
    - `maxRebate` (number)：最高退水值（可选）

**彩种退水配置（Personal模块）**：
```json
{
  "games": ["新奥六合彩", "168澳洲幸运8"],
  "config": [
    {
      "game": "新奥六合彩",
      "categories": [
        {
          "category": "1-10车号",
          "isGroup": false,
          "level": 1,
          "plateA": 0.000,
          "plateB": 1.000,
          "plateC": 2.000,
          "plateD": 3.000
        }
      ]
    },
    {
      "game": "168澳洲幸运8",
      "categories": [
        {
          "category": "前三后三中三",
          "isGroup": true,
          "level": 0,
          "children": [
            {
              "category": "豹子",
              "plateA": 0.000,
              "plateB": 1.000,
              "plateC": 2.000,
              "plateD": 3.000
            }
          ]
        }
      ]
    }
  ]
}
```

**字段说明**：
- `isGroup` (boolean)：是否为分组
  - `true`：分组，有 `children` 字段
  - `false`：具体玩法，有 `plateA/B/C/D` 字段
- `level` (number)：层级
  - `0`：分组层
  - `1`：具体玩法层
- `plateA/B/C/D` (number)：各盘口退水百分比

### 报表汇总字段

**summary（当前页汇总）**：
用于注单、交易记录等接口，汇总当前页数据。

示例（注单）：
```json
{
  "summary": {
    "totalCount": 10,
    "totalAmount": 1000.00,
    "totalResult": -200.00
  }
}
```

示例（交易记录）：
```json
{
  "summary": {
    "totalCount": 5,
    "totalAmount": 5000.00,
    "totalFee": 50.00
  }
}
```

**crossPageStats（跨页统计）**：
仅用于财务报表，统计所有页的数据（不受分页限制）。

示例（财务报表）：
```json
{
  "crossPageStats": {
    "depositAmount": 50000.00,
    "withdrawalAmount": 30000.00,
    "bonus": 0.00,
    "irregularBet": 0.00,
    "returnAmount": 0.00,
    "handlingFee": 500.00,
    "depositWithdrawalFee": 300.00
  }
}
```

**使用规则**：
- 注单列表：返回 `summary`
- 交易记录：返回 `summary`
- 财务报表：返回 `crossPageStats`
- 输赢报表：不返回汇总（前端自行计算）
- 下线明细报表：特殊结构，分 `members` 和 `agents`

### 下线明细报表特殊结构

```json
{
  "code": 200,
  "data": {
    "members": {
      "list": [...],
      "total": 0,
      "page": 1,
      "pageSize": 20
    },
    "agents": {
      "list": [...],
      "total": 0,
      "page": 1,
      "pageSize": 20
    }
  }
}
```

**注意**：下线明细报表返回两个独立的分页列表（members 和 agents）。

## 模块与范围

- Auth
  - `POST /auth/login`、`POST /auth/logout`
  - 现阶段不启用认证流程，返回示例结构与成功态。
- Home
  - `GET /home/online-count`、`GET /home/online-trend`
  - 在线人数与趋势先用占位逻辑，预留后续接入心跳/WS。
- Users - Members
  - 列表、创建、修改、详情、登录日志、注单、交易、账变。
  - 建模会员实体与上下级关系、盘口、余额；聚合查询与分页。
- Users - Agents
  - 列表、创建、修改、详情、登录日志、下线会员、交易、账变。
  - 代理开盘、赚取退水、下级转账等配置字段。
- Rebate
  - `GET/PUT /users/rebate/:account`
  - 独立退水与继承、分游戏分玩法结构。
- Personal
  - 基本资料、域名、彩种退水配置、登录日志、密码修改。
  - 推广链接、域名增删、默认退水盘。
- Roles & Sub Accounts
  - 角色增删改查、权限树、子账号增删改查。
  - 权限编码与绑定策略后续与前端对齐。
- Reports
  - 财务总报表、财务报表、输赢、代理输赢、存取款、分类、下线明细、重新统计、导出。
  - 聚合统计与跨页汇总，预计算与导出 CSV。
- Lottery
  - 开奖列表与详情，对接现有开奖存储与同步任务。
- Health
  - `GET /health` 心跳，无认证。

## 开发日程（14 天）

### 第 1 天：基础框架与统一响应
**任务**：
- 路由前缀 `/api` 挂载、模块骨架与空实现
- **统一响应封装**：实现 `success_response`、`error_response`、`paginate_response` 函数
- **错误码常量定义**：创建错误码枚举类/常量文件
- **异常转码中间件**：捕获异常并转换为 `code/message/data` 格式
- **游戏名映射层**：实现游戏名验证与双向映射函数
- `GET /health` 完成并测试

**验收标准**：
- 统一响应函数可正常调用
- 异常能正确转换为统一格式
- health 接口返回正确格式

### 第 2 天：Lottery 与 Health
**任务**：
- `GET /lottery/results`：接入现有开奖数据，游戏名映射为中文
- `GET /lottery/results/:id`：单条查询
- **游戏名校验**：对 `lotteryType` 参数严格校验
- **时间格式**：确保 `lotteryTime` 格式为 `YYYY-MM-DD HH:mm:ss`
- 分页返回标准格式

**验收标准**：
- 返回的游戏名为中文
- 分页格式正确
- 查询参数验证生效

### 第 3 天：Home 模块
**任务**：
- `GET /home/online-count`：占位实现（返回示例数据）
- `GET /home/online-trend`：占位实现（返回时间点数组）
- **预留数据源接口**：注释说明后续接入心跳/WebSocket 的位置
- **缓存策略预留**：预留 Redis 缓存调用点

**验收标准**：
- 返回格式符合文档
- 占位数据合理

### 第 4 天：Users-Members（查询）
**任务**：
- `GET /users/members`：会员列表查询、分页、筛选
- `GET /users/members/:account`：会员详情
- `GET /users/members/:account/login-log`：登录日志分页
- **索引优化**：确保 `account`、`superior_id`、时间字段有索引
- **盘口显示**：`plate` 字段返回 "A盘"/"B盘" 等格式（带"盘"字）
- **在线状态**：占位逻辑（默认 `false`）

**验收标准**：
- 分页查询正常
- 筛选条件生效
- 时间格式正确

### 第 5 天：Users-Members（操作）
**任务**：
- `POST /users/members`：新增会员
  - 账号唯一性校验
  - 密码 bcrypt 加密
  - 盘口格式验证（A/B/C/D）
  - 设置 `superior_id` 为当前登录代理
  - 从上级获取默认退水配置
  - 初始化 `balance=0`
- `PUT /users/members/:id`：修改会员
  - 只允许修改 `plate` 和 `companyRemarks`
  - 验证盘口值
- **错误码应用**：账号已存在返回 2001，参数错误返回 400

**验收标准**：
- 创建成功，数据库记录正确
- 错误码返回正确
- 参数验证生效

### 第 6 天：Users-Members（记录）
**任务**：
- `GET /users/members/:account/bet-orders`：注单列表
  - **游戏名校验**：`betType` 参数验证
  - **summary 汇总**：返回 `totalCount`、`totalAmount`、`totalResult`
  - 分页 + 汇总同时返回
- `GET /users/members/:account/transactions`：交易记录
  - **summary 汇总**：返回 `totalCount`、`totalAmount`、`totalFee`
- `GET /users/members/:account/account-changes`：账变记录（仅分页，无汇总）

**验收标准**：
- 汇总字段计算正确
- 游戏名显示为中文
- 筛选条件生效

### 第 7 天：Users-Agents（查询）
**任务**：
- `GET /users/agents`：代理列表
  - `plate` 字段返回多个盘口（如 "A盘,B盘"）
- `GET /users/agents/:account`：代理详情
  - 返回代理专属字段：`openPlate`、`earnRebate`、`subordinateTransfer`
- `GET /users/agents/:account/login-log`：登录日志
- `GET /users/agents/:account/members`：下线会员列表
  - 查询条件：`superior_id = agent_id`
  - 复用会员列表逻辑

**验收标准**：
- 代理字段返回正确
- 下线会员查询正确

### 第 8 天：Users-Agents（操作与记录）
**任务**：
- `POST /users/agents`：新增代理
  - 验证 `openPlate` 数组（元素必须为 A/B/C/D）
  - 验证 `earnRebate`（full/partial/none）
  - 生成唯一 `invite_code`
  - 初始化推广域名为空数组
- `PUT /users/agents/:id`：修改代理
- `GET /users/agents/:account/transactions`：交易记录（含 summary）
- `GET /users/agents/:account/account-changes`：账变记录

**验收标准**：
- 代理创建成功
- `openPlate` 数组验证生效
- 交易记录汇总正确

### 第 9 天：Rebate 与 Personal（基础）
**任务**：
- `GET /users/rebate/:account`：获取退水设置
  - 返回 JSON 结构（见"复杂数据结构"章节）
  - **游戏名验证**：`gameSettings.game` 必须为中文游戏名
- `PUT /users/rebate/:account`：更新退水设置
  - 验证 JSON 结构
  - 验证游戏名
- `GET /personal/basic`：个人基本信息
  - 返回推广链接、邀请码、域名列表
- `PUT /personal/basic`：更新基本信息
  - 验证 `defaultRebate` 为 A/B/C/D
- `POST /personal/promote/domain`：添加推广域名
  - 域名格式验证

**验收标准**：
- 退水配置结构正确
- 游戏名验证生效
- 个人信息字段完整

### 第 10 天：Personal（退水配置与日志）+ Roles 基础
**任务**：
- `GET /personal/lottery-rebate-config`：获取彩种退水配置
  - **游戏名筛选**：`game` 参数验证
  - 返回分层结构（`isGroup`、`level`、`children`）
  - 固定返回两种游戏的配置
- `PUT /personal/lottery-rebate-config`：保存退水配置
  - **游戏名验证**：`game` 参数必须为中文
  - 验证 `plateA/B/C/D` 数值范围
- `GET /personal/login-log`：登录日志（分页）
- `PUT /personal/password`：修改密码
  - 验证旧密码
  - bcrypt 加密新密码
- `GET /roles`、`GET /roles/:id`：角色列表与详情（基础实现）

**验收标准**：
- 分层结构返回正确
- 游戏名验证生效
- 密码修改功能正常

### 第 11 天：Roles & Sub Accounts
**任务**：
- `POST /roles`、`PUT /roles/:id`、`DELETE /roles/:id`：角色增删改
- `GET /roles/permissions`：权限树
  - 三级结构：模块 -> 子模块 -> 具体权限
  - 权限编码规范（如 `personal-basic-1`）
- `GET /roles/sub-accounts`：子账号列表
- `POST /roles/sub-accounts`：新增子账号
  - 验证账号唯一性
  - 加密登录密码和支付密码
- `PUT /roles/sub-accounts/:id`、`DELETE /roles/sub-accounts/:id`

**验收标准**：
- 权限树结构正确
- 子账号创建成功
- 角色绑定正常

### 第 12 天：Reports（基础）
**任务**：
- `GET /reports/financial-summary`：财务总报表
  - 聚合统计字段
- `GET /reports/financial`：财务报表
  - **crossPageStats 实现**：统计所有页数据
- `GET /reports/win-loss`：输赢报表
  - **游戏名筛选**：`gameTypes` 数组验证
  - 不返回汇总（前端计算）
- `GET /reports/agent-win-loss`：代理输赢报表
  - 同输赢报表逻辑

**验收标准**：
- crossPageStats 计算正确
- 游戏名筛选生效
- 分页格式正确

### 第 13 天：Reports（明细与导出）
**任务**：
- `GET /reports/deposit-withdrawal`：存取款报表
- `GET /reports/category`：分类报表
  - **游戏名显示**：`lotteryType` 为中文
- `GET /reports/downline-details`：下线明细报表
  - **特殊结构**：返回 `members` 和 `agents` 两个分页对象
- `POST /reports/financial-summary/recalculate`：重新统计
  - 异步触发重新计算任务
- `GET /reports/export/:type`：导出 CSV
  - 字段顺序固定
  - 文件名规范：`{type}_{dateStart}_{dateEnd}.csv`

**验收标准**：
- 下线明细结构正确
- 导出功能正常
- CSV 格式规范

### 第 14 天：一致性校验与测试
**任务**：
- **响应格式检查**：所有接口符合响应格式检查清单
- **游戏名全面校验**：所有涉及游戏名的接口都返回中文
- **分页一致性**：确保所有列表接口包含 `list/total/page/pageSize`
- **错误处理一致性**：错误时 `data=null`、`code!=200`
- **时间格式统一**：`YYYY-MM-DD HH:mm:ss`
- **金额格式统一**：保留2位小数
- **单元测试**：核心接口成功/失败场景测试
- **集成测试**：完整业务流程测试
- **性能验证**：基本并发测试

**验收标准**：
- 所有接口符合规范
- 测试覆盖率达标
- 无明显性能问题

## 数据模型与仓库任务

### 用户表 `users`

**字段定义**：
- `id` (int, 主键)：用户ID
- `account` (varchar, 唯一索引)：账号
- `password` (varchar)：密码（bcrypt加密）
- `name` (varchar, 可选)：用户名称/昵称
- `real_name` (varchar, 可选)：真实姓名
- `user_type` (varchar)：用户类型（admin/agent/member/general/shareholder）
- `superior_id` (int, 索引, 可选)：上级ID（外键）
- `balance` (decimal(15,2))：余额
- `plate` (varchar)：所属盘口（A/B/C/D）
- `status` (varchar)：状态（正常/冻结/禁用）
- `company_remarks` (text, 可选)：公司备注
- `created_at` (datetime)：创建时间
- `updated_at` (datetime)：更新时间

**代理专属字段**：
- `open_plate` (json)：开放盘口列表，如 `["A", "B"]`
- `earn_rebate` (varchar)：赚取退水（full/partial/none）
- `subordinate_transfer` (varchar)：下级转账（enable/disable）
- `default_rebate_plate` (varchar)：新会员默认退水盘口（A/B/C/D）
- `invite_code` (varchar, 唯一)：邀请码
- `promotion_domains` (json)：推广域名列表

**索引建议**：
- `account`：唯一索引
- `superior_id`：普通索引
- `user_type`：普通索引
- `created_at`：时间范围查询索引

### 登录日志表 `login_logs`

**字段定义**：
- `id` (int, 主键)
- `user_id` (int, 索引)：用户ID
- `login_time` (datetime)：登录时间
- `ip_address` (varchar)：IP地址
- `ip_location` (varchar)：IP归属地（如"中国-广州-广东"）
- `operator` (varchar)：运营商（如"移动"）

**索引建议**：
- `user_id + login_time`：联合索引

### 注单表 `bet_orders`

**字段定义**：
- `id` (int, 主键)
- `order_no` (varchar, 唯一索引)：注单号
- `user_id` (int, 索引)：用户ID
- `bet_time` (datetime)：投注时间
- `settle_time` (datetime, 可选)：结算时间
- `bet_type` (varchar)：彩种，必须是 "新奥六合彩" 或 "168澳洲幸运8"
- `bet_content` (text)：投注内容
- `bet_amount` (decimal(15,2))：投注金额
- `rebate` (decimal(15,2))：退水
- `bet_result` (decimal(15,2))：输赢结果（负数为输）
- `status` (varchar)：状态（settled/unsettled/cancelled）
- `ip_address` (varchar, 可选)：投注IP

**索引建议**：
- `order_no`：唯一索引
- `user_id + bet_time`：联合索引
- `bet_type + bet_time`：联合索引
- `status`：普通索引

**聚合查询**：
- `summary`：汇总当前页的 `totalCount`、`totalAmount`、`totalResult`

### 交易记录表 `transactions`

**字段定义**：
- `id` (int, 主键)
- `user_id` (int, 索引)：用户ID
- `transaction_time` (datetime)：交易时间
- `transaction_type` (varchar)：交易类型（deposit/withdrawal/transfer/recharge/deduction）
- `amount` (decimal(15,2))：金额
- `fee` (decimal(15,2))：手续费
- `transaction_info` (varchar)：交易信息
- `status` (varchar)：状态（success/failed/processing/cancelled）
- `processor` (varchar)：处理人
- `review_comments` (text, 可选)：审核备注

**索引建议**：
- `user_id + transaction_time`：联合索引
- `transaction_type`：普通索引
- `status`：普通索引

**聚合查询**：
- `summary`：汇总 `totalCount`、`totalAmount`、`totalFee`

### 账变记录表 `account_changes`

**字段定义**：
- `id` (int, 主键)
- `user_id` (int, 索引)：用户ID
- `change_time` (datetime)：变动时间
- `change_type` (varchar)：变动类型（deposit/withdrawal/transfer/recharge/deduction/bet/win/rebate）
- `balance_before` (decimal(15,2))：变动前余额
- `change_value` (decimal(15,2))：变动金额（正数为增加，负数为减少）
- `balance_after` (decimal(15,2))：变动后余额
- `operator` (varchar)：操作人

**索引建议**：
- `user_id + change_time`：联合索引
- `change_type`：普通索引

### 退水配置表 `rebate_settings`

**字段定义**：
- `id` (int, 主键)
- `user_id` (int, 唯一索引)：用户ID
- `independent_rebate` (boolean)：是否独立退水
- `earn_rebate` (decimal(5,3))：赚取退水百分比
- `game_settings` (json)：游戏退水设置（JSON结构）
- `updated_at` (datetime)：更新时间

**JSON结构**：见"复杂数据结构"章节

### 角色权限表

**roles 表**：
- `id` (int, 主键)
- `role_name` (varchar, 唯一)：角色名称
- `role_code` (varchar, 唯一)：角色编码
- `remarks` (text)：备注
- `status` (varchar)：状态（启用/禁用）
- `created_at` (datetime)：创建时间

**role_permissions 表**：
- `id` (int, 主键)
- `role_id` (int, 索引)：角色ID
- `permission_code` (varchar)：权限编码（如 `personal-basic-1`）

**sub_accounts 表**：
- `id` (int, 主键)
- `parent_user_id` (int, 索引)：主账号ID
- `account` (varchar, 唯一)：子账号
- `password` (varchar)：登录密码
- `payment_password` (varchar)：支付密码
- `account_name` (varchar)：账户名称
- `role_id` (int)：角色ID
- `status` (varchar)：状态（启用/禁用）
- `created_at` (datetime)：创建时间

### 开奖结果表 `lottery_results`

**字段定义**：
- `id` (int, 主键)
- `issue_number` (varchar)：期数
- `lottery_time` (datetime)：开奖时间
- `lottery_type` (varchar)：彩种，必须是 "新奥六合彩" 或 "168澳洲幸运8"
- `numbers` (json)：开出号码数组
- `champion_sum` (int, 可选)：冠亚军和
- `champion_size` (varchar, 可选)：冠亚军和大小
- `champion_parity` (varchar, 可选)：冠亚军和单双
- `dragon_tiger_1` ~ `dragon_tiger_5` (varchar, 可选)：龙虎

**索引建议**：
- `lottery_type + issue_number`：唯一索引
- `lottery_time`：时间查询索引

**数据来源**：复用现有开奖存储与同步任务

## 关键实现要点

### 统一响应封装
- 提供 `success_response`、`error_response`、`paginate_response` 三个封装函数
- 异常中间件捕获所有异常，转换为统一错误响应体
- 确保所有接口 HTTP 状态码统一返回 200
- 错误时 `data` 必须为 `null`（不能是 `undefined` 或省略）

### 中文枚举验证
- **游戏名**：严格校验为 `["新奥六合彩", "168澳洲幸运8"]`
- **状态值**：使用中文（"正常"/"冻结"/"禁用"）
- **盘口值**：`["A", "B", "C", "D"]`
- **注单/交易类型**：使用固定枚举值
- **映射策略**：
  - 数据库可以存储英文代码或数字
  - 响应时必须映射为中文显示值
  - 提供双向映射函数（中文 ↔ 代码）

### 分页与汇总
- **基础分页**：所有列表返回 `list/total/page/pageSize`
- **当前页汇总**：注单、交易记录返回 `summary` 字段
- **跨页统计**：财务报表返回 `crossPageStats` 字段
- **空列表处理**：`list` 为空数组 `[]`，`total` 为 `0`

### 游戏名映射层
- 创建游戏名映射工具类/函数
- 所有涉及游戏名的查询、插入、响应都经过映射
- 提供验证函数，拒绝非法游戏名

### 退水配置处理
- **继承逻辑**：`independentRebate=false` 时，从上级代理获取退水配置
- **独立配置**：`independentRebate=true` 时，使用自己的配置
- **创建会员时**：从上级代理的 `personal` 退水配置中获取默认值
- **分层结构**：支持 `isGroup` 和 `children` 嵌套结构

### 报表聚合策略
- **实时查询**：小数据量时直接查询计算
- **预计算**：建议每日定时任务预计算报表数据
- **汇总表**：创建 `daily_reports` 表存储每日统计
- **重新统计**：提供接口触发指定日期范围的重新计算

### 账号创建流程
**创建会员**：
1. 验证账号唯一性
2. 验证参数格式（盘口、密码等）
3. 密码 bcrypt 加密
4. 设置 `superior_id` 为当前登录代理ID
5. 从上级代理获取默认退水配置
6. 创建用户记录（`balance=0`）
7. 初始化退水配置记录

**创建代理**：
1. 验证账号唯一性
2. 验证 `openPlate` 数组格式
3. 密码加密
4. 生成唯一 `invite_code`
5. 创建用户记录
6. 初始化退水配置（从当前管理员获取）

### 登录日志记录
- 每次登录成功后记录
- 获取客户端IP地址
- 调用IP归属地查询API（或使用离线数据库）
- 记录运营商信息
- 异步写入，避免阻塞登录响应

### 密码安全
- 使用 bcrypt 加密，salt rounds 建议 10-12
- 登录时使用 `bcrypt.compare()` 验证
- 密码修改需验证旧密码
- 不存储明文密码，不在日志中记录密码

### 导出 CSV
- 查询条件与列表接口完全一致
- 字段顺序固定，按接口文档定义
- 文件名格式：`{报表类型}_{开始日期}_{结束日期}.csv`
- 中文列名与前端显示一致
- 大数据量分批查询，流式写入

### 路由隔离
- 管理端路由：`/api/*`（如 `/api/users/members`）
- 机器人端路由：保持原有路径（如 `/bot/*`）
- 中间件、认证逻辑独立
- 互不影响，互不干扰

### 后续认证留口
- 当前所有接口不启用认证
- 预留认证中间件挂载点
- 如需认证，可快速启用基于 Session 或 JWT 的认证
- 权限校验逻辑已在代码中注释预留

## 风险与依赖

- 报表聚合性能：建议采用每日汇总表与定时预计算。
- 在线人数数据源：需后续接入心跳或 WebSocket。
- 权限绑定与编码：待前端提供权限编码与接口映射规范。
- 玩法字典与退水结构：需统一玩法全集来源与边界规则。

## 验收标准

接口开发完成后，必须满足以下所有标准：

### 响应格式验收
- [ ] 接口响应严格满足文档示例结构与字段命名
- [ ] 分页结构包含 `list`、`total`、`page`、`pageSize` 四个字段
- [ ] 汇总字段完整返回（注单/交易返回 `summary`，财务报表返回 `crossPageStats`）
- [ ] 空列表返回空数组 `[]`，不是 `null` 或 `undefined`
- [ ] 错误响应时 `data=null` 且 `code!=200`
- [ ] HTTP 状态码统一返回 `200`

### 数据格式验收
- [ ] **游戏名称必须为中文**："新奥六合彩" 或 "168澳洲幸运8"
  - 所有涉及游戏名的字段（`betType`、`lotteryType`、`game`、`gameTypes`）都返回中文
  - 查询参数中的游戏名也必须校验为中文
- [ ] 时间格式统一为 `YYYY-MM-DD HH:mm:ss`
- [ ] 日期格式统一为 `YYYY-MM-DD`
- [ ] 金额字段为 `number` 类型，保留 2 位小数
- [ ] 盘口值为 `A`、`B`、`C`、`D` 之一（或显示为 "A盘"、"B盘" 等）
- [ ] 中文枚举与格式校验一致（状态、用户类型等）

### 业务逻辑验收
- [ ] 账号创建时验证唯一性，重复时返回错误码 `2001`
- [ ] 密码使用 bcrypt 加密存储，salt rounds >= 10
- [ ] 会员创建时自动继承上级代理的退水配置
- [ ] 代理创建时生成唯一 `invite_code`
- [ ] 登录时记录登录日志（IP、归属地、运营商）
- [ ] 退水配置支持独立与继承两种模式

### 功能完整性验收
- [ ] 所有 51 个接口均已实现
- [ ] 导出接口返回符合筛选条件的 CSV 流
- [ ] 重新统计接口能触发异步计算
- [ ] 管理端 `/api/*` 与机器人端路由隔离，互不影响运行

### 性能与安全验收
- [ ] 列表查询使用分页，避免全表扫描
- [ ] 敏感操作（创建、修改、删除）记录操作日志
- [ ] 所有输入参数进行验证，防止SQL注入
- [ ] 大数据量查询响应时间 < 3 秒

### 测试验收
- [ ] 单元测试覆盖成功和失败场景
- [ ] 集成测试验证完整业务流程
- [ ] 基本并发测试通过（100+ 并发请求）