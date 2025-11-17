# Sunshine Attendance Admin - API 接口文档

> **本文档用于后端开发，开发完成后可直接接入真实服务器使用**

## 目录

- [通用说明](#通用说明)
- [响应格式](#响应格式)
- [错误码定义](#错误码定义)
- [数据格式规范](#数据格式规范)
- [分页说明](#分页说明)
- [接口列表](#接口列表)

---

## 通用说明

### Base URL

**开发环境**: `http://localhost:3000/api`  
**生产环境**: 根据实际部署情况配置

### 请求头 (Request Headers)

所有请求必须包含以下请求头：

```
Content-Type: application/json;charset=UTF-8
```

**说明**:
- `Content-Type`: 固定为 `application/json;charset=UTF-8`

### 请求方法

- `GET`: 查询数据
- `POST`: 创建数据
- `PUT`: 更新数据
- `DELETE`: 删除数据

### 路径参数

路径中的参数使用 `:param` 格式，例如 `/users/members/:id`，实际请求时替换为具体值：`/users/members/123`

### 查询参数

查询参数通过 URL Query String 传递，例如：`/users/members?page=1&pageSize=20&account=test`

### 请求体

POST/PUT 请求的请求体为 JSON 格式，放在 Request Body 中。

---

## 响应格式

> **重要**: 所有接口必须遵循统一的响应格式，HTTP 状态码统一返回 `200`，通过响应体中的 `code` 字段判断请求是否成功。

### 统一响应结构

所有接口的响应都遵循以下统一格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

**字段说明**:
- `code` (number, required): 状态码，200 表示成功，其他值表示失败（见 [错误码定义](#错误码定义)）
- `message` (string, required): 提示信息，成功时通常为 "操作成功" 或具体操作描述，失败时为错误提示
- `data` (any, required): 返回数据，根据接口不同可能是对象、数组或 null

### 成功响应格式

#### 1. 返回对象数据

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "account": "test",
    "name": "测试用户"
  }
}
```

**使用场景**: 获取单个资源详情、登录返回用户信息等

#### 2. 返回数组数据（列表）

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "list": [
      {
        "id": 1,
        "account": "test1"
      },
      {
        "id": 2,
        "account": "test2"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 20
  }
}
```

**使用场景**: 分页列表接口

**注意**: 
- 列表数据必须包含在 `list` 字段中
- 分页信息包含 `total`（总记录数）、`page`（当前页码）、`pageSize`（每页数量）

#### 3. 返回简单数据

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "user": {
      "id": 1,
      "account": "test"
    }
  }
}
```

**使用场景**: 登录返回用户信息等

#### 4. 无返回数据（操作成功）

```json
{
  "code": 200,
  "message": "操作成功",
  "data": null
}
```

**使用场景**: 新增、修改、删除等操作接口

**注意**: 即使没有返回数据，`data` 字段也必须存在，值为 `null`

### 错误响应格式

所有错误响应统一格式：

```json
{
  "code": 400,
  "message": "错误提示信息",
  "data": null
}
```

**字段说明**:
- `code` (number, required): 错误码，见 [错误码定义](#错误码定义)
- `message` (string, required): 错误提示信息，必须清晰明确，便于前端显示和用户理解
- `data` (null, required): 错误时 `data` 必须为 `null`

### 响应格式示例

#### 示例 1: 登录成功

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "id": 1,
      "account": "Dd12580",
      "userType": "admin",
      "name": "管理员"
    }
  }
}
```

#### 示例 2: 获取列表成功

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "list": [
      {
        "id": 1,
        "account": "member001",
        "balance": 1000.00
      }
    ],
    "total": 50,
    "page": 1,
    "pageSize": 20
  }
}
```

#### 示例 3: 创建成功

```json
{
  "code": 200,
  "message": "新增会员成功",
  "data": null
}
```

#### 示例 4: 参数错误

```json
{
  "code": 400,
  "message": "请求参数错误：账号不能为空",
  "data": null
}
```

#### 示例 5: 未授权

```json
{
  "code": 401,
  "message": "未授权，请重新登录",
  "data": null
}
```

#### 示例 6: 资源不存在

```json
{
  "code": 404,
  "message": "会员不存在",
  "data": null
}
```

### 响应格式规范

1. **HTTP 状态码**: 所有接口统一返回 `200`，不使用 4xx、5xx 等 HTTP 状态码
2. **Content-Type**: 统一为 `application/json;charset=UTF-8`
3. **字段顺序**: 建议按 `code`、`message`、`data` 顺序返回（非强制）
4. **字段类型**: 
   - `code` 必须是数字类型
   - `message` 必须是字符串类型
   - `data` 可以是对象、数组或 null，但不能是 undefined
5. **空值处理**: 
   - 成功但无数据时，`data` 为 `null`，不能省略
   - 错误时，`data` 必须为 `null`
6. **分页响应**: 
   - 列表接口必须包含 `list`、`total`、`page`、`pageSize` 字段
   - `list` 为空数组时返回 `[]`，不能为 `null`
   - `total` 为总记录数，即使 `list` 为空也要返回正确的总数

### 特殊响应格式

#### 报表汇总数据

某些报表接口可能包含汇总统计，格式如下：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "list": [...],
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "summary": {
      "totalAmount": 10000.00,
      "totalCount": 50
    }
  }
}
```

#### 跨页统计

财务报表等接口可能包含跨页统计：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "list": [...],
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "crossPageStats": {
      "depositAmount": 50000.00,
      "withdrawalAmount": 30000.00
    }
  }
}
```

### 响应格式验证

后端开发时，建议：

1. **统一响应封装**: 创建统一的响应封装函数，确保格式一致
2. **类型检查**: 确保 `code` 为数字，`message` 为字符串，`data` 不为 undefined
3. **错误处理**: 所有错误都通过 `code` 和 `message` 返回，`data` 统一为 `null`
4. **测试验证**: 确保所有接口响应格式符合规范

### 响应格式快速参考

| 场景 | code | message | data | 示例接口 |
|------|------|---------|------|---------|
| 成功-返回对象 | 200 | "操作成功" | 对象 | GET /users/members/:account |
| 成功-返回列表 | 200 | "操作成功" | {list, total, page, pageSize} | GET /users/members |
| 成功-无数据 | 200 | "操作成功" | null | POST /users/members |
| 参数错误 | 400 | "错误提示" | null | 所有接口 |
| 未授权 | 401 | "未授权，请重新登录" | null | 需要认证的接口 |
| 无权限 | 403 | "无权限访问" | null | 需要权限的接口 |
| 资源不存在 | 404 | "资源不存在" | null | GET /users/members/:id |
| 服务器错误 | 500 | "服务器内部错误" | null | 所有接口 |

### 响应封装函数示例（参考）

**Python 示例**:

```python
def success_response(data, message='操作成功'):
    return {
        'code': 200,
        'message': message,
        'data': data
    }

