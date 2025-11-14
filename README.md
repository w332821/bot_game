# Game Bot - 悦聊游戏机器人

基于 FastAPI 的游戏机器人系统，支持澳洲幸运8和新澳游戏。

## 🎮 项目简介

这是一个完整的游戏机器人系统，通过悦聊Bot API接入群聊，提供自动化的游戏服务。

### 主要功能

- 🎲 **双游戏支持** - 澳洲幸运8（5分钟/局）+ 新澳（24小时/局）
- 💰 **下注系统** - 支持9种玩法（番、正、单双、号码等）
- ⏰ **自动开奖** - 定时调度，自动结算
- 👥 **用户管理** - 余额、排行榜、历史记录
- 📊 **数据统计** - 投注流水、开奖历史
- 🖼️ **图片生成** - 自动生成开奖历史图片

## 🚀 快速开始

### 1. 环境要求

- Python 3.11+
- MySQL 5.7+
- Conda（推荐）

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
conda create -n bot_game python=3.11
conda activate bot_game

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

#### 数据库配置 (`config.yaml`)

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml`:
```yaml
db:
  database_uri: "mysql+asyncmy://user:password@localhost:3306/game_bot"
  sync_database_uri: "mysql+pymysql://user:password@localhost:3306/game_bot"
  echo: false
```

#### Bot API 配置 (`.env`)

```bash
cp .env.example .env
```

编辑 `.env`:
```bash
# Bot API 配置
BOT_API_BASE=http://127.0.0.1:65035
BOT_API_KEY=your_bot_api_key
BOT_API_SECRET=your_bot_api_secret

# 开奖 API（可选，有默认值）
LUCKY8_API_BASE=https://api.api168168.com
LIUHECAI_API_BASE=https://history.macaumarksix.com
```

### 4. 初始化数据库

```bash
python -m base.init_db
```

### 5. 启动服务

```bash
# 使用启动脚本（推荐）
./start.sh

# 或手动启动
python biz/application.py
```

服务启动在 **http://localhost:3003**

### 6. 访问文档

- API 文档: http://localhost:3003/docs
- 健康检查: http://localhost:3003/health

## 📚 项目结构

```
bot_game/
├── base/                    # 基础设施层
│   ├── model.py            # 基础模型（UUID、时间戳、软删除）
│   ├── repo.py             # 通用 Repository
│   ├── api.py              # 统一响应格式
│   └── middleware/         # 中间件（日志、异常、请求ID）
│
├── biz/                     # 业务逻辑层
│   ├── application.py      # FastAPI 应用入口
│   ├── containers.py       # 依赖注入容器
│   │
│   ├── game/               # 🎮 游戏模块（核心）
│   │   ├── service/        # 游戏业务逻辑
│   │   ├── scheduler/      # 自动开奖调度器
│   │   ├── logic/          # 游戏规则引擎
│   │   └── webhook/        # Webhook 事件处理
│   │
│   ├── user/               # 👤 用户模块
│   ├── bet/                # 💵 下注模块
│   ├── chat/               # 💬 群聊模块
│   ├── draw/               # 🎰 开奖模块
│   ├── odds/               # 📊 赔率模块
│   └── admin/              # 🛠️ 管理模块
│
├── external/                # 外部服务集成
│   ├── bot_api_client.py   # 悦聊 Bot API 客户端
│   └── draw_api_client.py  # 开奖 API 客户端
│
├── utils/                   # 工具类
│   └── draw_image_generator.py  # 图片生成器
│
└── docs/                    # 📖 文档
    ├── APP_ENDPOINTS.md            # API 端点详细文档
    ├── WEBHOOK_SPEC.md             # Webhook 规范
    └── REAL_API_INTEGRATION.md     # 开奖 API 集成说明
