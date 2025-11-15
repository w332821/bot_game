# 图片显示问题修复总结

## 问题描述

用户反馈图片生成有以下问题：
1. **表头第一行没有任何数据** - 表头文字显示为空白或乱码
2. **第五、第六列（大小、单双）没有任何数据** - 显示为乱码占位符
3. **第二列内容跑到别的列** - 开奖号码列宽度太小，内容溢出

## 根本原因分析

### 1. 中文字体缺失
**最关键的问题**：PIL默认字体`ImageFont.load_default()`不支持中文字符！
- 表头："期号"、"开奖号码"、"特码"、"宝"、"大小"、"单双" 无法显示
- 数据："大"、"小"、"单"、"双" 无法显示
- 结果：这些位置显示为空白或乱码方块

### 2. 列宽设置不合理
```python
# 原来的设置
col_widths = [120, 150, 100, 100, 100, 100]  # 第二列只有150px

# 问题：开奖号码如 "01,02,03,04,05,06,07,08" 长度约240px
# 导致内容溢出到其他列
```

### 3. 文字垂直位置计算错误
```python
# 原来的代码
text_y = 10 + self.header_height // 2 - 8  # 表头
text_y = row_y + self.row_height // 2 - 8  # 数据行

# Node.js正确的计算方式
text_y = 30 + 8  # 表头固定位置
text_y = rowY + rowHeight / 2 + 5  # 数据行
```

## 修复内容

### 修改1：增加开奖号码列宽度
`utils/draw_image_generator.py:102`
```python
# 修改前
col_widths = [120, 150, 100, 100, 100, 100]

# 修改后
col_widths = [100, 350, 100, 100, 100, 100]
#             期号↑ 开奖号码↑
```

### 修改2：修正图片高度计算
`utils/draw_image_generator.py:111`
```python
# 修改前
height = self.header_height + self.row_height * rows + 40 + 10

# 修改后（对应Node.js line 326）
height = self.header_height + self.row_height * (rows + 1) + 40
```

### 修改3：修正文字垂直位置
`utils/draw_image_generator.py:137, 196`
```python
# 表头文字位置（对应Node.js line 364）
text_y = 30 + 8  # 固定位置，而不是动态计算

# 数据行文字位置（对应Node.js line 424）
text_y = row_y + self.row_height // 2 + 5  # +5而不是-8
```

### 修改4：增强字体加载
`utils/draw_image_generator.py:58-76`
```python
# 增加更多macOS和Linux字体路径
font_paths = [
    "/System/Library/Fonts/PingFang.ttc",  # macOS
    "/System/Library/Fonts/STHeiti Light.ttc",  # macOS 黑体
    "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux Noto
    "C:\\Windows\\Fonts\\msyh.ttc",  # Windows
    "C:\\Windows\\Fonts\\simhei.ttf",  # Windows
]
```

### 修改5：增大字体大小
`utils/draw_image_generator.py:40-42`
```python
# 修改前
self.font = self._load_font(14)
self.header_font = self._load_font(15, bold=True)

# 修改后
self.font = self._load_font(16)  # 增大2px
self.header_font = self._load_font(18, bold=True)  # 增大3px
```

## 预期效果

修复后的表格应该：
1. ✅ 表头完整显示：期号 | 开奖号码 | 特码 | 宝 | 大小 | 单双
2. ✅ 开奖号码列宽度足够，不溢出
3. ✅ "大小单双"列正确显示中文
4. ✅ 所有文字垂直居中对齐
5. ✅ 字体清晰可读

## 表格布局

```
┌──────────┬────────────────────────────┬─────────┬─────────┬─────────┬─────────┐
│   期号   │        开奖号码            │  特码   │   宝    │  大小   │  单双   │
│  (100px) │        (350px)             │ (100px) │ (100px) │ (100px) │ (100px) │
├──────────┼────────────────────────────┼─────────┼─────────┼─────────┼─────────┤
│20250115  │ 01,02,03,04,05,06,07,08    │   28    │    5    │   大    │   双    │
├──────────┼────────────────────────────┼─────────┼─────────┼─────────┼─────────┤
│20250115  │ 10,11,12,13,14,15,16,17    │   15    │    3    │   小    │   单    │
└──────────┴────────────────────────────┴─────────┴─────────┴─────────┴─────────┘
```

## 测试

运行测试脚本生成示例图片：
```bash
python test_image_gen.py
open /tmp/test_lucky8.png
```

## 注意事项

⚠️ **字体依赖**：
- macOS：自带PingFang字体，应该能正常显示
- Linux服务器：需要安装中文字体包
  ```bash
  # Ubuntu/Debian
  sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei

  # CentOS/RHEL
  sudo yum install wqy-microhei-fonts wqy-zenhei-fonts
  ```
- 如果没有中文字体，表头和中文字段将显示为方块或空白

## 对应Node.js代码

所有修改都严格参考`game-bot-master/draw-image.js`：
- Line 312-320: 列宽定义
- Line 322-326: 图片高度计算
- Line 336-339: 列位置计算
- Line 364: 表头文字Y坐标
- Line 424: 数据行文字Y坐标
