#!/usr/bin/env python3
"""
创建新的业务模块脚本

使用方法:
    python scripts/create_module.py <module_name>

示例:
    python scripts/create_module.py user
"""

import os
import sys
from pathlib import Path


def create_module(module_name: str):
    """创建新的业务模块目录结构和基础文件"""

    # 确定项目根目录
    project_root = Path(__file__).parent.parent
    module_path = project_root / "biz" / module_name

    if module_path.exists():
        print(f"错误: 模块 '{module_name}' 已存在！")
        sys.exit(1)

    # 创建目录结构
    directories = [
        module_path,
        module_path / "models",
        module_path / "repo",
        module_path / "service",
        module_path / "api",
        module_path / "exception",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"创建目录: {directory}")

    # 模块名的大驼峰形式
    class_name = ''.join(word.capitalize() for word in module_name.split('_'))

    # 创建 __init__.py 文件
    init_files = [
        module_path / "__init__.py",
        module_path / "models" / "__init__.py",
        module_path / "repo" / "__init__.py",
        module_path / "service" / "__init__.py",
        module_path / "api" / "__init__.py",
        module_path / "exception" / "__init__.py",
    ]

    for init_file in init_files:
        init_file.touch()
        print(f"创建文件: {init_file}")

    # 创建 models/model.py
    model_content = f'''from sqlmodel import SQLModel, Field
from base.model import ModelBase


class {class_name}(ModelBase, table=True):
    """
    {class_name} 实体模型
    """
    __tablename__ = "{module_name}"

    name: str = Field(description="名称")
    # 添加更多字段...


class {class_name}Create(SQLModel):
    """创建 {class_name} 的请求模型"""
    name: str


class {class_name}Update(SQLModel):
    """更新 {class_name} 的请求模型"""
    name: str | None = None
'''

    (module_path / "models" / "model.py").write_text(model_content, encoding='utf-8')
    print(f"创建文件: {module_path / 'models' / 'model.py'}")

    # 创建 models/schema.py
    schema_content = f'''from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class {class_name}Response(BaseModel):
    """单个 {class_name} 的响应模型"""
    id: UUID
    name: str
    create_time: datetime
    modify_time: datetime

    class Config:
        from_attributes = True


class {class_name}ListResponse(BaseModel):
    """{class_name} 列表的响应模型"""
    total: int
    items: list[{class_name}Response]
'''

    (module_path / "models" / "schema.py").write_text(schema_content, encoding='utf-8')
    print(f"创建文件: {module_path / 'models' / 'schema.py'}")

    # 创建 repo
    repo_content = f'''from base.repo import BaseRepository
from biz.{module_name}.models.model import {class_name}, {class_name}Create, {class_name}Update


class {class_name}Repository(BaseRepository[{class_name}, {class_name}Create, {class_name}Update]):
    """
    {class_name} 数据访问层

    继承自 BaseRepository，提供基础的 CRUD 操作
    可以在这里添加自定义的查询方法
    """
    pass
'''

    (module_path / "repo" / f"{module_name}_repo.py").write_text(repo_content, encoding='utf-8')
    print(f"创建文件: {module_path / 'repo' / f'{module_name}_repo.py'}")

    # 创建 service
    service_content = f'''from biz.{module_name}.repo.{module_name}_repo import {class_name}Repository
from biz.{module_name}.models.model import {class_name}Create, {class_name}Update
from uuid import UUID


class {class_name}Service:
    """
    {class_name} 业务逻辑层
    """

    def __init__(self, {module_name}_repo: {class_name}Repository):
        self.{module_name}_repo = {module_name}_repo

    async def create_{module_name}(self, {module_name}_create: {class_name}Create):
        """创建 {class_name}"""
        return await self.{module_name}_repo.create({module_name}_create)

    async def get_{module_name}(self, {module_name}_id: UUID):
        """根据 ID 获取 {class_name}"""
        return await self.{module_name}_repo.get_by_id({module_name}_id)

    async def update_{module_name}(self, {module_name}_id: UUID, {module_name}_update: {class_name}Update):
        """更新 {class_name}"""
        return await self.{module_name}_repo.update({module_name}_id, {module_name}_update)

    async def delete_{module_name}(self, {module_name}_id: UUID):
        """删除 {class_name} (软删除)"""
        await self.{module_name}_repo.delete({module_name}_id)

    async def list_{module_name}s(self, offset: int = 0, limit: int = 10):
        """获取 {class_name} 列表"""
        return await self.{module_name}_repo.list(offset=offset, limit=limit)
'''

    (module_path / "service" / f"{module_name}_service.py").write_text(service_content, encoding='utf-8')
    print(f"创建文件: {module_path / 'service' / f'{module_name}_service.py'}")

    # 创建 api
    api_content = f'''from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from uuid import UUID

from biz.containers import Container
from biz.{module_name}.service.{module_name}_service import {class_name}Service
from biz.{module_name}.models.model import {class_name}Create, {class_name}Update
from biz.{module_name}.models.schema import {class_name}Response, {class_name}ListResponse
from base.api import UnifyResponse

{module_name}_api = APIRouter(
    prefix="/v1/{module_name}",
    tags=["{module_name}"],
)


@{module_name}_api.post("/create", response_model={class_name}Response, response_class=UnifyResponse)
@inject
async def create_{module_name}(
    {module_name}_create: {class_name}Create,
    {module_name}_service: {class_name}Service = Depends(Provide[Container.{module_name}_service])
):
    """创建 {class_name}"""
    return await {module_name}_service.create_{module_name}({module_name}_create)


@{module_name}_api.get("/{{0}}", response_model={class_name}Response, response_class=UnifyResponse)
@inject
async def get_{module_name}(
    {module_name}_id: UUID,
    {module_name}_service: {class_name}Service = Depends(Provide[Container.{module_name}_service])
):
    """根据 ID 获取 {class_name}"""
    return await {module_name}_service.get_{module_name}({module_name}_id)


@{module_name}_api.put("/{{0}}", response_model={class_name}Response, response_class=UnifyResponse)
@inject
async def update_{module_name}(
    {module_name}_id: UUID,
    {module_name}_update: {class_name}Update,
    {module_name}_service: {class_name}Service = Depends(Provide[Container.{module_name}_service])
):
    """更新 {class_name}"""
    return await {module_name}_service.update_{module_name}({module_name}_id, {module_name}_update)


@{module_name}_api.delete("/{{0}}", response_class=UnifyResponse)
@inject
async def delete_{module_name}(
    {module_name}_id: UUID,
    {module_name}_service: {class_name}Service = Depends(Provide[Container.{module_name}_service])
):
    """删除 {class_name}"""
    await {module_name}_service.delete_{module_name}({module_name}_id)
    return {{"message": "删除成功"}}


@{module_name}_api.get("/list", response_model={class_name}ListResponse, response_class=UnifyResponse)
@inject
async def list_{module_name}s(
    offset: int = 0,
    limit: int = 10,
    {module_name}_service: {class_name}Service = Depends(Provide[Container.{module_name}_service])
):
    """获取 {class_name} 列表"""
    items, total = await {module_name}_service.list_{module_name}s(offset=offset, limit=limit)
    return {{"items": items, "total": total}}
'''

    # 修复路径参数的格式
    api_content = api_content.replace("{0}", f"{{{module_name}_id}}")

    (module_path / "api" / f"{module_name}_api.py").write_text(api_content, encoding='utf-8')
    print(f"创建文件: {module_path / 'api' / f'{module_name}_api.py'}")

    # 创建 exception
    exception_content = f'''from enum import IntEnum
from fastapi import status
from base.exception import UnifyException


class {class_name}ExceptionCode(IntEnum):
    """{class_name} 业务异常代码"""
    {class_name}NotFound = 200001
    {class_name}AlreadyExists = 200002


# 定义具体的异常实例
{class_name}NotFound = UnifyException(
    detail="{module_name} not found",
    biz_code={class_name}ExceptionCode.{class_name}NotFound,
    http_code=status.HTTP_404_NOT_FOUND
)

{class_name}AlreadyExists = UnifyException(
    detail="{module_name} already exists",
    biz_code={class_name}ExceptionCode.{class_name}AlreadyExists,
    http_code=status.HTTP_409_CONFLICT
)
'''

    (module_path / "exception" / "exception.py").write_text(exception_content, encoding='utf-8')
    print(f"创建文件: {module_path / 'exception' / 'exception.py'}")

    # 打印后续步骤说明
    print(f"\n✅ 模块 '{module_name}' 创建成功！\n")
    print("接下来需要手动完成以下步骤：\n")
    print("1. 在 biz/containers.py 中注册依赖：")
    print(f"   from biz.{module_name}.repo.{module_name}_repo import {class_name}Repository")
    print(f"   from biz.{module_name}.service.{module_name}_service import {class_name}Service")
    print(f"   {module_name}_repo = providers.Factory({class_name}Repository, session_factory=db_session_factory)")
    print(f"   {module_name}_service = providers.Factory({class_name}Service, {module_name}_repo={module_name}_repo)")
    print()
    print("2. 在 biz/application.py 中注册路由：")
    print(f"   from biz.{module_name}.api.{module_name}_api import {module_name}_api")
    print(f"   app.include_router({module_name}_api, prefix=api_prefix)")
    print()
    print("3. 在 biz/application.py 的 container.wire() 中添加模块：")
    print(f'   container.wire(modules=["biz.{module_name}.api.{module_name}_api"])')
    print()
    print("4. 运行数据库初始化脚本创建表：")
    print("   python -m base.init_db")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python scripts/create_module.py <module_name>")
        print("示例: python scripts/create_module.py user")
        sys.exit(1)

    module_name = sys.argv[1]

    # 验证模块名
    if not module_name.isidentifier():
        print(f"错误: '{module_name}' 不是有效的 Python 标识符")
        sys.exit(1)

    create_module(module_name)
