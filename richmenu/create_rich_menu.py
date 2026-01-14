"""
建立 LINE Rich Menu - 天氣查詢選單
將 22 個縣市按地區分類顯示
"""
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    RichMenuRequest,
    RichMenuSize,
    RichMenuArea,
    RichMenuBounds,
    MessageAction,
    URIAction,
    RichMenuSwitchAction
)
from dotenv import load_dotenv
import os
import requests

load_dotenv()

configuration = Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))


def create_weather_rich_menu_for_region(region_name, cities, region_idx=0):
    """建立特定地區的 Rich Menu - 三層設計"""

    # 高度配置：上層小、中層大、下層小
    top_height = 400      # 上層：功能選單
    middle_height = 886   # 中層：城市按鈕（主要區域）
    bottom_height = 400   # 下層：地區切換

    # Rich Menu 基本設定
    rich_menu = RichMenuRequest(
        size=RichMenuSize(width=2500, height=1686),
        selected=False,  # 不自動選中，由程式控制
        name=f"天氣選單-{region_name}",
        chat_bar_text="選單",
        areas=[]
    )

    # === 上層：功能選單（高度 400px）===
    function_width = 2500 // 2  # 2個功能按鈕

    # 功能1：天氣查詢
    rich_menu.areas.append(RichMenuArea(
        bounds=RichMenuBounds(
            x=0, y=0, width=function_width, height=top_height),
        action=MessageAction(
            text=f"📍 當前地區：{region_name}\n點擊下方城市查詢天氣",
            label="天氣查詢"
        )
    ))

    # 功能2：更多功能
    rich_menu.areas.append(RichMenuArea(
        bounds=RichMenuBounds(x=function_width, y=0,
                              width=function_width, height=top_height),
        action=MessageAction(
            text="✨ 更多功能即將推出！\n敬請期待",
            label="更多功能"
        )
    ))

    # === 中層：城市按鈕（高度 886px，主要區域）===
    # 計算城市按鈕佈局（最多6個城市，2行3列）
    max_cols = 3
    max_rows = 2
    city_width = 2500 // max_cols   # 約 833px
    city_height = middle_height // max_rows  # 約 443px

    for idx, city in enumerate(cities):
        col = idx % max_cols
        row = idx // max_cols

        if row >= max_rows:  # 最多顯示6個城市
            break

        x = col * city_width
        y = top_height + (row * city_height)

        city_short = city.replace('市', '').replace('縣', '')

        rich_menu.areas.append(RichMenuArea(
            bounds=RichMenuBounds(
                x=x, y=y, width=city_width, height=city_height),
            action=MessageAction(
                text=f"天氣 {city}",
                label=city_short
            )
        ))

    # === 下層：地區切換（高度 400px）===
    regions_data = [
        ("北部", 0, "north"),
        ("中部", 1, "central"),
        ("南部", 2, "south"),
        ("東部", 3, "east"),
        ("離島", 4, "islands")
    ]

    region_width = 2500 // 5  # 500px

    for idx, (name, _, alias) in enumerate(regions_data):
        x = idx * region_width
        y = top_height + middle_height

        # 使用 RichMenuSwitchAction 直接切換 Rich Menu
        rich_menu.areas.append(RichMenuArea(
            bounds=RichMenuBounds(
                x=x, y=y, width=region_width, height=bottom_height),
            action=RichMenuSwitchAction(
                rich_menu_alias_id=alias,
                data=f"region={name}"
            )
        ))

    return rich_menu


def create_all_region_menus():
    """創建所有地區的 Rich Menu"""

    regions = [
        ("北部", ["臺北市", "新北市", "基隆市", "桃園市", "新竹市", "新竹縣"]),
        ("中部", ["臺中市", "苗栗縣", "彰化縣", "南投縣", "雲林縣"]),
        ("南部", ["臺南市", "高雄市", "嘉義市", "嘉義縣", "屏東縣"]),
        ("東部", ["宜蘭縣", "花蓮縣", "臺東縣"]),
        ("離島", ["澎湖縣", "金門縣", "連江縣"])
    ]

    menu_ids = {}

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        for idx, (region_name, cities) in enumerate(regions):
            try:
                rich_menu = create_weather_rich_menu_for_region(
                    region_name, cities, idx)
                response = line_bot_api.create_rich_menu(
                    rich_menu_request=rich_menu)
                menu_id = response.rich_menu_id
                menu_ids[region_name] = menu_id
                print(f"✅ {region_name} Rich Menu 創建成功: {menu_id}")
            except Exception as e:
                print(f"❌ {region_name} 創建失敗: {e}")

    return menu_ids


def create_weather_rich_menu():
    """建立預設的天氣查詢 Rich Menu（北部）"""

    # 預設創建北部地區的選單
    rich_menu = create_weather_rich_menu_for_region(
        "北部",
        ["臺北市", "新北市", "基隆市", "桃園市", "新竹市", "新竹縣"],
        0
    )

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        try:
            response = line_bot_api.create_rich_menu(
                rich_menu_request=rich_menu)
            rich_menu_id = response.rich_menu_id
            print(f"✅ Rich Menu 創建成功！")
            print(f"Rich Menu ID: {rich_menu_id}")

            return rich_menu_id

        except Exception as e:
            print(f"❌ 創建失敗: {e}")
            return None


