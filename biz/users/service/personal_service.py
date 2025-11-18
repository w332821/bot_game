"""
个人中心 Service
"""
from typing import Optional, Dict, Any, List
import re
from biz.users.repo.personal_repo import PersonalRepository
from base.game_name_mapper import validate_game_name


class PersonalService:
    def __init__(self, personal_repo: PersonalRepository):
        self.personal_repo = personal_repo

    async def get_basic_info(self, account: str) -> Optional[Dict[str, Any]]:
        """
        获取个人基本信息
        """
        return await self.personal_repo.get_basic_info(account)

    async def update_basic_info(
        self,
        account: str,
        plate: Optional[str] = None,
        open_plate: Optional[List[str]] = None,
        earn_rebate: Optional[str] = None,
        subordinate_transfer: Optional[str] = None,
        default_rebate_plate: Optional[str] = None
    ) -> bool:
        """
        更新个人基本信息
        """
        # 验证 openPlate（如果提供）
        if open_plate is not None:
            valid_plates = {'A', 'B', 'C', 'D'}
            if not open_plate or len(open_plate) == 0:
                raise ValueError("开放盘口不能为空")
            for p in open_plate:
                if p not in valid_plates:
                    raise ValueError(f"无效的盘口: {p}，只能是 A/B/C/D")

        return await self.personal_repo.update_basic_info(
            account, plate, open_plate, earn_rebate, subordinate_transfer, default_rebate_plate
        )

    def validate_domain(self, domain: str) -> bool:
        """
        验证域名格式
        """
        # 域名正则
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(pattern, domain):
            raise ValueError(f"无效的域名格式: {domain}")
        return True

    async def add_promotion_domain(self, account: str, domain: str) -> Dict[str, Any]:
        """
        添加推广域名（仅代理）
        """
        # 验证域名格式
        self.validate_domain(domain)

        await self.personal_repo.add_promotion_domain(account, domain)

        # 返回推广链接列表
        links = await self.personal_repo.get_promotion_links(account)
        return {"promotionLinks": links}

    def validate_lottery_rebate_config(self, config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        验证彩票退水配置
        """
        if not config:
            raise ValueError("彩票退水配置不能为空")

        for item in config:
            # 验证必需字段
            if "gameName" not in item:
                raise ValueError("缺少必需字段: gameName")

            # 验证游戏名称
            try:
                validate_game_name(item["gameName"])
            except ValueError as e:
                raise ValueError(f"无效的游戏名称: {str(e)}")

            # 如果是分组，验证 children
            if item.get("isGroup"):
                if "children" not in item:
                    raise ValueError(f"分组 {item['gameName']} 缺少 children 字段")
                if not isinstance(item["children"], list):
                    raise ValueError(f"分组 {item['gameName']} 的 children 必须是数组")

                # 递归验证子项
                for child in item["children"]:
                    if "betTypeName" not in child or "rebate" not in child:
                        raise ValueError("投注类型缺少必需字段: betTypeName, rebate")

                    rebate = child["rebate"]
                    if not isinstance(rebate, (int, float)) or rebate < 0 or rebate > 100:
                        raise ValueError(f"退水比例必须在 0-100 之间，收到: {rebate}")
            else:
                # 非分组项必须有 betTypeName 和 rebate
                if "betTypeName" not in item or "rebate" not in item:
                    raise ValueError("投注类型缺少必需字段: betTypeName, rebate")

                rebate = item["rebate"]
                if not isinstance(rebate, (int, float)) or rebate < 0 or rebate > 100:
                    raise ValueError(f"退水比例必须在 0-100 之间，收到: {rebate}")

        return config

    async def get_lottery_rebate_config(self, account: str) -> List[Dict[str, Any]]:
        """
        获取彩票退水配置
        """
        config = await self.personal_repo.get_lottery_rebate_config(account)
        return config if config else []

    async def save_lottery_rebate_config(
        self,
        account: str,
        config: List[Dict[str, Any]]
    ) -> bool:
        """
        保存彩票退水配置
        """
        # 验证配置
        validated_config = self.validate_lottery_rebate_config(config)

        return await self.personal_repo.save_lottery_rebate_config(account, validated_config)

    async def get_login_logs(
        self,
        account: str,
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """
        获取登录日志
        """
        return await self.personal_repo.get_login_logs(account, page, page_size)

    async def update_password(
        self,
        account: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        修改密码
        """
        # 验证新密码长度
        if len(new_password) < 6 or len(new_password) > 20:
            raise ValueError("新密码长度必须在 6-20 之间")

        return await self.personal_repo.update_password(account, old_password, new_password)
