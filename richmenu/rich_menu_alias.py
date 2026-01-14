"""
建立 Rich Menu Alias - 為每個 Rich Menu 創建簡短的 alias
這樣就可以使用 RichMenuSwitchAction 直接切換
"""
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    CreateRichMenuAliasRequest
)
from dotenv import load_dotenv
import os

load_dotenv()

configuration = Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))

# Rich Menu ID 映射
MENU_IDS = {
    "北部": "richmenu-c262e84690c251a6a8d7fed817314119",
    "中部": "richmenu-09e88c958242dd5736588cca9d8aa0c4",
    "南部": "richmenu-4de81b2bdbe28c209b43463a6f15d07c",
    "東部": "richmenu-e13c76d694211d5ad8ae544270689ed8",
    "離島": "richmenu-16005f550755820b0f4e74ee4cb19924"
}


def create_aliases():
    """為所有 Rich Menu 創建 alias"""

    # Alias ID 只能用小寫英文、數字、dash和underscore
    alias_mapping = {
        "北部": "north",
        "中部": "central",
        "南部": "south",
        "東部": "east",
        "離島": "islands"
    }

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        print("🏷️  開始創建 Rich Menu Alias...")
        print("="*60)

        for region, menu_id in MENU_IDS.items():
            alias_id = alias_mapping[region]

            try:
                # 先嘗試刪除現有的 alias
                try:
                    line_bot_api.delete_rich_menu_alias(alias_id)
                    print(f"🗑️  已刪除舊 alias: {alias_id}")
                except:
                    pass

                # 創建新的 alias
                alias_request = CreateRichMenuAliasRequest(
                    rich_menu_alias_id=alias_id,
                    rich_menu_id=menu_id
                )

                line_bot_api.create_rich_menu_alias(alias_request)
                print(f"✅ {region}: {alias_id} -> {menu_id}")

            except Exception as e:
                print(f"❌ {region} 創建失敗: {e}")

        print("="*60)
        print("\n✅ 所有 alias 創建完成！")
        print("\n現在可以使用以下 alias 進行切換：")
        for region in MENU_IDS.keys():
            print(f"  {alias_mapping[region]} ({region})")


def list_aliases():
    """列出所有 Rich Menu Alias"""

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        try:
            response = line_bot_api.get_rich_menu_alias_list()
            print("\n📋 現有的 Rich Menu Alias:")
            print("="*60)
            for alias in response.aliases:
                print(f"  {alias.rich_menu_alias_id} -> {alias.rich_menu_id}")
            print("="*60)
        except Exception as e:
            print(f"❌ 取得列表失敗: {e}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'create':
            create_aliases()
        elif sys.argv[1] == 'list':
            list_aliases()
    else:
        print("使用方式：")
        print("  python rich_menu_alias.py create  # 創建所有 alias")
        print("  python rich_menu_alias.py list    # 列出所有 alias")
