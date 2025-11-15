"""
开奖图片生成器
对应 bot-server.js 中的 draw-image.js
使用PIL/Pillow生成开奖历史图片
"""
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import tempfile

logger = logging.getLogger(__name__)


class DrawImageGenerator:
    """开奖图片生成器"""

    def __init__(self):
        """初始化生成器"""
        # 对应 Node.js: /root/yueliao-server/uploads
        # Python版本使用环境变量配置，默认为 /root/yueliao-server/uploads
        self.uploads_dir = os.getenv('UPLOADS_DIR', '/root/yueliao-server/uploads')

        # 确保uploads目录存在
        if not os.path.exists(self.uploads_dir):
            try:
                os.makedirs(self.uploads_dir, exist_ok=True)
                logger.info(f"✅ 创建uploads目录: {self.uploads_dir}")
            except Exception as e:
                logger.warning(f"⚠️ 无法创建uploads目录，使用临时目录: {str(e)}")
                self.uploads_dir = tempfile.gettempdir()

        self.image_width = 800
        self.image_height_per_row = 60
        self.padding = 20
        self.font_size = 24

        # 尝试加载字体
        self.font = self._load_font()

    def _load_font(self) -> ImageFont:
        """
        加载字体

        Returns:
            ImageFont: 字体对象
        """
        try:
            # 尝试加载系统字体（支持中文）
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "C:\\Windows\\Fonts\\msyh.ttc",  # Windows
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, self.font_size)

            logger.warning("⚠️ 未找到系统字体，使用默认字体")
            return ImageFont.load_default()

        except Exception as e:
            logger.error(f"❌ 加载字体失败: {str(e)}")
            return ImageFont.load_default()

    def generate_lucky8_image(
        self,
        draws: List[Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> str:
        """
        生成澳洲幸运8开奖历史图片

        Args:
            draws: 开奖记录列表，每条记录包含：
                - issue: 期号
                - draw_number: 番数（1-4）
                - special_number: 特码（1-20）
                - draw_time: 开奖时间
            save_path: 保存路径，如果不提供则生成临时文件

        Returns:
            str: 图片文件路径
        """
        if not draws:
            logger.warning("⚠️ 开奖记录为空，无法生成图片")
            return None

        # 计算图片高度
        row_count = len(draws) + 1  # +1 for header
        image_height = row_count * self.image_height_per_row + self.padding * 2

        # 创建图片
        image = Image.new('RGB', (self.image_width, image_height), color='white')
        draw = ImageDraw.Draw(image)

        # 绘制标题
        title = "【澳洲幸运8开奖历史】"
        title_y = self.padding
        draw.text((self.image_width // 2 - 150, title_y), title, fill='black', font=self.font)

        # 绘制表头
        header_y = title_y + self.image_height_per_row
        headers = ["期号", "番数", "特码", "时间"]
        col_widths = [200, 100, 100, 300]
        x_offset = self.padding

        for i, header in enumerate(headers):
            draw.text((x_offset, header_y), header, fill='black', font=self.font)
            x_offset += col_widths[i]

        # 绘制数据行
        y_offset = header_y + self.image_height_per_row

        for draw_data in draws:
            issue = str(draw_data.get('issue', 'N/A'))
            draw_number = str(draw_data.get('draw_number', 'N/A'))
            special_number = str(draw_data.get('special_number', 'N/A'))

            # 格式化时间
            draw_time = draw_data.get('draw_time') or draw_data.get('timestamp')
            if isinstance(draw_time, datetime):
                time_str = draw_time.strftime('%Y-%m-%d %H:%M')
            else:
                time_str = str(draw_time) if draw_time else 'N/A'

            # 绘制每一列
            x_offset = self.padding
            values = [issue, draw_number, special_number, time_str]

            for i, value in enumerate(values):
                draw.text((x_offset, y_offset), value, fill='black', font=self.font)
                x_offset += col_widths[i]

            y_offset += self.image_height_per_row

        # 保存图片
        # 对应 Node.js: /root/yueliao-server/uploads/draw_{gameType}_{issue}.png
        if not save_path:
            # 尝试从开奖记录中获取期号
            issue = draws[0].get('issue', datetime.now().strftime('%Y%m%d%H%M%S')) if draws else 'unknown'
            filename = f"draw_lucky8_{issue}.png"
            save_path = os.path.join(self.uploads_dir, filename)

        image.save(save_path)
        logger.info(f"✅ 澳洲幸运8图片已生成: {save_path}")

        return save_path

    def generate_liuhecai_image(
        self,
        draws: List[Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> str:
        """
        生成六合彩开奖历史图片

        Args:
            draws: 开奖记录列表，每条记录包含：
                - issue: 期号
                - draw_code: 开奖号码
                - special_number: 特码
                - draw_time: 开奖时间
            save_path: 保存路径

        Returns:
            str: 图片文件路径
        """
        if not draws:
            logger.warning("⚠️ 开奖记录为空，无法生成图片")
            return None

        # 计算图片高度
        row_count = len(draws) + 1  # +1 for header
        image_height = row_count * self.image_height_per_row + self.padding * 2

        # 创建图片
        image = Image.new('RGB', (self.image_width, image_height), color='white')
        draw = ImageDraw.Draw(image)

        # 绘制标题
        title = "【六合彩开奖历史】"
        title_y = self.padding
        draw.text((self.image_width // 2 - 120, title_y), title, fill='black', font=self.font)

        # 绘制表头
        header_y = title_y + self.image_height_per_row
        headers = ["期号", "特码", "时间"]
        col_widths = [200, 150, 300]
        x_offset = self.padding

        for i, header in enumerate(headers):
            draw.text((x_offset, header_y), header, fill='black', font=self.font)
            x_offset += col_widths[i]

        # 绘制数据行
        y_offset = header_y + self.image_height_per_row

        for draw_data in draws:
            issue = str(draw_data.get('issue', 'N/A'))
            special_number = str(draw_data.get('special_number', 'N/A'))

            # 格式化时间
            draw_time = draw_data.get('draw_time') or draw_data.get('timestamp')
            if isinstance(draw_time, datetime):
                time_str = draw_time.strftime('%Y-%m-%d %H:%M')
            else:
                time_str = str(draw_time) if draw_time else 'N/A'

            # 绘制每一列
            x_offset = self.padding
            values = [issue, special_number, time_str]

            for i, value in enumerate(values):
                draw.text((x_offset, y_offset), value, fill='black', font=self.font)
                x_offset += col_widths[i]

            y_offset += self.image_height_per_row

        # 保存图片
        # 对应 Node.js: /root/yueliao-server/uploads/draw_{gameType}_{issue}.png
        if not save_path:
            # 尝试从开奖记录中获取期号
            issue = draws[0].get('issue', datetime.now().strftime('%Y%m%d%H%M%S')) if draws else 'unknown'
            filename = f"draw_liuhecai_{issue}.png"
            save_path = os.path.join(self.uploads_dir, filename)

        image.save(save_path)
        logger.info(f"✅ 六合彩图片已生成: {save_path}")

        return save_path

    def generate_image(
        self,
        game_type: str,
        draws: List[Dict[str, Any]],
        save_path: Optional[str] = None
    ) -> str:
        """
        根据游戏类型生成开奖图片（统一接口）

        Args:
            game_type: 游戏类型（lucky8/liuhecai）
            draws: 开奖记录列表
            save_path: 保存路径

        Returns:
            str: 图片文件路径
        """
        if game_type == 'lucky8':
            return self.generate_lucky8_image(draws, save_path)
        elif game_type == 'liuhecai':
            return self.generate_liuhecai_image(draws, save_path)
        else:
            logger.error(f"❌ 不支持的游戏类型: {game_type}")
            return None


# 全局单例
_generator: Optional[DrawImageGenerator] = None


def get_draw_image_generator() -> DrawImageGenerator:
    """获取DrawImageGenerator单例"""
    global _generator
    if _generator is None:
        _generator = DrawImageGenerator()
    return _generator