def upload_rich_menu_image(rich_menu_id, image_path):
    """上傳 Rich Menu 圖片"""

    url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"
    headers = {
        "Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}",
        "Content-Type": "image/png"
    }

    try:
        with open(image_path, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
            response.raise_for_status()
            print(f"✅ 圖片上傳成功！")
            return True
    except Exception as e:
        print(f"❌ 圖片上傳失敗: {e}")
        return False


def set_default_rich_menu(rich_menu_id):
    """設定為預設 Rich Menu"""

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        try:
            line_bot_api.set_default_rich_menu(rich_menu_id=rich_menu_id)
            print(f"✅ 已設定為預設選單！")
            return True
        except Exception as e:
            print(f"❌ 設定失敗: {e}")
            return False


def list_rich_menus():
    """列出所有 Rich Menu"""

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        try:
            response = line_bot_api.get_rich_menu_list()
            print("\n📋 現有的 Rich Menu：")
            for menu in response.richmenus:
                print(f"  - ID: {menu.rich_menu_id}")
                print(f"    名稱: {menu.name}")
                print(f"    選中: {menu.selected}")
                print()
            return response.richmenus
        except Exception as e:
            print(f"❌ 取得列表失敗: {e}")
            return []


def delete_rich_menu(rich_menu_id):
    """刪除 Rich Menu"""

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        try:
            line_bot_api.delete_rich_menu(rich_menu_id=rich_menu_id)
            print(f"✅ Rich Menu {rich_menu_id} 已刪除")
            return True
        except Exception as e:
            print(f"❌ 刪除失敗: {e}")
            return False


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'list':
            # 列出所有選單
            list_rich_menus()

        elif command == 'delete' and len(sys.argv) > 2:
            # 刪除指定選單
            menu_id = sys.argv[2]
            delete_rich_menu(menu_id)

        elif command == 'create':
            # 創建新選單
            menu_id = create_weather_rich_menu()
            if menu_id:
                print("\n⚠️  接下來請：")
                print("1. 執行: python generate_rich_menu_image.py 北部")
                print("2. 執行: python create_rich_menu.py upload {menu_id}")

        elif command == 'create-all':
            # 創建所有地區選單
            print("🚀 創建所有地區的 Rich Menu...")
            menu_ids = create_all_region_menus()

            if menu_ids:
                print("\n" + "="*50)
                print("✅ 所有選單創建完成！")
                print("="*50)
                for region, menu_id in menu_ids.items():
                    print(f"{region}: {menu_id}")
                print("\n請為每個選單上傳對應圖片：")
                for region, menu_id in menu_ids.items():
                    print(
                        f"  python create_rich_menu.py upload {menu_id} rich_menu_{region}.png")

        elif command == 'upload' and len(sys.argv) > 2:
            # 上傳圖片
            menu_id = sys.argv[2]
            image_path = sys.argv[3] if len(
                sys.argv) > 3 else "rich_menu_image.png"

            if upload_rich_menu_image(menu_id, image_path):
                # 設定為預設選單
                set_default_rich_menu(menu_id)

        else:
            print("使用方式：")
            print("  python create_rich_menu.py create              # 創建單一選單（北部）")
            print("  python create_rich_menu.py create-all          # 創建所有地區選單")
            print("  python create_rich_menu.py list                # 列出所有選單")
            print("  python create_rich_menu.py delete <menu_id>    # 刪除選單")
            print(
                "  python create_rich_menu.py upload <menu_id> [image_path]  # 上傳圖片")
    else:
        # 預設執行：創建選單
        print("🚀 開始建立 Rich Menu...")
        menu_id = create_weather_rich_menu()

        if menu_id:
            print("\n" + "="*50)
            print("📝 下一步：準備 Rich Menu 圖片")
            print("="*50)
            print("\n圖片規格：")
            print("  - 尺寸: 2500 x 1686 像素")
            print("  - 格式: PNG 或 JPG")
            print("  - 大小: 小於 1MB")
            print("\n區域劃分（從上到下）：")
            print("  第1列 (0-337px): 北部 - 臺北市、新北市、基隆市、桃園市、新竹市、新竹縣")
            print("  第2列 (337-674px): 中部 - 臺中市、苗栗縣、彰化縣、南投縣、雲林縣")
            print("  第3列 (674-1011px): 南部 - 臺南市、高雄市、嘉義市、嘉義縣、屏東縣")
            print("  第4列 (1011-1348px): 東部 - 宜蘭縣、花蓮縣、臺東縣")
            print("  第5列 (1348-1686px): 離島 - 澎湖縣、金門縣、連江縣")
            print("\n圖片準備好後，執行：")
            print(
                f"  python create_rich_menu.py upload {menu_id} rich_menu_image.png")
