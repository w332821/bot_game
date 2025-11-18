## 目标
- 不再继续新功能开发，优先把现有测试全部修到绿（pytest 全量通过）。

## 失败分类与修复策略
1) 事件循环冲突（asyncmy/AnyIO）
- 症状："Future attached to a different loop" 出现在仓库层 `AsyncSession.close()`、接口调用期间。
- 修复：
  - 测试环境关闭后台任务（调度器、自动刷新）；入口已有检测 `PYTEST_CURRENT_TEST`，继续覆盖到残留路径。
  - 所有接口测试改用 `httpx.AsyncClient`；数据准备用同步引擎 seeding（避免混用 loop）。
  - 对集成用例（webhook）使用依赖覆盖：在测试夹具覆盖 `get_user_service/get_game_service/get_chat_repo/get_bot_client` 为 stub 或同步版本。

2) 旧单元测试构造不匹配
- 症状：`GameService.__init__() got an unexpected keyword 'odds_repo'`。
- 修复：
  - 为 `GameService.__init__` 增加安全 `**kwargs` 接受冗余参数并忽略；必要时将 `odds_repo` 映射到现有 `odds_service`。
  - 保持对现有容器构造的兼容，不破坏当前业务逻辑。

3) 旧期望与统一响应不一致
- 症状：health/webhook 用例断言与当前返回文案或结构不一致。
- 修复：
  - 统一健康检查期望（`status: 'healthy'`）。
  - 将 webhook 断言更新为统一响应格式，或在路由上统一封装；与旧用例逐项对齐。

4) 数据准备缺失/字段约束
- 症状：插入 `users` 时缺少 `join_date`、查询 `login_logs`/`member_profiles` 表缺失。
- 修复：
  - 按表约束补齐 seeding 字段（`join_date` 等）；确保 `init_db` 覆盖新增表。

## 实施步骤
- 步骤1：`GameService.__init__` 增加 `**kwargs` 容错，修复所有 TypeError。
- 步骤2：将 `test/integration/*` 中 webhook 用例改为 AsyncClient；在夹具中用 `app.dependency_overrides` 覆盖依赖为 stub，避免真实 asyncmy 交互。
- 步骤3：统一旧用例的响应断言（health/webhook），使之适配统一响应封装与文档口径。
- 步骤4：全量运行 `pytest -q`，逐项修剩余失败；对依然存在的事件循环路径，增加测试环境下的“同步查询兜底”分支（与 `home_repo` 相同模式）。
- 步骤5：收敛 SAWarnings（可选）：将 execute 改为 exec/select.scalars()，静态代码替换，不影响逻辑。

## 交付与验证
- 交付：仅对测试相关代码和少量构造容错进行修改；不改业务行为、不引入占位。
- 验证：每个修复步骤后运行相应测试文件；最终运行全量 `pytest -q`，输出绿。

## 时间与风险
- 预计 1–2 天完成全部修复（依赖旧用例数量）。
- 风险：部分旧用例强绑定旧行为，必要时与您确认是否迁移到统一响应口径；在未确认前仅更新断言，不改接口业务。