def error_response(code, message, data=None):
    return {
        'code': code,
        'message': message,
        'data': data
    }

def paginate_response(list_data, total, page, page_size, message='操作成功'):
    return {
        'code': 200,
        'message': message,
        'data': {
            'list': list_data or [],
            'total': total or 0,
            'page': page or 1,
            'pageSize': page_size or 20
        }
    }
```

### 响应格式检查清单

开发时请确保：

- [ ] HTTP 状态码统一返回 `200`
- [ ] 响应体包含 `code`、`message`、`data` 三个字段
- [ ] `code` 为数字类型，200 表示成功
- [ ] `message` 为字符串类型，不能为空
- [ ] `data` 不能为 `undefined`，无数据时使用 `null`
- [ ] 列表接口包含 `list`、`total`、`page`、`pageSize`
- [ ] 错误响应时 `data` 必须为 `null`
- [ ] 所有字段类型正确，符合 JSON 规范

---

## 错误码定义

| 错误码 | 说明 | HTTP状态码 | 处理建议 |
|--------|------|-----------|---------|
| 200 | 成功 | 200 | - |
| 400 | 请求参数错误 | 200 | 检查请求参数 |
| 401 | 未授权 | 200 | 重新登录 |
| 403 | 无权限访问 | 200 | 检查用户权限 |
| 404 | 资源不存在 | 200 | 检查请求的资源ID |
| 500 | 服务器内部错误 | 200 | 联系技术支持 |
| 1001 | 账号或密码错误 | 200 | 检查登录凭证 |
| 1003 | 账号已被禁用 | 200 | 联系管理员 |
| 1004 | 账号不存在 | 200 | 检查账号是否正确 |
| 2001 | 账号已存在 | 200 | 使用其他账号 |
| 2002 | 密码格式不正确 | 200 | 密码需6-20位字符 |
| 2003 | 余额不足 | 200 | 检查账户余额 |
| 3001 | 数据不存在 | 200 | 检查数据ID |
| 3002 | 数据已被删除 | 200 | 数据已不存在 |

**注意**: 
- 所有接口的 HTTP 状态码统一返回 `200`
- 通过响应体中的 `code` 字段判断请求是否成功
- `code === 200` 表示成功，其他值表示失败

---

## 数据格式规范

### 数据类型

- `string`: 字符串
- `number`: 数字（整数或小数）
- `boolean`: 布尔值（true/false）
- `array`: 数组
- `object`: 对象
- `null`: 空值

### 时间格式

所有时间字段统一使用格式：`YYYY-MM-DD HH:mm:ss`

**示例**:
- `2025-11-10 15:30:00`
- `2025-01-01 00:00:00`

### 日期格式

日期字段（不含时间）使用格式：`YYYY-MM-DD`

**示例**:
- `2025-11-10`
- `2025-01-01`

### 金额格式

所有金额字段使用 `number` 类型，保留 **2位小数**

**示例**:
- `1000.00`
- `0.50`
- `-200.00` (负数表示支出或亏损)

### 账号格式

- 账号为字符串，长度建议 6-20 位
- 支持字母、数字、下划线
- 不区分大小写（建议统一转换为小写存储）

### 密码格式

- 密码长度：6-20 位
- 建议包含字母和数字
- 后端存储时需进行加密（建议使用 bcrypt）

### 盘口格式

盘口值固定为：`A`、`B`、`C`、`D` 四个值之一

### 游戏名称格式

系统仅支持以下两种游戏：
- `新奥六合彩`: 新奥六合彩游戏
- `168澳洲幸运8`: 168澳洲幸运8游戏

所有涉及游戏名称的字段（如 `betType`、`lotteryType`、`game` 等）只能是上述两种游戏之一。

### 用户类型

- `admin`: 管理员
- `agent`: 代理
- `member`: 会员
- `general`: 总代
- `shareholder`: 股东

### 状态值

**账号状态**:
- `正常`: 账号正常
- `冻结`: 账号被冻结
- `禁用`: 账号被禁用

**启用状态**:
- `启用`: 已启用
- `禁用`: 已禁用

**注单状态**:
- `settled`: 已结算
- `unsettled`: 未结算
- `cancelled`: 已取消

**交易状态**:
- `success`: 成功
- `failed`: 失败
- `processing`: 处理中
- `cancelled`: 已取消

---

## 分页说明

### 分页参数

所有列表接口支持分页，通过以下查询参数控制：

- `page` (number, default: 1): 页码，从 1 开始
- `pageSize` (number, default: 20): 每页数量，建议范围 10-100

### 分页响应格式

分页接口返回格式：

```json
{
  "code": 200,
  "data": {
    "list": [
      // 数据列表
    ],
    "total": 100,      // 总记录数
    "page": 1,         // 当前页码
    "pageSize": 20     // 每页数量
  }
}
```

### 分页计算

- 总页数 = `Math.ceil(total / pageSize)`
- 前端根据 `total` 和 `pageSize` 计算总页数

---

## 业务逻辑说明

### 用户层级关系

系统采用 **代理-会员** 的层级结构：

```
管理员 (admin)
  └── 代理 (agent/general/shareholder)
      └── 会员 (member)
```

- 管理员可以管理所有代理和会员
- 代理可以管理自己的下线会员和下级代理
- 会员只能查看自己的信息

### 权限控制

- 根据用户类型和角色控制接口访问权限
- 代理只能查看和管理自己的下线数据

### 数据范围

- 代理查询会员列表时，只能看到自己的下线会员
- 代理查询报表时，只能看到自己及下线的数据
- 管理员可以查看所有数据

### 在线状态

- 在线状态通过 WebSocket 或心跳机制维护
- 建议每 30 秒更新一次在线状态
- 超过 5 分钟无活动视为离线

### 退水计算

- 退水按百分比计算，保留 3 位小数
- 退水金额 = 投注金额 × 退水百分比
- 系统仅支持 "新奥六合彩" 和 "168澳洲幸运8" 两种游戏
- 每种游戏的不同玩法可以设置不同的退水比例

### 报表统计

- 报表数据建议按天统计，支持按日期范围查询
- 报表数据可以异步计算，使用定时任务更新
- 支持重新统计功能，用于数据修正

---

## 接口列表

以下是所有接口的详细说明：

## Auth

### POST /auth/login
登录接口

**说明**: 用户登录认证，成功后返回用户信息

**认证**: 不需要

**Request Body:**
```json
{
  "account": "Dd12580",
  "password": "******"
}
```

**参数验证**:
- `account` (string, required, 6-20位): 账号，必填，长度6-20位
- `password` (string, required, 6-20位): 密码，必填，长度6-20位

**成功响应** (code: 200):
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "id": 1,
      "account": "Dd12580",
      "userType": "admin",
      "name": "管理员"
    }
  }
}
```

