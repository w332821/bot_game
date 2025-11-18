"""
测试角色管理 CRUD 接口
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from biz.roles.service.role_service import RoleService
from biz.roles.repo.role_repo import RoleRepository


class TestRoleList:
    """测试角色列表"""

    @pytest.mark.asyncio
    async def test_get_roles_success(self):
        """测试成功获取角色列表"""
        mock_repo = AsyncMock(spec=RoleRepository)
        mock_repo.get_roles = AsyncMock(return_value={
            "list": [
                {
                    "id": 1,
                    "roleName": "管理员",
                    "roleCode": "admin",
                    "description": "系统管理员",
                    "userCount": 5,
                    "status": "启用",
                    "createTime": "2023-11-17 10:00:00"
                }
            ],
            "total": 1
        })

        service = RoleService(role_repo=mock_repo)
        result = await service.get_roles(1, 10)

        assert result["total"] == 1
        assert len(result["list"]) == 1
        assert result["list"][0]["roleName"] == "管理员"


class TestRoleDetail:
    """测试角色详情"""

    @pytest.mark.asyncio
    async def test_get_role_detail_success(self):
        """测试成功获取角色详情"""
        mock_repo = AsyncMock(spec=RoleRepository)
        mock_repo.get_role_by_id = AsyncMock(return_value={
            "id": 1,
            "roleName": "管理员",
            "roleCode": "admin",
            "remarks": "备注",
            "permissions": ["personal-basic-1", "users-members-1"]
        })

        service = RoleService(role_repo=mock_repo)
        result = await service.get_role_detail(1)

        assert result["roleName"] == "管理员"
        assert len(result["permissions"]) == 2


class TestRoleCreate:
    """测试创建角色"""

    @pytest.mark.asyncio
    async def test_create_role_success(self):
        """测试成功创建角色"""
        mock_repo = AsyncMock(spec=RoleRepository)
        mock_repo.check_role_code_exists = AsyncMock(return_value=False)
        mock_repo.create_role = AsyncMock(return_value=1)

        service = RoleService(role_repo=mock_repo)
        role_id = await service.create_role(
            "新角色",
            "备注",
            ["personal-basic-1", "users-members-1"]
        )

        assert role_id == 1
        mock_repo.create_role.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_role_invalid_name(self):
        """测试创建角色时名称无效"""
        mock_repo = AsyncMock(spec=RoleRepository)
        service = RoleService(role_repo=mock_repo)

        with pytest.raises(ValueError, match="角色名称不能为空"):
            await service.create_role("", "备注", ["personal-basic-1"])

    @pytest.mark.asyncio
    async def test_create_role_empty_permissions(self):
        """测试创建角色时权限列表为空"""
        mock_repo = AsyncMock(spec=RoleRepository)
        service = RoleService(role_repo=mock_repo)

        with pytest.raises(ValueError, match="权限列表不能为空"):
            await service.create_role("新角色", "备注", [])

    @pytest.mark.asyncio
    async def test_create_role_invalid_permission_code(self):
        """测试创建角色时权限编码无效"""
        mock_repo = AsyncMock(spec=RoleRepository)
        service = RoleService(role_repo=mock_repo)

        with pytest.raises(ValueError, match="无效的权限编码"):
            await service.create_role("新角色", "备注", ["invalid-code"])


class TestRoleUpdate:
    """测试更新角色"""

    @pytest.mark.asyncio
    async def test_update_role_success(self):
        """测试成功更新角色"""
        mock_repo = AsyncMock(spec=RoleRepository)
        mock_repo.get_role_by_id = AsyncMock(return_value={
            "id": 1,
            "roleName": "管理员",
            "roleCode": "admin",
            "remarks": "备注",
            "permissions": ["personal-basic-1"]
        })
        mock_repo.update_role = AsyncMock(return_value=True)

        service = RoleService(role_repo=mock_repo)
        result = await service.update_role(
            1, "新名称", "新备注", ["personal-basic-2"]
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_update_role_not_found(self):
        """测试更新不存在的角色"""
        mock_repo = AsyncMock(spec=RoleRepository)
        mock_repo.get_role_by_id = AsyncMock(return_value=None)

        service = RoleService(role_repo=mock_repo)

        with pytest.raises(ValueError, match="角色不存在"):
            await service.update_role(999, "名称", "备注", ["personal-basic-1"])


class TestRoleDelete:
    """测试删除角色"""

    @pytest.mark.asyncio
    async def test_delete_role_success(self):
        """测试成功删除角色"""
        mock_repo = AsyncMock(spec=RoleRepository)
        mock_repo.get_role_by_id = AsyncMock(return_value={"id": 1})
        mock_repo.get_role_user_count = AsyncMock(return_value=0)
        mock_repo.delete_role = AsyncMock(return_value=True)

        service = RoleService(role_repo=mock_repo)
        result = await service.delete_role(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_role_has_users(self):
        """测试删除有用户的角色"""
        mock_repo = AsyncMock(spec=RoleRepository)
        mock_repo.get_role_by_id = AsyncMock(return_value={"id": 1})
        mock_repo.get_role_user_count = AsyncMock(return_value=5)

        service = RoleService(role_repo=mock_repo)

        with pytest.raises(ValueError, match="无法删除"):
            await service.delete_role(1)


class TestPermissionsTree:
    """测试权限树"""

    def test_get_permissions_tree(self):
        """测试获取权限树"""
        mock_repo = MagicMock(spec=RoleRepository)
        mock_repo.get_permissions_tree = MagicMock(return_value=[
            {
                "id": "personal",
                "label": "个人管理",
                "children": [
                    {
                        "id": "personal-basic",
                        "label": "基本资料",
                        "children": [
                            {"id": "personal-basic-1", "label": "修改盘口"}
                        ]
                    }
                ]
            }
        ])

        service = RoleService(role_repo=mock_repo)
        tree = service.get_permissions_tree()

        assert len(tree) > 0
        assert tree[0]["id"] == "personal"


class TestValidation:
    """测试验证逻辑"""

    def test_validate_role_name(self):
        """测试角色名称验证"""
        mock_repo = MagicMock(spec=RoleRepository)
        service = RoleService(role_repo=mock_repo)

        # 正常名称
        assert service.validate_role_name("管理员") == "管理员"

        # 空名称
        with pytest.raises(ValueError):
            service.validate_role_name("")

        # 过长名称
        with pytest.raises(ValueError):
            service.validate_role_name("a" * 51)

    def test_validate_permissions(self):
        """测试权限验证"""
        mock_repo = MagicMock(spec=RoleRepository)
        service = RoleService(role_repo=mock_repo)

        # 正常权限
        perms = service.validate_permissions(["personal-basic-1", "users-members-2"])
        assert len(perms) == 2

        # 空权限
        with pytest.raises(ValueError):
            service.validate_permissions([])

        # 无效格式
        with pytest.raises(ValueError):
            service.validate_permissions(["invalid"])

    def test_generate_role_code(self):
        """测试角色编码生成"""
        mock_repo = MagicMock(spec=RoleRepository)
        service = RoleService(role_repo=mock_repo)

        code = service.generate_role_code("管理员")
        assert "_" in code  # 包含时间戳分隔符
