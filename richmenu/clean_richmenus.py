"""
清理多餘的 Rich Menu
保留有圖片且在 alias 中的 5 個，刪除其他的
"""
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from dotenv import load_dotenv
import os

load_dotenv()

configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))

# 正確的 Rich Menu ID（從 rich_menu_alias.py）
KEEP_MENUS = {
    "北部": "richmenu-c262e84690c251a6a8d7fed817314119",
    "中部": "richmenu-09e88c958242dd5736588cca9d8aa0c4",
    "南部": "richmenu-4de81b2bdbe28c209b43463a6f15d07c",
    "東部": "richmenu-e13c76d694211d5ad8ae544270689ed8",
    "離島": "richmenu-16005f550755820b0f4e74ee4cb19924"
}

def clean_duplicate_menus():
    """清理重複的 Rich Menu"""
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 取得所有 Rich Menu
        response = line_bot_api.get_rich_menu_list()
        all_menus = response.richmenus
        
        print(f"📋 總共有 {len(all_menus)} 個 Rich Menu")
        print("="*60)
        
        keep_ids = set(KEEP_MENUS.values())
        deleted_count = 0
        
        for menu in all_menus:
            menu_id = menu.rich_menu_id
            
            if menu_id in keep_ids:
                # 找出對應的地區
                region = None
                for r, mid in KEEP_MENUS.items():
                    if mid == menu_id:
                        region = r
                        break
                
                print(f"✅ 保留: {menu.name} ({region})")
                print(f"   ID: {menu_id}")
            else:
                # 刪除
                try:
                    line_bot_api.delete_rich_menu(menu_id)
                    print(f"🗑️  刪除: {menu.name}")
                    print(f"   ID: {menu_id}")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ 刪除失敗: {menu_id} - {e}")
        
        print("="*60)
        print(f"\n✅ 清理完成！")
        print(f"   保留: {len(keep_ids)} 個")
        print(f"   刪除: {deleted_count} 個")
        print(f"   剩餘: {len(keep_ids)} 個")
        
        # 重新確認
        response = line_bot_api.get_rich_menu_list()
        print(f"\n📋 最終確認: 共 {len(response.richmenus)} 個 Rich Menu")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'confirm':
        clean_duplicate_menus()
    else:
        print("⚠️  此操作會刪除多餘的 Rich Menu！")
        print(f"\n將保留以下 5 個 Rich Menu:")
        for region, menu_id in KEEP_MENUS.items():
            print(f"  {region}: {menu_id}")
        print("\n其他的都會被刪除！")
        print("\n執行指令: python clean_richmenus.py confirm")