**错误响应示例**:

账号或密码错误 (code: 1001):
```json
{
  "code": 1001,
  "message": "账号或密码错误",
  "data": null
}
```

账号已被禁用 (code: 1003):
```json
{
  "code": 1003,
  "message": "账号已被禁用，请联系管理员",
  "data": null
}
```

**字段说明**:
- `user.id` (number): 用户ID，数据库主键
- `user.account` (string): 账号
- `user.userType` (string): 用户类型 (admin/agent/member)
- `user.name` (string): 用户名称/昵称

**业务逻辑**:
1. 验证账号和密码
2. 检查账号状态（是否被禁用）
3. 记录登录日志（IP地址、登录时间等）
4. 返回用户信息

**数据库建议**:
- 密码存储：使用 bcrypt 加密，不存储明文
- 登录日志：记录到 `login_log` 表

### POST /auth/logout
登出接口

**说明**: 用户登出

**认证**: 需要

**Request Body**: 无

**成功响应** (code: 200):
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

**业务逻辑**:
1. 清除服务器端会话（如有）
2. 可选：记录登出日志

**注意**: 登出应始终返回成功，避免前端报错

## Home

### GET /home/online-count
获取当前在线人数

**Response:**
```json
{
  "code": 200,
  "data": {
    "web": 10,
    "app": 5,
    "total": 15
  }
}
```

**Fields:**
- `web` (number): Web端在线人数
- `app` (number): App端在线人数
- `total` (number): 总在线人数

### GET /home/online-trend
获取在线人数趋势数据

**Query Parameters:**
- `date` (string, optional): 日期，格式 YYYY-MM-DD，默认今天

**Response:**
```json
{
  "code": 200,
  "data": {
    "dates": ["00:00", "00:30", "01:00", ...],
    "web": [5, 6, 7, ...],
    "app": [3, 4, 5, ...],
    "total": [8, 10, 12, ...]
  }
}
```

**Fields:**
- `dates` (array): 时间点数组，格式 HH:mm
- `web` (array): Web端各时间点人数
- `app` (array): App端各时间点人数
- `total` (array): 总人数各时间点数据

## Users - Members

### GET /users/members
获取会员列表

**Query Parameters:**
- `page` (number, default: 1): 页码
- `pageSize` (number, default: 20): 每页数量
- `account` (string, optional): 账号查询
- `showOnline` (boolean, optional): 是否只显示在线用户
- `registrationDateStart` (string, optional): 注册开始日期 YYYY-MM-DD
- `registrationDateEnd` (string, optional): 注册结束日期 YYYY-MM-DD
- `plate` (string, optional): 盘口筛选 (A/B/C/D)
- `balanceMin` (number, optional): 余额最小值
- `balanceMax` (number, optional): 余额最大值

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "account": "a2356a",
        "online": false,
        "balance": 0,
        "plate": "B盘",
        "openTime": "2025-06-02 11:28:33",
        "superior": "Dd12580"
      }
    ],
    "total": 4,
    "page": 1,
    "pageSize": 20
  }
}
```

**Fields:**
- `id` (number): 会员ID
- `account` (string): 会员账号
- `online` (boolean): 是否在线
- `balance` (number): 余额
- `plate` (string): 所属盘口
- `openTime` (string): 开户时间
- `superior` (string): 所属上级账号

### POST /users/members
新增会员

**说明**: 创建新的会员账号

**认证**: 需要（代理或管理员）

**Request Body:**
```json
{
  "account": "newmember",
  "password": "******",
  "realName": "真实姓名",
  "affiliatedPlate": "A",
  "companyRemarks": "备注信息"
}
```

**参数验证**:
- `account` (string, required, 6-20位): 账号，必填，唯一，长度6-20位
- `password` (string, required, 6-20位): 密码，必填，长度6-20位
- `realName` (string, optional, max 50位): 真实姓名，可选，最大50位
- `affiliatedPlate` (string, required): 所属盘口，必填，值：A/B/C/D
- `companyRemarks` (string, optional, max 200位): 备注信息，可选，最大200位

**成功响应** (code: 200):
```json
{
  "code": 200,
  "message": "新增会员成功",
  "data": null
}
```

**错误响应示例**:

账号已存在 (code: 2001):
```json
{
  "code": 2001,
  "message": "账号已存在",
  "data": null
}
```

参数错误 (code: 400):
```json
{
  "code": 400,
  "message": "所属盘口格式错误，必须为 A、B、C 或 D",
  "data": null
}
```

**业务逻辑**:
1. 验证账号是否已存在
2. 验证参数格式
3. 密码加密存储
4. 设置上级代理为当前登录用户（代理创建时）
5. 设置默认退水配置（从代理的个人设置中获取）
6. 创建会员记录
7. 初始化账户余额为 0

**权限控制**:
- 代理只能创建自己的下线会员
- 管理员可以创建任意会员（需指定上级代理）

**数据库建议**:
- 账号字段添加唯一索引
- 密码字段使用加密存储
- 记录创建时间、创建人
- 关联上级代理ID

### PUT /users/members/:id
修改会员资料

**Request Body:**
```json
{
  "plate": "B",
  "companyRemarks": "更新备注"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "修改会员成功",
  "data": null
}
```

### GET /users/members/:account
获取会员详情

**Response:**
```json
{
  "code": 200,
  "data": {
    "account": "a2356a",
    "superior": "Dd12580",
    "balance": 0,
    "plate": "B",
    "companyRemarks": "",
    "openTime": "2025-06-02 11:28:33"
  }
}
```

### GET /users/members/:account/login-log
获取会员登录日志

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "loginTime": "2025-06-02 11:28:34",
        "ipAddress": "223.104.76.98",
        "ipLocation": "中国-广州-广东",
        "operator": "移动"
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 20
  }
}
```

