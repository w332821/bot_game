"""
第三方开奖API客户端
对应 Node.js 版本的 draw-api.js
集成真实的澳门快乐十分和澳门六合彩API
"""
import logging
import aiohttp
import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class DrawApiClient:
    """
    第三方开奖API客户端

    使用与Node.js版本相同的真实API:
    - 澳门快乐十分(幸运8): https://api.api168168.com/klsf/getHistoryLotteryInfo.do
    - 澳门六合彩: https://history.macaumarksix.com/history/macaujc2/y/2025
    """

    def __init__(self):
        """初始化客户端"""
        # 澳门快乐十分API (与Node.js版本相同)
        self.lucky8_api_base = os.getenv(
            'LUCKY8_API_BASE',
            'https://api.api168168.com'
        )

        # 澳门六合彩API (与Node.js版本相同)
        self.liuhecai_api_base = os.getenv(
            'LIUHECAI_API_BASE',
            'https://history.macaumarksix.com'
        )

        # 数据缓存 (与Node.js版本相同)
        self._lucky8_results: List[Dict] = []
        self._latest_lucky8_draw: Optional[Dict] = None
        self._draw_results: List[Dict] = []
        self._latest_draw: Optional[Dict] = None
        self._last_refresh: Optional[datetime] = None

        # 自动刷新任务
        self._refresh_task: Optional[asyncio.Task] = None

    async def _request(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        timeout: int = 10,
        retries: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        发送HTTP请求（带重试）

        Args:
            url: 请求URL
            method: HTTP方法
            params: 查询参数
            timeout: 超时时间（秒）
            retries: 重试次数

        Returns:
            Dict: 响应数据，失败返回None
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }

        for attempt in range(retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method,
                        url=url,
                        params=params,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status == 200:
                            # 检查 Content-Type 是否为 JSON
                            content_type = response.headers.get('Content-Type', '')
                            if 'application/json' in content_type or 'text/plain' in content_type:
                                try:
                                    return await response.json()
                                except Exception:
                                    # 尝试手动解析JSON
                                    text = await response.text()
                                    import json
                                    try:
                                        return json.loads(text)
                                    except:
                                        logger.warning(f"⚠️ 无法解析JSON响应: {url}")
                                        return None
                            else:
                                # 如果不是JSON，降低日志级别（不是错误，只是警告）
                                if attempt == retries:  # 只在最后一次失败时记录
                                    text = await response.text()
                                    logger.warning(f"⚠️ API返回非JSON响应: {url}")
                                    logger.debug(f"   Content-Type: {content_type}")
                                    logger.debug(f"   响应内容（前200字符）: {text[:200]}")
                                return None
                        else:
                            if attempt == retries:
                                logger.warning(f"⚠️ API请求失败: {url}, 状态码={response.status}")
                            return None

            except aiohttp.ClientError as e:
                if attempt == retries:
                    logger.warning(f"⚠️ API网络错误: {url} - {str(e)}")
                else:
                    await asyncio.sleep(1)  # 重试前等待1秒
                continue
            except Exception as e:
                if attempt == retries:
                    logger.warning(f"⚠️ API请求异常: {url} - {str(e)}")
                continue

        return None

    def _parse_draw_numbers(self, open_code: str) -> List[int]:
        """
        解析开奖号码字符串（逗号分隔）
        对应 Node.js: parseDrawNumbers()

        Args:
            open_code: 开奖号码字符串，如 "3,15,7,19,12,8,4,20"

        Returns:
            List[int]: 号码数组
        """
        try:
            if not open_code:
                return []
            return [int(x.strip()) for x in open_code.split(',') if x.strip().isdigit()]
        except Exception:
            return []

    def _calculate_lucky8_result(self, numbers: List[int]) -> Optional[int]:
        """
        计算幸运8结果（番数）
        对应 Node.js: calculateLucky8Result()

        规则：取最后一位数字 % 4 的余数
        - 余数 1 = 1番
        - 余数 2 = 2番
        - 余数 3 = 3番
        - 余数 0 = 4番

        Args:
            numbers: 开奖号码数组（至少1个数字）

        Returns:
            int: 番数 (1-4)，无效时返回None
        """
        if not numbers or len(numbers) == 0:
            return None

        # 取最后一位除以4的余数
        last_number = numbers[-1]

        if not isinstance(last_number, int):
            return None

        remainder = last_number % 4

        # 根据规则映射到番数
        if remainder == 1:
            return 1
        elif remainder == 2:
            return 2
        elif remainder == 3:
            return 3
        elif remainder == 0:
            return 4

        return None

    async def fetch_lucky8_results(self) -> bool:
        """
        获取澳门快乐十分开奖数据
        对应 Node.js: fetchLucky8Results()

        API: https://api.api168168.com/klsf/getHistoryLotteryInfo.do
        参数: date=&lotCode=10011

        Returns:
            bool: 是否成功获取数据
        """
        try:
            url = f"{self.lucky8_api_base}/klsf/getHistoryLotteryInfo.do"
            params = {
                'date': '',
                'lotCode': '10011'
            }

            logger.info("📡 正在获取澳门快乐十分开奖数据...")
            data = await self._request(url, params=params)

            if data and data.get('errorCode') == 0:
                result = data.get('result', {})
                result_data = result.get('data', [])

                if result_data and len(result_data) > 0:
                    self._lucky8_results = result_data
                    self._latest_lucky8_draw = result_data[0]  # 最新的开奖结果

                    logger.info(
                        f"✅ 获取到 {len(self._lucky8_results)} 条快乐十分开奖记录，"
                        f"最新期号: {self._latest_lucky8_draw.get('preDrawIssue')}"
                    )
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ 获取快乐十分开奖数据失败: {str(e)}")
            return False

    async def fetch_draw_results(self) -> bool:
        """
        获取澳门六合彩开奖数据
        对应 Node.js: fetchDrawResults()

        API: https://history.macaumarksix.com/history/macaujc2/y/2025

        Returns:
            bool: 是否成功获取数据
        """
        try:
            current_year = datetime.now().year
            url = f"{self.liuhecai_api_base}/history/macaujc2/y/{current_year}"

            logger.info("📡 正在获取澳门六合彩开奖数据...")
            data = await self._request(url)

            if data and data.get('result') and data.get('data'):
                draw_data = data.get('data', [])

                if draw_data and len(draw_data) > 0:
                    self._draw_results = draw_data
                    self._latest_draw = draw_data[0]  # 最新的开奖结果

                    logger.info(
                        f"✅ 获取到 {len(self._draw_results)} 条澳门六合彩开奖记录，"
                        f"最新期号: {self._latest_draw.get('expect')}"
                    )
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ 获取澳门六合彩开奖数据失败: {str(e)}")
            return False

    async def initialize_draw_data(self) -> Dict[str, bool]:
        """
        初始化开奖数据（启动时调用）
        对应 Node.js: initializeDrawData()

        Returns:
            Dict: {'lucky8_success': bool, 'draw_success': bool}
        """
        logger.info("🔄 开始获取开奖数据...")

        lucky8_success = await self.fetch_lucky8_results()
        draw_success = await self.fetch_draw_results()

        if lucky8_success:
            logger.info("✅ 快乐十分开奖数据初始化成功")
        else:
            logger.warning("⚠️ 快乐十分开奖数据初始化失败，将使用随机番数")

        if draw_success:
            logger.info("✅ 澳门六合彩开奖数据初始化成功")
        else:
            logger.warning("⚠️ 澳门六合彩开奖数据初始化失败")

        self._last_refresh = datetime.now()

        return {
            'lucky8_success': lucky8_success,
            'draw_success': draw_success
        }

    def get_latest_lucky8_draw_number(self) -> Dict[str, Any]:
        """
        获取最新的幸运8开奖结果（番数）
        对应 Node.js: getLatestLucky8DrawNumber()

        Returns:
            Dict: {
                'draw_number': int,       # 番数 (1-4)
                'draw_code': str,         # 完整开奖号码
                'issue': str,             # 期号
                'numbers': List[int],     # 号码数组
                'special_number': int,    # 特码（第8位）
                'is_random': bool         # 是否为随机数
            }
        """
        if not self._latest_lucky8_draw:
            # 如果没有数据，返回随机番数（兜底）
            logger.warning("⚠️ 未获取到快乐十分开奖数据，使用随机番数")
            import random
            # 生成随机番数 (1-4)
            random_fan = random.randint(1, 4)
            # 生成随机特码 (1-20，澳洲幸运8的特码范围)
            random_tema = random.randint(1, 20)
            return {
                'draw_number': random_fan,
                'draw_code': None,
                'issue': 'random',
                'numbers': [],
                'special_number': random_tema,
                'is_random': True
            }

        # 解析开奖号码
        numbers = self._parse_draw_numbers(self._latest_lucky8_draw.get('preDrawCode', ''))
        draw_number = self._calculate_lucky8_result(numbers)

        # 计算特码（第8位，如果没有则用最后一位）
        special_number = None
        if len(numbers) >= 8:
            special_number = numbers[7]
        elif len(numbers) > 0:
            special_number = numbers[-1]

        return {
            'draw_number': draw_number,
            'draw_code': self._latest_lucky8_draw.get('preDrawCode'),
            'issue': self._latest_lucky8_draw.get('preDrawIssue'),
            'numbers': numbers,
            'special_number': special_number,
            'is_random': False
        }

    def get_latest_marksix_tema(self) -> Dict[str, Any]:
        """
        获取最新的六合彩特码（第7位号码）
        对应 Node.js: getLatestMarkSixTema()

        Returns:
            Dict: {
                'draw_number': int,       # 特码号码 (1-49)
                'draw_code': str,         # 完整开奖号码
                'issue': str,             # 期号
                'numbers': List[int],     # 号码数组（7个）
                'special_number': int,    # 特码值
                'is_random': bool         # 是否为随机数
            }
        """
        if not self._latest_draw:
            # 如果没有数据，返回随机特码（1-49兜底）
            logger.warning("⚠️ 未获取到六合彩开奖数据，使用随机特码")
            import random
            random_tema = random.randint(1, 49)
            return {
                'draw_number': random_tema,
                'draw_code': None,
                'issue': 'random',
                'numbers': [],
                'special_number': random_tema,
                'is_random': True
            }

        # 解析开奖号码（逗号分隔的7个数字）
        numbers = self._parse_draw_numbers(self._latest_draw.get('openCode', ''))

        if len(numbers) != 7:
            logger.warning("⚠️ 六合彩开奖号码格式错误，使用随机特码")
            import random
            random_tema = random.randint(1, 49)
            return {
                'draw_number': random_tema,
                'draw_code': self._latest_draw.get('openCode'),
                'issue': self._latest_draw.get('expect'),
                'numbers': [],
                'special_number': random_tema,
                'is_random': True
            }

        # 第7位（索引6）是特码号码（1-49）
        special_number = numbers[6]

        # 处理期号：将最后一个逗号换成"特"
        issue = self._latest_draw.get('expect', '')
        if issue and ',' in issue:
            issue = issue[:issue.rfind(',')] + '特' + issue[issue.rfind(',') + 1:]

        return {
            'draw_number': special_number,
            'draw_code': self._latest_draw.get('openCode'),
            'issue': issue,
            'numbers': numbers,
            'special_number': special_number,
            'is_random': False
        }

    def get_recent_lucky8_draws(self, limit: int = 15) -> List[Dict[str, Any]]:
        """
        获取最近N期的幸运8开奖记录
        对应 Node.js: getRecentLucky8Draws()

        Args:
            limit: 获取数量

        Returns:
            List[Dict]: 开奖记录数组
        """
        if not self._lucky8_results:
            return []

        valid_draws = []

        for draw in self._lucky8_results:
            if len(valid_draws) >= limit:
                break

            numbers = self._parse_draw_numbers(draw.get('preDrawCode', ''))
            draw_number = self._calculate_lucky8_result(numbers)

            # 只添加有效的记录（draw_number 不为 None）
            if draw_number is not None:
                # 计算特码（第8位，如果没有则用最后一位）
                special_number = None
                if len(numbers) >= 8:
                    special_number = numbers[7]
                elif len(numbers) > 0:
                    special_number = numbers[-1]

                valid_draws.append({
                    'issue': draw.get('preDrawIssue'),
                    'draw_number': str(draw_number),  # 番数
                    'draw_code': draw.get('preDrawCode'),
                    'special_number': special_number,
                    'timestamp': draw.get('preDrawTime'),
                    'numbers': numbers
                })

        return valid_draws

    def get_recent_marksix_draws(self, limit: int = 15) -> List[Dict[str, Any]]:
        """
        获取最近N期的六合彩开奖记录
        对应 Node.js: getRecentMarkSixDraws()

        Args:
            limit: 获取数量

        Returns:
            List[Dict]: 开奖记录数组
        """
        if not self._draw_results:
            return []

        valid_draws = []

        for draw in self._draw_results:
            if len(valid_draws) >= limit:
                break

            numbers = self._parse_draw_numbers(draw.get('openCode', ''))

            # 六合彩需要7个号码
            if len(numbers) != 7:
                continue

            # 第7位（索引6）是特码
            special_number = numbers[6]

            # 处理期号：将最后一个逗号换成"特"
            issue = draw.get('expect', '')
            if issue and ',' in issue:
                issue = issue[:issue.rfind(',')] + '特' + issue[issue.rfind(',') + 1:]

            valid_draws.append({
                'issue': issue,
                'draw_number': str(special_number),  # 特码
                'draw_code': draw.get('openCode'),
                'special_number': special_number,
                'timestamp': draw.get('drawTime'),
                'numbers': numbers
            })

        return valid_draws

    async def start_auto_refresh(self, interval_minutes: int = 5):
        """
        启动自动刷新开奖数据
        对应 Node.js: startAutoRefresh()

        Args:
            interval_minutes: 刷新间隔（分钟）
        """
        logger.info(f"🔄 开启自动刷新开奖数据，间隔: {interval_minutes} 分钟")

        async def refresh_loop():
            while True:
                try:
                    await asyncio.sleep(interval_minutes * 60)
                    logger.info("🔄 刷新开奖数据...")
                    await self.fetch_lucky8_results()
                    await self.fetch_draw_results()
                    self._last_refresh = datetime.now()
                except Exception as e:
                    logger.error(f"❌ 自动刷新失败: {str(e)}")

        # 创建后台任务
        self._refresh_task = asyncio.create_task(refresh_loop())

    def stop_auto_refresh(self):
        """停止自动刷新"""
        if self._refresh_task:
            self._refresh_task.cancel()
            logger.info("⏹️ 已停止自动刷新开奖数据")

    async def get_latest_lucky8_draw(self) -> Optional[Dict[str, Any]]:
        """
        获取最新的澳洲幸运8开奖结果（统一接口）

        Returns:
            Dict: 开奖数据
        """
        result = self.get_latest_lucky8_draw_number()

        return {
            'issue': result['issue'],
            'draw_number': result['draw_number'],
            'draw_code': result['draw_code'],
            'special_number': result['special_number'],
            'draw_time': datetime.now()
        }

    async def get_latest_liuhecai_draw(self) -> Optional[Dict[str, Any]]:
        """
        获取最新的六合彩开奖结果（统一接口）

        Returns:
            Dict: 开奖数据
        """
        result = self.get_latest_marksix_tema()

        return {
            'issue': result['issue'],
            'draw_number': None,  # 六合彩没有番数
            'draw_code': result['draw_code'],
            'special_number': result['special_number'],
            'draw_time': datetime.now()
        }

    async def get_draw_result(self, game_type: str, force_refresh: bool = True) -> Optional[Dict[str, Any]]:
        """
        根据游戏类型获取最新开奖结果（统一接口）

        Args:
            game_type: 游戏类型（lucky8/liuhecai）
            force_refresh: 是否强制刷新API数据（默认True，确保每次开奖都获取最新数据）

        Returns:
            Dict: 开奖数据
        """
        # 在获取结果前先刷新数据，确保拿到最新的开奖号码
        if force_refresh:
            if game_type == 'lucky8':
                await self.fetch_lucky8_results()
            elif game_type == 'liuhecai':
                await self.fetch_draw_results()

        if game_type == 'lucky8':
            return await self.get_latest_lucky8_draw()
        elif game_type == 'liuhecai':
            return await self.get_latest_liuhecai_draw()
        else:
            logger.error(f"❌ 不支持的游戏类型: {game_type}")
            return None

    async def get_recent_draws(self, game_type: str, limit: int = 30) -> List[Dict[str, Any]]:
        """
        根据游戏类型获取最近N期开奖记录（统一接口）
        对应 bot-server.js 中 drawApi.getRecentLucky8Draws() 和 getRecentMarkSixDraws()

        Args:
            game_type: 游戏类型（lucky8/liuhecai）
            limit: 获取数量

        Returns:
            List[Dict]: 开奖记录数组
        """
        if game_type == 'lucky8':
            return self.get_recent_lucky8_draws(limit=limit)
        elif game_type == 'liuhecai':
            return self.get_recent_marksix_draws(limit=limit)
        else:
            logger.error(f"❌ 不支持的游戏类型: {game_type}")
            return []

    def get_draw_stats(self) -> Dict[str, Any]:
        """
        获取开奖数据统计信息
        对应 Node.js: getDrawStats()

        Returns:
            Dict: 统计信息
        """
        lucky8_info = self.get_latest_lucky8_draw_number()
        marksix_info = self.get_latest_marksix_tema()

        return {
            'lucky8': {
                'total_records': len(self._lucky8_results),
                'latest_issue': lucky8_info.get('issue'),
                'latest_draw_number': lucky8_info.get('draw_number'),
                'last_refresh': self._last_refresh.isoformat() if self._last_refresh else None
            },
            'markSix': {
                'total_records': len(self._draw_results),
                'latest_issue': marksix_info.get('issue'),
                'latest_tema': marksix_info.get('special_number'),
                'last_refresh': self._last_refresh.isoformat() if self._last_refresh else None
            }
        }


# 全局单例
_draw_api_client: Optional[DrawApiClient] = None


def get_draw_api_client() -> DrawApiClient:
    """获取DrawApiClient单例"""
    global _draw_api_client
    if _draw_api_client is None:
        _draw_api_client = DrawApiClient()
    return _draw_api_client
