"""
自動生成 Rich Menu 圖片 - 三層設計（現代商業風格）
使用 PIL 創建帶有城市名稱的選單圖片
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import colorsys


def draw_rounded_rectangle(draw, coords, radius, fill):
    """繪製圓角矩形"""
    x1, y1, x2, y2 = coords
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + radius * 2, y1 +
                  radius * 2], 180, 270, fill=fill)
    draw.pieslice([x2 - radius * 2, y1, x2, y1 +
                  radius * 2], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2],
                  90, 180, fill=fill)
    draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)


def create_gradient_vertical(width, height, color_start, color_end):
    """創建垂直漸變"""
    base = Image.new('RGB', (width, height), color_start)
    top = Image.new('RGB', (width, height), color_end)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base


def create_rich_menu_image(region_name="北部"):
    """生成 Rich Menu 圖片 - 現代商業風格"""

    # 圖片尺寸
    width = 2500
    height = 1686

    # 三層高度配置
    top_height = 400      # 上層：功能選單
    middle_height = 886   # 中層：城市按鈕
    bottom_height = 400   # 下層：地區切換

    # 定義地區和城市 - 專業配色方案
    regions_data = {
        "北部": (["臺北市", "新北市", "基隆市", "桃園市", "新竹市", "新竹縣"], "#1976D2", "#2196F3"),
        "中部": (["臺中市", "苗栗縣", "彰化縣", "南投縣", "雲林縣"], "#388E3C", "#4CAF50"),
        "南部": (["臺南市", "高雄市", "嘉義市", "嘉義縣", "屏東縣"], "#F57C00", "#FF9800"),
        "東部": (["宜蘭縣", "花蓮縣", "臺東縣"], "#0097A7", "#00BCD4"),
        "離島": (["澎湖縣", "金門縣", "連江縣"], "#7B1FA2", "#9C27B0")
    }

    cities, dark_color, light_color = regions_data.get(
        region_name, regions_data["北部"])

    # 創建漸變背景
    img = create_gradient_vertical(width, height, "#FAFAFA", "#F0F0F0")
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/msjhbd.ttc", 75)
        font_large = ImageFont.truetype("C:/Windows/Fonts/msjhbd.ttc", 95)
        font_medium = ImageFont.truetype("C:/Windows/Fonts/msjhbd.ttc", 58)
        font_small = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 38)
    except:
        print("⚠️  未找到微軟正黑體")
        font_title = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # === 上層：功能選單（高度 400px）- 漸變卡片設計 ===
    function_width = width // 2
    functions = [
        ("天氣查詢", dark_color, light_color),
        ("更多功能", "#616161", "#757575")
    ]

    margin = 20
    card_padding = 15

    for idx, (name, color_dark, color_light) in enumerate(functions):
        x = idx * function_width

        # 創建漸變背景卡片
        card_gradient = create_gradient_vertical(
            function_width - margin * 2,
            top_height - margin * 2,
            color_dark,
            color_light
        )
        img.paste(card_gradient, (x + margin, margin))

        # 添加微妙的內陰影效果（用半透明黑色邊框）
        draw.rectangle(
            [x + margin, margin, x + function_width - margin, top_height - margin],
            outline='#00000020',
            width=2
        )

        # 主標題
        bbox = draw.textbbox((0, 0), name, font=font_title)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (function_width - text_width) // 2
        text_y = (top_height - text_height) // 2 - 20

        # 文字陰影效果
        draw.text((text_x + 2, text_y + 2), name,
                  fill='#00000040', font=font_title)
        draw.text((text_x, text_y), name, fill='white', font=font_title)

        # 副標題
        if idx == 1:  # 更多功能
            subtitle = "Coming Soon"
            bbox_sub = draw.textbbox((0, 0), subtitle, font=font_small)
            sub_width = bbox_sub[2] - bbox_sub[0]
            sub_x = x + (function_width - sub_width) // 2
            draw.text((sub_x, text_y + 95), subtitle,
                      fill='#FFFFFFAA', font=font_small)

    # === 中層：城市按鈕（高度 886px）- 卡片式設計 ===
    max_cols = 3
    max_rows = 2
    city_width = width // max_cols
    city_height = middle_height // max_rows
    card_margin = 25

    # 計算主題色的 RGB
    rgb = tuple(int(dark_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)

    for idx, city in enumerate(cities[:6]):
        col = idx % max_cols
        row = idx // max_cols

        x = col * city_width
        y = top_height + (row * city_height)

        # 每個城市用不同的亮度（創造層次）
        brightness = 0.50 + (idx % 3) * 0.08
        l_adjusted = min(brightness, 0.75)
        r, g, b = colorsys.hls_to_rgb(h, l_adjusted, s)
        city_color_dark = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

        # 稍亮的顏色作為漸變終點
        l_light = min(l_adjusted + 0.12, 0.85)
        r2, g2, b2 = colorsys.hls_to_rgb(h, l_light, s)
        city_color_light = f"#{int(r2*255):02x}{int(g2*255):02x}{int(b2*255):02x}"

        # 創建城市卡片的漸變背景
        city_gradient = create_gradient_vertical(
            city_width - card_margin * 2,
            city_height - card_margin * 2,
            city_color_dark,
            city_color_light
        )
        img.paste(city_gradient, (x + card_margin, y + card_margin))

        # 添加細微邊框
        draw.rectangle(
            [x + card_margin, y + card_margin,
             x + city_width - card_margin, y + city_height - card_margin],
            outline='#FFFFFF40',
            width=3
        )

        # 城市名稱（帶陰影）
        city_short = city.replace('市', '').replace('縣', '')
        bbox = draw.textbbox((0, 0), city_short, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (city_width - text_width) // 2
        text_y = y + (city_height - text_height) // 2 - 10

        # 文字陰影
        draw.text((text_x + 3, text_y + 3), city_short,
                  fill='#00000050', font=font_large)
        draw.text((text_x, text_y), city_short, fill='white', font=font_large)

    # === 下層：地區切換（高度 400px）- 現代標籤設計 ===
    region_names = ["北部", "中部", "南部", "東部", "離島"]
    region_colors = [
        ("#1976D2", "#2196F3"),
        ("#388E3C", "#4CAF50"),
        ("#F57C00", "#FF9800"),
        ("#0097A7", "#00BCD4"),
        ("#7B1FA2", "#9C27B0")
    ]
    region_width = width // 5
    tab_margin = 18

    for idx, (name, colors) in enumerate(zip(region_names, region_colors)):
        x = idx * region_width
        y = top_height + middle_height

        if name == region_name:
            # 選中的地區 - 使用漸變色
            color_dark, color_light = colors
            tab_gradient = create_gradient_vertical(
                region_width - tab_margin * 2,
                bottom_height - tab_margin * 2,
                color_dark,
                color_light
            )
            img.paste(tab_gradient, (x + tab_margin, y + tab_margin))

            # 頂部高亮條
            draw.rectangle(
                [x + tab_margin + 10, y + tab_margin,
                 x + region_width - tab_margin - 10, y + tab_margin + 8],
                fill='#FFFFFF90'
            )

            text_color = 'white'
            font_weight = font_medium

            # 添加邊框
            draw.rectangle(
                [x + tab_margin, y + tab_margin,
                 x + region_width - tab_margin, y + bottom_height - tab_margin],
                outline='#FFFFFF60',
                width=3
            )
        else:
            # 未選中的地區 - 淺色背景
            draw.rectangle(
                [x + tab_margin, y + tab_margin,
                 x + region_width - tab_margin, y + bottom_height - tab_margin],
                fill='#E8E8E8',
                outline='#D0D0D0',
                width=2
            )
            text_color = '#757575'
            font_weight = font_medium

        # 地區名稱
        bbox = draw.textbbox((0, 0), name, font=font_weight)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (region_width - text_width) // 2
        text_y = y + (bottom_height - text_height) // 2

        if name == region_name:
            # 選中的地區文字加陰影
            draw.text((text_x + 2, text_y + 2), name,
                      fill='#00000040', font=font_weight)

        draw.text((text_x, text_y), name, fill=text_color, font=font_weight)

    # 保存圖片
    output_path = f"rich_menu_{region_name}.png"
    img.save(output_path, "PNG")
    print(f"✅ Rich Menu 圖片已生成: {output_path}")
    print(f"   地區: {region_name}")
    print(f"   尺寸: {width}x{height}")
    print(f"\n高度配置：")
    print(f"   上層功能: {top_height}px")
    print(f"   中層城市: {middle_height}px")
    print(f"   下層地區: {bottom_height}px")
    return output_path


if __name__ == '__main__':
    import sys

    region = sys.argv[1] if len(sys.argv) > 1 else "北部"

    if region == "all":
        # 生成所有地區的圖片
        for region_name in ["北部", "中部", "南部", "東部", "離島"]:
            print(f"\n生成 {region_name} 圖片...")
            create_rich_menu_image(region_name)
    else:
        create_rich_menu_image(region)