### GET /users/members/:account/bet-orders
获取会员注单

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)
- `betTimeStart` (string, optional): 投注开始时间
- `betTimeEnd` (string, optional): 投注结束时间
- `betType` (string, optional): 彩种名称，只能是 "新奥六合彩" 或 "168澳洲幸运8"
- `status` (string, optional): 注单状态 (settled/unsettled/cancelled)
- `orderNo` (string, optional): 注单号
- `ipAddress` (string, optional): IP地址

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "orderNo": "ORD20251110001",
        "betTime": "2025-11-10 15:00:00",
        "settleTime": "2025-11-10 15:09:00",
        "betType": "新奥六合彩",
        "betAccount": "a2356a",
        "betContent": "1-10车号",
        "betAmount": 100.00,
        "rebate": 1.00,
        "betResult": 0.00,
        "status": "settled"
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20,
    "summary": {
      "totalCount": 0,
      "totalAmount": 0,
      "totalResult": 0
    }
  }
}
```

**Fields:**
- `orderNo` (string): 注单号
- `betTime` (string): 投注时间
- `settleTime` (string): 结算时间
- `betType` (string): 投注种类，只能是 "新奥六合彩" 或 "168澳洲幸运8"
- `betAccount` (string): 投注账号
- `betContent` (string): 投注内容
- `betAmount` (number): 下注金额
- `rebate` (number): 退水
- `betResult` (number): 下注结果
- `status` (string): 状态

### GET /users/members/:account/transactions
获取会员交易记录

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)
- `transactionTimeStart` (string, optional): 交易开始时间
- `transactionTimeEnd` (string, optional): 交易结束时间
- `transactionType` (string, optional): 交易类型 (deposit/withdrawal/transfer/recharge/deduction)
- `status` (string, optional): 交易状态 (success/failed/processing/cancelled)

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "transactionTime": "2025-11-10 10:00:00",
        "account": "a2356a",
        "transactionType": "deposit",
        "amount": 1000.00,
        "fee": 0.00,
        "transactionInfo": "USDT ERC20",
        "status": "success",
        "processor": "系统",
        "reviewComments": ""
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20,
    "summary": {
      "totalCount": 0,
      "totalAmount": 0,
      "totalFee": 0
    }
  }
}
```

### GET /users/members/:account/account-changes
获取会员账变记录

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)
- `dateStart` (string, optional): 开始日期
- `dateEnd` (string, optional): 结束日期
- `changeType` (string, optional): 变动类型 (deposit/withdrawal/transfer/recharge/deduction/bet/win/rebate)

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "time": "2025-11-10 10:00:00",
        "changeType": "deposit",
        "balanceBefore": 0.00,
        "changeValue": 1000.00,
        "balanceAfter": 1000.00,
        "operator": "系统"
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

**Fields:**
- `time` (string): 时间
- `changeType` (string): 变动类型
- `balanceBefore` (number): 变动前余额
- `changeValue` (number): 变动数值（正数为增加，负数为减少）
- `balanceAfter` (number): 变动后余额
- `operator` (string): 操作人

## Users - Agents

### GET /users/agents
获取代理列表

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)
- `account` (string, optional): 账号查询
- `registrationDateStart` (string, optional): 开户开始日期
- `registrationDateEnd` (string, optional): 开户结束日期
- `balanceMin` (number, optional): 余额最小值
- `balanceMax` (number, optional): 余额最大值

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "account": "agent001",
        "balance": 1000.00,
        "plate": "A盘,B盘",
        "openTime": "2025-01-01 10:00:00"
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

### POST /users/agents
新增代理

**Request Body:**
```json
{
  "account": "newagent",
  "password": "******",
  "userType": "agent",
  "openPlate": ["A", "B"],
  "earnRebate": "full",
  "subordinateTransfer": "enable",
  "remarks": "备注信息"
}
```

**Fields:**
- `userType` (string): 用户类型 (agent/general/shareholder)
- `openPlate` (array): 开放盘口列表
- `earnRebate` (string): 赚取退水 (full/partial/none)
- `subordinateTransfer` (string): 下级转账 (enable/disable)

**Response:**
```json
{
  "code": 200,
  "message": "新增代理成功",
  "data": null
}
```

### PUT /users/agents/:id
修改代理资料

**Request Body:**
```json
{
  "openPlate": ["A", "B", "C"],
  "earnRebate": "partial",
  "subordinateTransfer": "enable",
  "remarks": "更新备注"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "修改代理成功",
  "data": null
}
```

### GET /users/agents/:account
获取代理详情

**Response:**
```json
{
  "code": 200,
  "data": {
    "account": "agent001",
    "balance": 1000.00,
    "plate": "A盘,B盘",
    "openTime": "2025-01-01 10:00:00",
    "userType": "agent",
    "openPlate": ["A", "B"],
    "earnRebate": "full",
    "subordinateTransfer": "enable"
  }
}
```

### GET /users/agents/:account/login-log
获取代理登录日志

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "loginTime": "2025-06-02 11:28:34",
        "ipAddress": "223.104.76.98",
        "ipLocation": "中国-广州-广东",
        "operator": "移动"
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 20
  }
}
```

### GET /users/agents/:account/members
获取代理的下线会员列表

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)
- `account` (string, optional): 账号查询
- `showOnline` (boolean, optional): 是否只显示在线用户
- `registrationDateStart` (string, optional): 注册开始日期
- `registrationDateEnd` (string, optional): 注册结束日期
- `plate` (string, optional): 盘口筛选
- `balanceMin` (number, optional): 余额最小值
- `balanceMax` (number, optional): 余额最大值

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "account": "member001",
        "online": false,
        "balance": 0,
        "plate": "B盘",
        "openTime": "2025-06-02 11:28:33",
        "superior": "agent001"
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

### GET /users/agents/:account/transactions
获取代理交易记录

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)
- `transactionTimeStart` (string, optional): 交易开始时间
- `transactionTimeEnd` (string, optional): 交易结束时间
- `transactionType` (string, optional): 交易类型
- `status` (string, optional): 交易状态

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "transactionTime": "2025-11-10 10:00:00",
        "account": "agent001",
        "transactionType": "deposit",
        "amount": 1000.00,
        "fee": 0.00,
        "transactionInfo": "USDT ERC20",
        "status": "success",
        "processor": "系统",
        "reviewComments": ""
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20,
    "summary": {
      "totalCount": 0,
      "totalAmount": 0,
      "totalFee": 0
    }
  }
}
```

### GET /users/agents/:account/account-changes
获取代理账变记录

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)
- `dateStart` (string, optional): 开始日期
- `dateEnd` (string, optional): 结束日期
- `changeType` (string, optional): 变动类型

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "time": "2025-11-10 10:00:00",
        "changeType": "deposit",
        "balanceBefore": 0.00,
        "changeValue": 1000.00,
        "balanceAfter": 1000.00,
        "operator": "系统"
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

## Rebate

### GET /users/rebate/:account
获取退水设置

**Response:**
```json
{
  "code": 200,
  "data": {
    "account": "a2356a",
    "independentRebate": false,
    "settings": {
      "earnRebate": 0.00,
      "gameSettings": [
        {
          "game": "新奥六合彩",
          "categories": [
            {
              "type": "1-10车号",
              "bPlate": 0.000,
              "maxRebate": 1
            }
          ]
        }
      ]
    }
  }
}
```