```

## 🎯 支持的游戏和玩法

### 澳洲幸运8

| 玩法 | 示例 | 赔率 | 说明 |
|-----|------|-----|------|
| 番 | `番 3/200` | 3倍 | 单号投注 |
| 正 | `正1/200` | 2倍 | 对立号投注 |
| 单/双 | `单200` | 2倍 | 奇偶投注 |

### 新澳

| 玩法 | 示例 | 赔率 | 说明 |
|-----|------|-----|------|
| 号码 | `1/200` | 40倍 | 单号投注（1-49） |
| 大/小 | `大200` | 2倍 | 大小投注 |
| 单/双 | `单200` | 2倍 | 奇偶投注 |
| 波色 | `红波200` | 3倍 | 波色投注 |

## 🤖 消息指令

在群聊中发送以下指令：

| 指令 | 功能 | 示例 |
|-----|------|------|
| 下注指令 | 下注 | `番 3/200` `单200` |
| `查` / `余额` | 查询余额 | `查` |
| `排行` / `排行榜` | 查看排行榜 | `排行` |
| `流水` / `历史` | 投注历史 | `流水` |
| `取消` | 取消当前期投注 | `取消` |
| `开奖` | 手动触发开奖 | `开奖` |
| `开奖历史` | 查看历史开奖 | `开奖历史` |

## 🔧 技术栈

- **Web 框架**: FastAPI + Uvicorn
- **数据库**: MySQL + SQLModel (异步 ORM)
- **依赖注入**: dependency-injector
- **图片处理**: Pillow (PIL)
- **HTTP 客户端**: aiohttp
- **任务调度**: asyncio
- **日志**: Python logging

## 📖 文档

| 文档 | 说明 |
|-----|------|
| [QUICKSTART.md](./QUICKSTART.md) | 快速开始指南 |
| [SETUP_GUIDE.md](./SETUP_GUIDE.md) | 详细安装配置 |
| [CLAUDE.md](./CLAUDE.md) | AI 项目说明（给 Claude Code 看的） |
| [docs/APP_ENDPOINTS.md](./docs/APP_ENDPOINTS.md) | API 端点详细文档 |
| [docs/WEBHOOK_SPEC.md](./docs/WEBHOOK_SPEC.md) | Webhook 事件规范 |
| [docs/REAL_API_INTEGRATION.md](./docs/REAL_API_INTEGRATION.md) | 真实开奖 API 集成 |

## 🏗️ 架构特点

### 分层架构
- **API 层**: HTTP 请求处理、参数验证
- **Service 层**: 业务逻辑、事务管理
- **Repository 层**: 数据访问、数据库操作

### 核心特性
- ✅ 依赖注入 - 易于测试和扩展
- ✅ 异步 I/O - 高性能并发处理
- ✅ 软删除 - 数据安全保护
- ✅ 统一响应 - 标准化 API 格式
- ✅ 异常处理 - 全局错误捕获
- ✅ 请求追踪 - Request ID 中间件
- ✅ 日志记录 - 完整的请求日志

## 🚢 部署

### 开发环境

```bash
python biz/application.py
```

### 生产环境

```bash
# 使用 Uvicorn（推荐）
uvicorn biz.application:app \
  --host 0.0.0.0 \
  --port 3003 \
  --workers 4

# 或使用 Gunicorn
gunicorn biz.application:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:3003
```

## 🔍 与 Node.js 版本对比

| 特性 | Node.js | Python FastAPI |
|-----|---------|----------------|
| **架构** | 单体架构 | 分层架构 |
| **数据存储** | JSON 文件 | MySQL 数据库 |
| **并发模型** | 事件循环 | 异步协程 |
| **扩展性** | 较难 | 易扩展 |
| **测试性** | 一般 | 优秀（依赖注入） |
| **功能完整性** | ✅ 100% | ✅ 100%（完全兼容） |

**推荐使用 Python 版本**，原因：
1. 更好的架构设计
2. 数据库支持更强大的查询和统计
3. 依赖注入使代码更易测试
4. 更容易扩展新功能

## 🛠️ 开发指南

### 添加新模块

使用代码生成脚本：

```bash
python scripts/create_module.py <module_name>
```

### 自定义查询

在 Repository 中添加方法：

```python
async def get_by_chat_id(self, chat_id: str):
    async with self._session_factory() as session:
        result = await session.exec(
            select(self._model).where(
                self._model.chat_id == chat_id,
                self._model.deleted == False
            )
        )
        return result.all()
```

### 添加业务逻辑

在 Service 层实现：

```python
async def process_bet(self, bet_data: dict):
    # 1. 验证
    # 2. 扣款
    # 3. 保存
    # 4. 通知
    pass
```

## 📝 待办事项

- [ ] 开发 Admin Web 界面（Vue/React）
- [ ] 添加更多游戏类型
- [ ] 优化图片生成性能
- [ ] 添加 Redis 缓存
- [ ] 完善测试覆盖率
- [ ] 添加监控和告警

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

---

**最后更新**: 2025-11-13
**版本**: 2.0.0 (Python FastAPI)
