# 后台管理系统 API 对接文档

## 一、系统架构说明

### 账号类型
系统支持三种账号类型：

| 账号类型 | 说明 | 登录接口 | 密码存储位置 |
|---------|------|---------|-------------|
| **管理员** | 超级管理员/分销商 | `/api/auth/login` | `admin_accounts` 表 |
| **代理** | 代理账号 | `/api/auth/login` | `agent_profiles` 表 |
| **会员** | 会员账号 | `/api/auth/login` | `member_profiles` 表 |

### 数据库表关系
```
users 表（通用账户）
├── 存储余额、积分等财务数据
└── 所有账号类型共享

agent_profiles（代理扩展）
├── 关联 users 表获取余额
└── 存储密码和代理配置

member_profiles（会员扩展）
├── 关联 users 表获取余额
└── 存储密码和会员配置
```

---

## 二、API 接口

### 1. 登录接口

**接口地址**：`POST /api/auth/login`

**功能**：统一登录接口，支持管理员/代理/会员

**请求参数**：
```json
{
  "account": "admin",     // 账号（管理员username / 代理account / 会员account）
  "password": "123456"    // 密码
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "id": "admin_1234567890",
      "account": "admin",
      "userType": "super_admin"  // super_admin | distributor | agent | member
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**userType 说明**：
- `super_admin`: 超级管理员
- `distributor`: 分销商
- `agent`: 代理
- `member`: 会员

---

### 2. 修改密码接口

**接口地址**：`PUT /api/personal/password`

**功能**：修改当前登录用户的密码

**请求头**：
```
Authorization: Bearer <token>
```

**请求参数**：
```json
{
  "oldPassword": "123456",    // 旧密码
  "newPassword": "newpass"    // 新密码（6-20位）
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "success": true
  }
}
```

**错误响应**：
```json
{
  "code": 40001,
  "message": "旧密码错误",
  "data": null
}
```

---

### 3. 创建代理

**接口地址**：`POST /api/users/agents`

**请求头**：
```
Authorization: Bearer <admin_token>
```

**请求参数**：
```json
{
  "account": "agent001",           // 代理账号
  "password": "123456",            // 登录密码
  "plate": "B",                    // 主盘口 A/B/C
  "openPlate": ["A", "B", "C"],    // 开放盘口
  "earnRebate": "partial",         // 赚取退水: full/partial/none
  "subordinateTransfer": "enable", // 下级转账: enable/disable
  "defaultRebatePlate": "A",       // 新会员默认退水盘口
  "superiorAccount": "admin",      // 上级账号（可选）
  "companyRemarks": "备注"          // 公司备注（可选）
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "account": "agent001"
  }
}
```

---

### 4. 创建会员

**接口地址**：`POST /api/users/members`

**请求头**：
```
Authorization: Bearer <admin_token>
```

**请求参数**：
```json
{
  "account": "member001",      // 会员账号
  "password": "123456",        // 登录密码
  "plate": "B",                // 盘口 A/B/C
  "superiorAccount": "agent001", // 上级账号（可选）
  "companyRemarks": "备注"      // 公司备注（可选）
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "account": "member001"
  }
}
```

---

## 三、前端开发指南

### 1. 登录流程

```javascript
// 1. 调用登录接口
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    account: 'admin',
    password: '123456'
  })
});

const result = await loginResponse.json();

// 2. 保存 token 到 localStorage
if (result.code === 200) {
  localStorage.setItem('token', result.data.token);
  localStorage.setItem('userType', result.data.user.userType);
  localStorage.setItem('account', result.data.user.account);

  // 跳转到主页
  window.location.href = '/dashboard';
}
```

### 2. 携带 Token 请求

```javascript
// 所有需要认证的请求都要带上 token
const response = await fetch('/api/personal/password', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  },
  body: JSON.stringify({
    oldPassword: '123456',
    newPassword: 'newpass'
  })
});
```

### 3. 修改密码流程

```javascript
async function changePassword(oldPassword, newPassword) {
  const response = await fetch('/api/personal/password', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({
      oldPassword,
      newPassword
    })
  });

  const result = await response.json();

  if (result.code === 200) {
    alert('密码修改成功，请重新登录');
    // 清除 token，跳转到登录页
    localStorage.clear();
    window.location.href = '/login';
  } else {
    alert(result.message);
  }
}
```

### 4. Token 过期处理

```javascript
// 封装请求方法
async function apiRequest(url, options = {}) {
  const token = localStorage.getItem('token');

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers
    }
  });

  // Token 过期，返回 401
  if (response.status === 401) {
    alert('登录已过期，请重新登录');
    localStorage.clear();
    window.location.href = '/login';
    return;
  }

  return response.json();
}
```

---

## 四、错误码说明

| 错误码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或登录已过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 40001 | 账号或密码错误 |
| 40002 | 旧密码错误 |
| 500 | 服务器内部错误 |

---

## 五、注意事项

### 1. 密码安全
- 新密码长度：6-20 位
- 密码采用 bcrypt 加密存储
- 修改密码需要验证旧密码

### 2. Token 管理
- Token 有效期：默认 24 小时
- Token 过期需要重新登录
- 建议在 localStorage 中存储 token

### 3. 权限控制
- 修改密码接口：所有登录用户都可以修改自己的密码
- 创建代理/会员：只有管理员权限才能操作

### 4. 账号规则
- 代理账号和会员账号独立，可以重名
- 每个账号都会关联到 users 表，获取余额等数据
- 代理/会员登录后的 chat_id 为 "admin_backend"

---

## 六、测试账号

| 类型 | 账号 | 密码 | 说明 |
|-----|------|------|------|
| 管理员 | admin | admin123 | 超级管理员 |

> 注意：创建代理和会员账号需要使用管理员 token

---

## 七、联系方式

如有问题，请联系后端开发团队。