**Fields:**
- `independentRebate` (boolean): 是否使用独立退水设置
- `settings.earnRebate` (number): 赚取退水百分比
- `settings.gameSettings` (array): 游戏设置
  - `game` (string): 游戏名称，只能是 "新奥六合彩" 或 "168澳洲幸运8"
  - `categories` (array): 种类配置
    - `type` (string): 种类名称
    - `bPlate` (number): B盘退水百分比
    - `maxRebate` (number): 最高退水值

### PUT /users/rebate/:account
更新退水设置

**Request Body:**
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
            "bPlate": 0.500
          }
        ]
      }
    ]
  }
}
```

**Response:**
```json
{
  "code": 200,
  "message": "退水设置已更新",
  "data": null
}
```

## Personal

### GET /personal/basic
获取个人基本信息

**Response:**
```json
{
  "code": 200,
  "data": {
    "account": "Dd12580",
    "status": "正常",
    "promotionLink": "https://www.haxi85.vip/?a=932017#/register",
    "inviteCode": "932017",
    "domains": ["baidu.com", "google.com"],
    "defaultRebate": "D",
    "availablePlates": ["A", "B", "C", "D"]
  }
}
```

**Fields:**
- `account` (string): 账号
- `status` (string): 账号状态 (正常/冻结/禁用)
- `promotionLink` (string): 推广链接
- `inviteCode` (string): 邀请码
- `domains` (array): 推广域名列表
- `defaultRebate` (string): 新注册会员默认退水盘口 (A/B/C/D)
- `availablePlates` (array): 可用盘口列表

### PUT /personal/basic
更新个人基本信息

**Request Body:**
```json
{
  "defaultRebate": "D",
  "domains": ["baidu.com", "google.com"]
}
```

**Response:**
```json
{
  "code": 200,
  "message": "基础资料更新成功",
  "data": null
}
```

### POST /personal/promote/domain
添加推广域名

**Request Body:**
```json
{
  "domain": "example.com"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "域名添加成功",
  "data": null
}
```

### GET /personal/lottery-rebate-config
获取彩种退水配置

**Query Parameters:**
- `game` (string, optional): 游戏名称，只能是 "新奥六合彩" 或 "168澳洲幸运8"，不传则返回所有游戏的配置

**Response:**
```json
{
  "code": 200,
  "data": {
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
}
```

**Fields:**
- `games` (array): 游戏列表，固定为 ["新奥六合彩", "168澳洲幸运8"]
- `config` (array): 配置数据
  - `game` (string): 游戏名称，只能是 "新奥六合彩" 或 "168澳洲幸运8"
  - `categories` (array): 种类配置
    - `category` (string): 种类名称
    - `isGroup` (boolean): 是否为分组
    - `level` (number): 层级 (0为分组，1为具体项)
    - `plateA/B/C/D` (number): 各盘退水百分比

### PUT /personal/lottery-rebate-config
保存彩种退水配置

**Request Body:**
```json
{
  "game": "新奥六合彩",
  "config": [
    {
      "category": "1-10车号",
      "plateA": 0.000,
      "plateB": 1.000,
      "plateC": 2.000,
      "plateD": 3.000
    }
  ]
}
```

**参数说明**:
- `game` (string, required): 游戏名称，只能是 "新奥六合彩" 或 "168澳洲幸运8"
- `config` (array, required): 配置数组，包含各玩法的退水设置

**Response:**
```json
{
  "code": 200,
  "message": "退水配置保存成功",
  "data": null
}
```

### GET /personal/login-log
获取登录日志

**Query Parameters:**
- `page` (number, default: 1): 页码
- `pageSize` (number, default: 20): 每页数量
- `dateRange` (array, optional): 日期范围 ["YYYY-MM-DD", "YYYY-MM-DD"]

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "loginTime": "2025-11-10 14:02:11",
        "ip": "103.116.72.4",
        "ipLocation": "中国-香港-香港",
        "operator": "移动"
      }
    ],
    "total": 5,
    "page": 1,
    "pageSize": 20
  }
}
```

**Fields:**
- `id` (number): 日志ID
- `loginTime` (string): 登录时间
- `ip` (string): IP地址
- `ipLocation` (string): IP归属地
- `operator` (string): 运营商

### PUT /personal/password
修改密码

**Request Body:**
```json
{
  "oldPassword": "******",
  "newPassword": "******"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

## Roles & Sub Accounts

### GET /roles
获取角色列表

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 10)
- `roleName` (string, optional): 角色名称搜索

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "roleName": "管理员",
        "roleCode": "admin",
        "description": "系统管理员，拥有所有权限",
        "userCount": 5,
        "status": "启用",
        "createTime": "2025-01-01 10:00:00"
      }
    ],
    "total": 3,
    "page": 1,
    "pageSize": 10
  }
}
```

**Fields:**
- `id` (number): 角色ID
- `roleName` (string): 角色名称
- `roleCode` (string): 角色编码
- `description` (string): 描述
- `userCount` (number): 用户数量
- `status` (string): 状态 (启用/禁用)
- `createTime` (string): 创建时间

### GET /roles/:id
获取角色详情

**Response:**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "roleName": "管理员",
    "roleCode": "admin",
    "remarks": "备注信息",
    "permissions": ["personal-basic-1", "personal-basic-2", ...]
  }
}
```

### POST /roles
新增角色

**Request Body:**
```json
{
  "roleName": "新角色",
  "remarks": "备注信息",
    "permissions": ["personal-basic-1", "personal-basic-2", ...]
}
```

**Response:**
```json
{
  "code": 200,
  "message": "新增角色成功",
  "data": null
}
```

### PUT /roles/:id
更新角色

**Request Body:**
```json
{
  "roleName": "更新角色名",
  "remarks": "更新备注",
  "permissions": ["personal-basic-1", ...]
}
```

**Response:**
```json
{
  "code": 200,
  "message": "更新角色成功",
  "data": null
}
```

### DELETE /roles/:id
删除角色

**Response:**
```json
{
  "code": 200,
  "message": "删除角色成功",
  "data": null
}
```

### GET /roles/permissions
获取权限树

**Response:**
```json
{
  "code": 200,
  "data": {
    "tree": [
      {
        "id": "personal",
        "label": "个人管理",
        "children": [
          {
            "id": "personal-basic",
            "label": "基本资料",
            "children": [
              { "id": "personal-basic-1", "label": "修改代理会员注册默认盘口" },
              { "id": "personal-basic-2", "label": "获取代理个人信息" }
            ]
          }
        ]
      }
    ]
  }
}
```

### GET /roles/sub-accounts
获取子账号列表

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "account": "sub001",
        "name": "子账号1",
        "role": "管理员",
        "createDate": "2025-01-01 10:00:00",
        "status": "启用"
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

**Fields:**
- `id` (number): 子账号ID
- `account` (string): 账号
- `name` (string): 账户名称
- `role` (string): 角色
- `createDate` (string): 新增日期
- `status` (string): 状态 (启用/禁用)

### POST /roles/sub-accounts
新增子账号

**Request Body:**
```json
{
  "agentAccount": "Dd12580",
  "loginPassword": "******",
  "paymentPassword": "******",
  "accountName": "子账号名称",
  "role": "admin"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "新增子账号成功",
  "data": null
}
```

### PUT /roles/sub-accounts/:id
更新子账号

**Request Body:**
```json
{
  "accountName": "更新名称",
  "role": "user",
  "status": "启用"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "更新子账号成功",
  "data": null
}
```

### DELETE /roles/sub-accounts/:id
删除子账号

**Response:**
```json
{
  "code": 200,
  "message": "删除子账号成功",
  "data": null
}
```

## Reports

### GET /reports/financial-summary
财务总报表

**Query Parameters:**
- `dateStart` (string, required): 开始日期 YYYY-MM-DD
- `dateEnd` (string, required): 结束日期 YYYY-MM-DD
- `page` (number, default: 1)
- `pageSize` (number, default: 20)

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "date": "2025-11-10",
        "deposit": 10000.00,
        "withdrawal": 5000.00,
        "bonus": 0.00,
        "irregularBets": 0.00,
        "refundAmount": 0.00,
        "handlingFee": 50.00,
        "depositWithdrawalFee": 30.00,
        "effectiveAmount": 9500.00,
        "memberPL": -2000.00,
        "lotteryTotalPL": -2000.00,
        "platformPL": 0.00,
        "thirdPartyEffectiveAmount": 0.00,
        "thirdPartyTotalPL": 0.00,
        "thirdPartyMemberPL": 0.00,
        "totalPL": -2000.00,
        "memberBalance": 8000.00,
        "agent": "Dd12580"
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 20
  }
}
```

