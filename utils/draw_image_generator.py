"""
开奖图片生成器
对应 bot-server.js 中的 draw-image.js
完全复刻Node.js版本的表格结构和样式
"""
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import tempfile

logger = logging.getLogger(__name__)


class DrawImageGenerator:
    """开奖图片生成器 - 完全对应Node.js版本"""

    def __init__(self):
        """初始化生成器"""
        # 对应 Node.js: /root/yueliao-server/uploads
        self.uploads_dir = os.getenv('UPLOADS_DIR', '/root/yueliao-server/uploads')

        # 确保uploads目录存在
        if not os.path.exists(self.uploads_dir):
            try:
                os.makedirs(self.uploads_dir, exist_ok=True)
                logger.info(f"✅ 创建uploads目录: {self.uploads_dir}")
            except Exception as e:
                logger.warning(f"⚠️ 无法创建uploads目录，使用临时目录: {str(e)}")
                self.uploads_dir = tempfile.gettempdir()

        # 对应 Node.js Canvas版本的尺寸参数 (line 322-326)
        self.width = 1000
        self.header_height = 60
        self.row_height = 45
        self.padding = 20

        # 尝试加载字体
        self.font = self._load_font(16)  # 普通字体，增大以更清晰
        self.header_font = self._load_font(18, bold=True)  # 表头加粗
        self.footer_font = self._load_font(12)  # 底部小字

    def _load_font(self, size: int, bold: bool = False) -> ImageFont:
        """
        加载字体
        对应 Node.js: 'Microsoft YaHei', 'SimHei', Arial

        Args:
            size: 字体大小
            bold: 是否加粗

        Returns:
            ImageFont: 字体对象
        """
        try:
            # 尝试加载系统字体（支持中文）
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",  # macOS
                "/System/Library/Fonts/STHeiti Light.ttc",  # macOS 黑体
                "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux Noto
                "C:\\Windows\\Fonts\\msyh.ttc",  # Windows 微软雅黑
                "C:\\Windows\\Fonts\\simhei.ttf",  # Windows 黑体
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    logger.info(f"✅ 使用字体: {font_path} (size={size})")
                    return ImageFont.truetype(font_path, size)

            logger.error("❌ 未找到任何中文字体！表头和中文将无法显示")
            logger.error("❌ 请安装中文字体，或检查字体路径")
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
        对应 Node.js generateCanvasImage() line 306-439

        表格结构（6列）：期号 | 开奖号码 | 特码 | 宝 | 大小 | 单双

        Args:
            draws: 开奖记录列表
            save_path: 保存路径

        Returns:
            str: 图片文件路径
        """
        if not draws:
            logger.warning("⚠️ 开奖记录为空，无法生成图片")
            return None

        # 对应 Node.js line 312-320
        headers = ['期号', '开奖号码', '特码', '宝', '大小', '单双']
        # 增加开奖号码列宽度，确保长号码能完整显示
        col_widths = [100, 350, 100, 100, 100, 100]

        # 计算列位置 - 对应 Node.js line 336-339
        col_x = [self.padding]
        for i in range(len(col_widths) - 1):
            col_x.append(col_x[-1] + col_widths[i])

        # 计算图片高度 - 对应 Node.js line 322-326
        rows = min(len(draws), 15)  # 最多显示15期
        height = self.header_height + self.row_height * (rows + 1) + 40

        # 创建图片 - 对应 Node.js line 328-333
        image = Image.new('RGB', (self.width, height), color='white')
        draw_ctx = ImageDraw.Draw(image)

        # ==================== 绘制表头 ====================
        # 对应 Node.js line 341-356

        # 表头背景 (#f5f5f5)
        draw_ctx.rectangle(
            [self.padding, 10, self.width - self.padding, 10 + self.header_height],
            fill='#f5f5f5',
            outline='#cccccc',
            width=1
        )

        # 表头竖线
        for i in range(1, len(col_widths)):
            x = col_x[i]
            draw_ctx.line([(x, 10), (x, 10 + self.header_height)], fill='#cccccc', width=1)

        # 表头文字 - 对应 Node.js line 358-365
        # Node.js: ctx.fillText(header, colX[i] + colWidths[i] / 2, 30 + 8);
        for i, header in enumerate(headers):
            text_x = col_x[i] + col_widths[i] // 2
            text_y = 30 + 8  # 对应Node.js的固定位置
            # 居中绘制
            bbox = draw_ctx.textbbox((0, 0), header, font=self.header_font)
            text_width = bbox[2] - bbox[0]
            draw_ctx.text(
                (text_x - text_width // 2, text_y),
                header,
                fill='#000000',
                font=self.header_font
            )

        # ==================== 绘制数据行 ====================
        # 对应 Node.js line 367-426

        for index, draw_data in enumerate(draws[:15]):  # 最多15期
            row_y = 10 + self.header_height + self.row_height * index

            # 行背景（交替颜色） - 对应 Node.js line 373-375
            bg_color = '#ffffff' if index % 2 == 0 else '#fafafa'
            draw_ctx.rectangle(
                [self.padding, row_y, self.width - self.padding, row_y + self.row_height],
                fill=bg_color,
                outline='#e0e0e0',
                width=1
            )

            # 列竖线 - 对应 Node.js line 382-388
            for i in range(1, len(col_widths)):
                x = col_x[i]
                draw_ctx.line([(x, row_y), (x, row_y + self.row_height)], fill='#e0e0e0', width=1)

            # 提取数据 - 对应 Node.js line 390-408
            issue = draw_data.get('issue', f'{index + 1}')
            draw_code = draw_data.get('draw_code', '')
            special_number = draw_data.get('special_number')
            bao = draw_data.get('draw_number', '-')  # 番数

            # 计算大小单双
            size_type = '-'
            parity_type = '-'
            if special_number is not None and special_number != '-':
                num = int(special_number) if isinstance(special_number, (int, str)) else 0
                size_type = '大' if num > 24 else '小'
                parity_type = '单' if num % 2 == 1 else '双'

            # 数据数组 - 对应 Node.js line 416
            data = [
                str(issue),
                str(draw_code),
                str(special_number) if special_number is not None else '-',
                str(bao),
                size_type,
                parity_type
            ]

            # 绘制文字 - 对应 Node.js line 420-425
            # Node.js: ctx.fillText(text, colX[i] + colWidths[i] / 2, rowY + rowHeight / 2 + 5);
            for i, text in enumerate(data):
                text_x = col_x[i] + col_widths[i] // 2
                text_y = row_y + self.row_height // 2 + 5  # 对应Node.js

                # 居中绘制
                bbox = draw_ctx.textbbox((0, 0), text, font=self.font)
                text_width = bbox[2] - bbox[0]
                draw_ctx.text(
                    (text_x - text_width // 2, text_y),
                    text,
                    fill='#000000',
                    font=self.font
                )

        # ==================== 底部时间 ====================
        # 对应 Node.js line 428-432
        footer_text = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        bbox = draw_ctx.textbbox((0, 0), footer_text, font=self.footer_font)
        text_width = bbox[2] - bbox[0]
        draw_ctx.text(
            (self.width // 2 - text_width // 2, height - 25),
            footer_text,
            fill='#999999',
            font=self.footer_font
        )

        # 保存图片 - 对应 Node.js line 240-248
        if not save_path:
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
