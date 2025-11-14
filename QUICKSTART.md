# 快速开始指南

这是一个 5 分钟快速开始指南，帮助你快速上手这个 FastAPI 项目模板。

## 第一步：安装依赖

```bash
pip install -r requirements.txt
```

## 第二步：配置数据库

```bash
# 复制配置文件模板
cp config.example.yaml config.yaml

# 编辑 config.yaml，修改数据库连接信息
# 你需要修改：用户名、密码、主机地址、数据库名
```

示例配置：
```yaml
db:
  database_uri: "mysql+asyncmy://root:password@localhost:3306/mydb"
  sync_database_uri: "mysql+pymysql://root:password@localhost:3306/mydb"
  echo: False
```

## 第三步：初始化数据库

```bash
# 确保你的 MySQL 数据库已启动，并且数据库已创建
python -m base.init_db
```

## 第四步：启动应用

```bash
# 开发模式（带热重载）
python biz/application.py
```

应用将在 http://localhost:8000 启动

## 第五步：测试 API

访问 http://localhost:8000/docs 查看自动生成的 API 文档

测试健康检查端点：
```bash
curl http://localhost:8000/health
```

## 创建你的第一个模块

```bash
# 创建一个 user 模块
python scripts/create_module.py user
```

脚本会自动生成完整的模块结构，然后按照控制台输出的提示完成以下步骤：

### 1. 注册依赖（在 `biz/containers.py` 中）

在文件末尾添加：
```python
from biz.user.repo.user_repo import UserRepository
from biz.user.service.user_service import UserService

user_repo = providers.Factory(UserRepository, session_factory=db_session_factory)
user_service = providers.Factory(UserService, user_repo=user_repo)
```

### 2. 注册路由（在 `biz/application.py` 中）

在导入区域添加：
```python
from biz.user.api.user_api import user_api
```

在路由注册区域添加：
```python
app.include_router(user_api, prefix=api_prefix)
```

### 3. Wire 模块（在 `biz/application.py` 中）

修改 `container.wire()` 调用：
```python
container.wire(modules=[
    "biz.user.api.user_api",
])
```

### 4. 初始化数据库表

```bash
python -m base.init_db
```

### 5. 重启应用并测试

```bash
python biz/application.py
```

访问 http://localhost:8000/docs，你会看到 user 模块的所有 API 端点！

## 项目结构说明

```
base_project/
├── base/                      # 基础设施层（不要修改）
│   ├── model.py              # 所有模型的基类
│   ├── repo.py               # Repository 基类
│   ├── api.py                # 统一响应格式
│   ├── exception.py          # 异常处理
│   └── middleware/           # 中间件（日志、请求追踪等）
├── biz/                       # 业务逻辑层（在这里开发）
│   ├── application.py        # 应用入口
│   ├── containers.py         # 依赖注入配置
│   └── [你的模块]/           # 你的业务模块
├── scripts/                   # 工具脚本
│   └── create_module.py      # 创建新模块
└── config.yaml               # 配置文件（不要提交到 git）
```

## 开发工作流

1. 使用 `python scripts/create_module.py <模块名>` 创建新模块
2. 在 `models/model.py` 中定义数据模型
3. 在 `service/` 中实现业务逻辑
4. 在 `api/` 中定义 API 端点
5. 在 `containers.py` 和 `application.py` 中注册模块
6. 运行 `python -m base.init_db` 创建数据库表
7. 在 `/docs` 中测试你的 API

## 下一步

- 阅读 [README.md](README.md) 了解详细功能
- 阅读 [CLAUDE.md](CLAUDE.md) 了解架构设计
- 查看生成的模块代码了解最佳实践

## 常见问题

**Q: 如何修改端口？**
A: 在 `biz/application.py` 的 `uvicorn.run()` 中修改 `port` 参数

**Q: 如何添加 CORS 白名单？**
A: 在 `biz/application.py` 中修改 `CORSMiddleware` 的 `allow_origins` 参数

**Q: 如何查看 SQL 语句？**
A: 在 `config.yaml` 中设置 `echo: True`

**Q: 数据库连接失败怎么办？**
A: 检查：
1. MySQL 是否已启动
2. 数据库是否已创建
3. 用户名密码是否正确
4. 主机地址和端口是否正确

祝你开发愉快！🚀