### GET /reports/financial
财务报表

**Query Parameters:**
- `dateStart` (string, required): 开始日期 YYYY-MM-DD
- `dateEnd` (string, required): 结束日期 YYYY-MM-DD
- `userType` (string, optional): 用户类型 (member/agent)
- `page` (number, default: 1)
- `pageSize` (number, default: 20)

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "date": "2025-11-10",
        "depositAmount": 10000.00,
        "withdrawalAmount": 5000.00,
        "bonus": 0.00,
        "irregularBet": 0.00,
        "returnAmount": 0.00,
        "handlingFee": 50.00,
        "depositWithdrawalFee": 30.00
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 20,
    "crossPageStats": {
      "depositAmount": 0,
      "withdrawalAmount": 0,
      "bonus": 0,
      "irregularBet": 0,
      "returnAmount": 0,
      "handlingFee": 0,
      "depositWithdrawalFee": 0
    }
  }
}
```

**Fields:**
- `date` (string): 日期
- `depositAmount` (number): 存款金额
- `withdrawalAmount` (number): 提款金额
- `bonus` (number): 红利
- `irregularBet` (number): 违规投注
- `returnAmount` (number): 返还金额
- `handlingFee` (number): 手续费
- `depositWithdrawalFee` (number): 充提手续费
- `crossPageStats` (object): 跨页统计

### GET /reports/win-loss
输赢报表

**Query Parameters:**
- `dateStart` (string, required): 开始日期 YYYY-MM-DD
- `dateEnd` (string, required): 结束日期 YYYY-MM-DD
- `account` (string, optional): 账号
- `memberProfit` (string, optional): 会员盈利筛选
- `gameTypes` (array, optional): 游戏名称数组，只能是 ["新奥六合彩", "168澳洲幸运8"] 或其子集
- `page` (number, default: 1)
- `pageSize` (number, default: 20)

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "level": 1,
        "account": "member001",
        "name": "会员1",
        "betCount": 10,
        "betAmount": 1000.00,
        "validAmount": 950.00,
        "winLoss": -200.00,
        "rebate": 10.00,
        "profitLossResult": -190.00,
        "receivableDownline": 0.00,
        "share": 0.00,
        "actualShareAmount": 0.00,
        "actualShareWinLoss": 0.00,
        "actualShareRebate": 0.00,
        "earnedRebate": 0.00,
        "profitLoss": 0.00
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

**Fields:**
- `level` (number): 级别
- `account` (string): 账号
- `name` (string): 姓名
- `betCount` (number): 笔数
- `betAmount` (number): 下注金额
- `validAmount` (number): 有效金额
- `winLoss` (number): 输赢
- `rebate` (number): 退水
- `profitLossResult` (number): 盈亏结果
- `receivableDownline` (number): 应收下线
- `share` (number): 占成
- `actualShareAmount` (number): 实占金额
- `actualShareWinLoss` (number): 实占输赢
- `actualShareRebate` (number): 实占退水
- `earnedRebate` (number): 赚水
- `profitLoss` (number): 盈亏

### GET /reports/agent-win-loss
代理输赢报表

**Query Parameters:**
- `dateStart` (string, required): 开始日期 YYYY-MM-DD
- `dateEnd` (string, required): 结束日期 YYYY-MM-DD
- `account` (string, optional): 账号
- `memberProfit` (string, optional): 会员盈利筛选
- `gameTypes` (array, optional): 游戏名称数组，只能是 ["新奥六合彩", "168澳洲幸运8"] 或其子集
- `page` (number, default: 1)
- `pageSize` (number, default: 20)

**Response:**
类似输赢报表结构，字段相同

### GET /reports/deposit-withdrawal
存取款报表

**Query Parameters:**
- `dateStart` (string, required): 开始日期 YYYY-MM-DD
- `dateEnd` (string, required): 结束日期 YYYY-MM-DD
- `userType` (string, optional): 用户类型 (member/agent)
- `page` (number, default: 1)
- `pageSize` (number, default: 20)

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "date": "2025-11-10",
        "depositCount": 10,
        "depositTransactions": 15,
        "depositAmount": 10000.00,
        "withdrawalCount": 5,
        "withdrawalTransactions": 8,
        "withdrawalAmount": 5000.00,
        "handlingFeeNonThirdParty": 50.00,
        "handlingFeeThirdParty": 30.00
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

**Fields:**
- `date` (string): 日期
- `depositCount` (number): 存款人数
- `depositTransactions` (number): 存款笔数
- `depositAmount` (number): 存款金额
- `withdrawalCount` (number): 提款人数
- `withdrawalTransactions` (number): 提款笔数
- `withdrawalAmount` (number): 提款金额
- `handlingFeeNonThirdParty` (number): 非第三方手续费
- `handlingFeeThirdParty` (number): 第三方手续费

### GET /reports/category
分类报表

**Query Parameters:**
- `dateStart` (string, required): 开始日期 YYYY-MM-DD
- `dateEnd` (string, required): 结束日期 YYYY-MM-DD
- `account` (string, optional): 账号
- `gameTypes` (array, optional): 游戏名称数组，只能是 ["新奥六合彩", "168澳洲幸运8"] 或其子集
- `page` (number, default: 1)
- `pageSize` (number, default: 20)

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "lotteryType": "新奥六合彩",
        "gameplay": "1-10车号",
        "betCount": 10,
        "betAmount": 1000.00,
        "validAmount": 950.00,
        "winLoss": -200.00,
        "rebate": 10.00,
        "profitLossResult": -190.00,
        "receivableDownline": 0.00,
        "share": 0.00,
        "actualShareAmount": 0.00,
        "actualShareResult": 0.00,
        "actualShareRebate": 0.00,
        "earnedRebate": 0.00,
        "profitLossResult": 0.00
      }
    ],
    "total": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

**Fields:**
- `lotteryType` (string): 彩种名称，只能是 "新奥六合彩" 或 "168澳洲幸运8"
- `gameplay` (string): 玩法
- `betCount` (number): 笔数
- `betAmount` (number): 下注金额
- `validAmount` (number): 有效金额
- `winLoss` (number): 输赢
- `rebate` (number): 退水
- `profitLossResult` (number): 盈亏结果
- `receivableDownline` (number): 应收下线
- `share` (number): 占成
- `actualShareAmount` (number): 实占金额
- `actualShareResult` (number): 实占结果
- `actualShareRebate` (number): 实占退水
- `earnedRebate` (number): 赚水

### GET /reports/downline-details
下线明细报表

**Query Parameters:**
- `dateStart` (string, required): 开始日期 YYYY-MM-DD
- `dateEnd` (string, required): 结束日期 YYYY-MM-DD
- `account` (string, optional): 账号
- `page` (number, default: 1)
- `pageSize` (number, default: 20)

**Response:**
```json
{
  "code": 200,
  "data": {
    "members": {
      "list": [
        {
          "member": "member001",
          "name": "会员1",
          "deposit": 10000.00,
          "depositCount": 5,
          "withdrawal": 5000.00,
          "withdrawalCount": 3,
          "bonus": 0.00,
          "depositWithdrawalFee": 30.00,
          "validAmount": 9500.00,
          "thirdPartyValidAmount": 0.00,
          "thirdPartyMemberWinLoss": 0.00,
          "memberWinLoss": -2000.00
        }
      ],
      "total": 0,
      "page": 1,
      "pageSize": 20
    },
    "agents": {
      "list": [
        {
          "agent": "agent001",
          "name": "代理1",
          "deposit": 5000.00,
          "depositCount": 3,
          "withdrawal": 2000.00,
          "withdrawalCount": 2,
          "bonus": 0.00,
          "depositWithdrawalFee": 15.00,
          "validAmount": 4500.00,
          "agentWinLoss": -1000.00,
          "thirdPartyValidAmount": 0.00,
          "thirdPartyMemberWinLoss": 0.00
        }
      ],
      "total": 0,
      "page": 1,
      "pageSize": 20
    }
  }
}
```

**Fields:**
- `members` (object): 会员数据
  - `member` (string): 会员账号
  - `name` (string): 姓名
  - `deposit` (number): 存款(元)
  - `depositCount` (number): 存款笔数(笔)
  - `withdrawal` (number): 取款(元)
  - `withdrawalCount` (number): 取款笔数(笔)
  - `bonus` (number): 红利(元)
  - `depositWithdrawalFee` (number): 充提手续费(元)
  - `validAmount` (number): 有效金额(元)
  - `thirdPartyValidAmount` (number): 三方有效金额(元)
  - `thirdPartyMemberWinLoss` (number): 三方会员输赢(元)
  - `memberWinLoss` (number): 会员输赢(元)
- `agents` (object): 代理数据，字段类似会员数据，但包含 `agentWinLoss` (代理输赢)

### POST /reports/financial-summary/recalculate
重新统计财务总报表

**Request Body:**
```json
{
  "dateStart": "2025-11-10",
  "dateEnd": "2025-11-10"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "重新统计成功",
  "data": null
}
```

### GET /reports/export/:type
导出报表

**Path Parameters:**
- `type` (string): 报表类型 (financial-summary/financial/win-loss/agent-win-loss/deposit-withdrawal/category/downline-details)

**Query Parameters:**
- `dateStart` (string, required): 开始日期 YYYY-MM-DD
- `dateEnd` (string, required): 结束日期 YYYY-MM-DD
- 其他筛选参数同对应报表接口

**Response:**
返回 CSV 文件流

## Lottery

### GET /lottery/results
获取开奖结果列表

**Query Parameters:**
- `page` (number, default: 1)
- `pageSize` (number, default: 20)
- `lotteryType` (string, optional): 彩种名称，只能是 "新奥六合彩" 或 "168澳洲幸运8"
- `lotteryDate` (string, optional): 开奖日期 YYYY-MM-DD

**Response:**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "issueNumber": "21270755",
        "lotteryTime": "2025-11-10 15:09:00",
        "lotteryType": "新奥六合彩",
        "numbers": ["3", "4", "6", "2", "9", "5", "10", "7", "1", "8"],
        "championSum": 7,
        "championSize": "小",
        "championParity": "单",
        "dragonTiger1": "虎",
        "dragonTiger2": "龙",
        "dragonTiger3": "虎",
        "dragonTiger4": "虎",
        "dragonTiger5": "龙"
      }
    ],
    "total": 2,
    "page": 1,
    "pageSize": 20
  }
}
```

**Fields:**
- `id` (number): 开奖结果ID
- `issueNumber` (string): 期数
- `lotteryTime` (string): 开奖时间
- `lotteryType` (string): 彩种名称，只能是 "新奥六合彩" 或 "168澳洲幸运8"名称
- `numbers` (array): 开出号码数组
- `championSum` (number): 冠亚军和
- `championSize` (string): 冠亚军和大小 (大/小)
- `championParity` (string): 冠亚军和单双 (单/双)
- `dragonTiger1-5` (string): 1-5龙虎 (龙/虎)

### GET /lottery/results/:id
获取开奖结果详情

**Response:**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "issueNumber": "21270755",
    "lotteryTime": "2025-11-10 15:09:00",
    "lotteryType": "新奥六合彩",
    "numbers": ["3", "4", "6", "2", "9", "5", "10", "7", "1", "8"],
    "championSum": 7,
    "championSize": "小",
    "championParity": "单",
    "dragonTiger1": "虎",
    "dragonTiger2": "龙",
    "dragonTiger3": "虎",
    "dragonTiger4": "虎",
    "dragonTiger5": "龙"
  }
}
```

## Health
### GET /health
健康检查接口

**说明**: 用于检查服务器是否正常运行

**认证**: 不需要

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-10T15:30:00.000Z"
}
```

**字段说明**:
- `status` (string): 状态，固定为 "ok"
- `timestamp` (string): 当前服务器时间戳

---

## 开发注意事项

### 1. 接口开发顺序建议

建议按以下顺序开发接口：

1. **认证模块** (Auth)
   - 先实现登录接口，确保认证逻辑正常
   - 再实现登出接口

2. **基础查询接口**
   - 个人基本信息
   - 会员列表、代理列表
   - 角色列表、权限树

3. **数据操作接口**
   - 新增、修改、删除接口
   - 注意权限控制和数据验证

4. **复杂查询接口**
   - 报表接口（涉及复杂统计）
   - 注单、交易记录等（涉及多表关联）

### 2. 数据库设计建议

#### 核心表结构

**用户表 (users)**
```sql
- id (主键)
- account (账号，唯一索引)
- password (密码，加密存储)
- user_type (用户类型：admin/agent/member)
- superior_id (上级ID，外键)
- balance (余额)
- plate (盘口：A/B/C/D)
- status (状态：正常/冻结/禁用)
- created_at (创建时间)
- updated_at (更新时间)
```

**登录日志表 (login_logs)**
```sql
- id (主键)
- user_id (用户ID，外键)
- login_time (登录时间)
- ip_address (IP地址)
- ip_location (IP归属地)
- operator (运营商)
```

**注单表 (bet_orders)**
```sql
- id (主键)
- order_no (注单号，唯一索引)
- user_id (用户ID，外键)
- bet_time (投注时间)
- settle_time (结算时间)
- bet_type (彩种，只能是 "新奥六合彩" 或 "168澳洲幸运8")
- bet_amount (投注金额)
- rebate (退水)
- bet_result (输赢结果)
- status (状态)
```

**账变记录表 (account_changes)**
```sql
- id (主键)
- user_id (用户ID，外键)
- change_time (变动时间)
- change_type (变动类型)
- balance_before (变动前余额)
- change_value (变动金额)
- balance_after (变动后余额)
- operator (操作人)
```

#### 索引建议

- 账号字段：唯一索引
- 用户ID + 时间字段：联合索引（用于查询日志、记录等）
- 上级ID：索引（用于查询下线）
- 时间字段：索引（用于时间范围查询）

### 3. 性能优化建议

1. **分页查询**
   - 使用 LIMIT 和 OFFSET，避免全表扫描
   - 大数据量时考虑使用游标分页

2. **报表统计**
   - 建议使用定时任务预计算报表数据
   - 使用汇总表存储每日统计数据
   - 支持异步重新统计

3. **缓存策略**
   - 权限树、配置数据可以缓存
   - 在线人数可以缓存，定时更新

4. **数据库优化**
   - 合理使用索引
   - 避免 N+1 查询问题
   - 大数据量查询使用分页

### 4. 安全建议

1. **密码安全**
   - 使用 bcrypt 加密，salt rounds 建议 10+
   - 不存储明文密码
   - 密码重置需要验证

2. **参数验证**
   - 所有输入参数必须验证
   - 防止 SQL 注入（使用参数化查询）
   - 防止 XSS 攻击（对输出进行转义）

3. **权限控制**
   - 每个接口都要验证用户权限
   - 代理只能访问自己的下线数据
   - 敏感操作需要记录操作日志

### 5. 测试建议

1. **单元测试**
   - 测试每个接口的成功和失败场景
   - 测试参数验证
   - 测试权限控制

2. **集成测试**
   - 测试完整的业务流程
   - 测试数据一致性

3. **性能测试**
   - 测试接口响应时间
   - 测试并发访问
   - 测试大数据量查询

### 6. 部署建议

1. **环境配置**
   - 开发环境：使用 mock 数据或测试数据库
   - 生产环境：使用真实数据库，配置备份

2. **日志记录**
   - 记录所有接口请求和响应
   - 记录错误日志
   - 记录操作日志（重要操作）

3. **监控告警**
   - 监控接口响应时间
   - 监控错误率
   - 监控服务器资源使用

### 7. 接口对接

开发完成后，前端需要：

1. **修改 Base URL**
   - 将 `http://localhost:3000/api` 改为实际的后端地址

2. **关闭 Mock 模式**
   - 在 `src/utils/request.js` 中将 `MOCK_MODE` 设置为 `false`

3. **测试接口**
   - 逐个测试所有接口
   - 确保数据格式一致
   - 确保错误处理正确

---

## 附录

### A. 接口清单

**认证模块** (2个)
- POST /auth/login
- POST /auth/logout

**首页模块** (2个)
- GET /home/online-count
- GET /home/online-trend

**用户管理 - 会员** (8个)
- GET /users/members
- POST /users/members
- PUT /users/members/:id
- GET /users/members/:account
- GET /users/members/:account/login-log
- GET /users/members/:account/bet-orders
- GET /users/members/:account/transactions
- GET /users/members/:account/account-changes

**用户管理 - 代理** (8个)
- GET /users/agents
- POST /users/agents
- PUT /users/agents/:id
- GET /users/agents/:account
- GET /users/agents/:account/login-log
- GET /users/agents/:account/members
- GET /users/agents/:account/transactions
- GET /users/agents/:account/account-changes

**退水设置** (2个)
- GET /users/rebate/:account
- PUT /users/rebate/:account

**个人中心** (7个)
- GET /personal/basic
- PUT /personal/basic
- POST /personal/promote/domain
- GET /personal/lottery-rebate-config
- PUT /personal/lottery-rebate-config
- GET /personal/login-log
- PUT /personal/password

**角色权限** (10个)
- GET /roles
- GET /roles/:id
- POST /roles
- PUT /roles/:id
- DELETE /roles/:id
- GET /roles/permissions
- GET /roles/sub-accounts
- POST /roles/sub-accounts
- PUT /roles/sub-accounts/:id
- DELETE /roles/sub-accounts/:id

**报表模块** (9个)
- GET /reports/financial-summary
- POST /reports/financial-summary/recalculate
- GET /reports/financial
- GET /reports/win-loss
- GET /reports/agent-win-loss
- GET /reports/deposit-withdrawal
- GET /reports/category
- GET /reports/downline-details
- GET /reports/export/:type

**开奖结果** (2个)
- GET /lottery/results
- GET /lottery/results/:id

**健康检查** (1个)
- GET /health

**总计**: 51 个接口

### B. 联系方式

如有疑问，请联系前端开发团队。

---

**文档版本**: v1.0  
**最后更新**: 2025-01-XX  
**维护者**: 前端开发团队


