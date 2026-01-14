# LINE Rich Menu 架構說明

## 📋 整體架構

```
Rich Menu 系統
├── 5 個區域選單 (北部/中部/南部/東部/離島)
├── Alias 別名系統 (north/central/south/east/islands)
└── 預設選單 (北部)
```

## 🎯 控管方式

### 1. **Rich Menu 建立流程**
```
生成圖片 → 建立選單結構 → 上傳圖片 → 設定 Alias → 設定預設選單
```

### 2. **選單 ID 管理**
- 每個選單有唯一的 `richmenu-xxxxx` ID
- 當前選單 ID 記錄在 `rich_menu_alias.py` 的 `MENU_IDS` 字典中

```python
MENU_IDS = {
    "北部": "richmenu-c262e84690c251a6a8d7fed817314119",
    "中部": "richmenu-09e88c958242dd5736588cca9d8aa0c4",
    "南部": "richmenu-4de81b2bdbe28c209b43463a6f15d07c",
    "東部": "richmenu-e13c76d694211d5ad8ae544270689ed8",
    "離島": "richmenu-16005f550755820b0f4e74ee4cb19924"
}
```

### 3. **Alias 別名系統**
- 使用簡短的英文別名來切換選單
- 好處：ID 固定不變，即使重新創建選單也不用改程式碼

```python
別名對應:
north → 北部
central → 中部
south → 南部
east → 東部
islands → 離島
```

### 4. **選單切換機制**
使用 `RichMenuSwitchAction` 實現直接點擊切換：
```python
RichMenuSwitchAction(
    rich_menu_alias_id="north",  # 使用 alias 而非 menu ID
    data="switch_to_north"
)
```

## 🔑 重要 API 列表

### 建立與管理

| API 方法 | 用途 | 範例 |
|---------|------|-----|
| `create_rich_menu()` | 建立 Rich Menu 結構 | `line_api.create_rich_menu(rich_menu_request)` |
| `set_rich_menu_image()` | 上傳選單圖片 | `line_api.set_rich_menu_image(menu_id, image_file)` |
| `get_rich_menu_list()` | 取得所有選單列表 | `line_api.get_rich_menu_list()` |
| `get_rich_menu()` | 取得單一選單詳細資訊 | `line_api.get_rich_menu(menu_id)` |
| `delete_rich_menu()` | 刪除選單 | `line_api.delete_rich_menu(menu_id)` |

### Alias 別名管理

| API 方法 | 用途 | 範例 |
|---------|------|-----|
| `create_rich_menu_alias()` | 建立別名 | `line_api.create_rich_menu_alias(alias_request)` |
| `get_rich_menu_alias_list()` | 取得所有別名 | `line_api.get_rich_menu_alias_list()` |
| `delete_rich_menu_alias()` | 刪除別名 | `line_api.delete_rich_menu_alias(alias_id)` |

### 預設選單

| API 方法 | 用途 | 範例 |
|---------|------|-----|
| `set_default_rich_menu()` | 設定預設選單 | `line_api.set_default_rich_menu(menu_id)` |
| `get_default_rich_menu_id()` | 取得預設選單 ID | `line_api.get_default_rich_menu_id()` |
| `cancel_default_rich_menu()` | 取消預設選單 | `line_api.cancel_default_rich_menu()` |

### 用戶選單管理

| API 方法 | 用途 | 範例 |
|---------|------|-----|
| `link_rich_menu_id_to_user()` | 綁定選單給特定用戶 | `line_api.link_rich_menu_id_to_user(user_id, menu_id)` |
| `get_rich_menu_id_of_user()` | 取得用戶當前選單 | `line_api.get_rich_menu_id_of_user(user_id)` |
| `unlink_rich_menu_id_from_user()` | 解除用戶選單綁定 | `line_api.unlink_rich_menu_id_from_user(user_id)` |

### 圖片下載

| API 方法 | 用途 | 範例 |
|---------|------|-----|
| `download_rich_menu_image()` | 下載選單圖片 | `line_api.download_rich_menu_image(menu_id)` |

## 📐 選單設計規格

### 圖片尺寸
- **總大小**: 2500 x 1686 px
- **分層設計**:
  - 上層功能區: 2500 x 400 px (2 個功能按鈕)
  - 中層城市區: 2500 x 886 px (3x2 城市網格)
  - 下層區域切換: 2500 x 400 px (5 個區域標籤)

### 點擊區域 (bounds)
```python
{
    "x": 0,        # 左上角 X 座標
    "y": 0,        # 左上角 Y 座標
    "width": 833,  # 寬度
    "height": 400  # 高度
}
```

### Action 類型
1. **MessageAction**: 發送訊息 `"天氣 台北市"`
2. **RichMenuSwitchAction**: 切換選單 (使用 alias)
3. **URIAction**: 開啟網址
4. **PostbackAction**: 回傳資料

## 🗂️ 核心檔案說明

| 檔案 | 用途 |
|-----|------|
| `richmenu/generate_rich_menu_image.py` | 自動生成選單圖片 |
| `richmenu/create_rich_menu.py` | 建立選單結構與上傳 |
| `richmenu/rich_menu_alias.py` | Alias 管理與 ID 記錄 |
| `richmenu/clean_richmenus.py` | 清理重複選單工具 |
| `admin_app.py` | Web 管理介面後端 (port 5001) |
| `templates/richmenu_manager.html` | Web 管理介面前端 |

## 🔄 完整建立流程範例

```bash
# 1. 生成圖片 (5張)
cd richmenu
python generate_rich_menu_image.py

# 2. 建立別名
python rich_menu_alias.py create

# 3. 建立選單結構並上傳
python create_rich_menu.py

# 4. 設定預設選單 (北部) - 在專案根目錄執行
cd ..
python -c "from linebot.v3.messaging import Configuration, ApiClient, MessagingApi; import os; from dotenv import load_dotenv; load_dotenv(); config = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')); api_client = ApiClient(config); line_api = MessagingApi(api_client); line_api.set_default_rich_menu('richmenu-c262e84690c251a6a8d7fed817314119'); print('✅ 已設定北部為預設選單'); api_client.close()"
```

## 🎨 設計特色

- **Material Design** 配色
- **漸層背景**: 垂直漸層 (#FAFAFA → #F0F0F0)
- **文字陰影**: 提升可讀性
- **圓角卡片**: 現代商業風格
- **選中指示**: 白色底部指示條
- **顏色區分**: 每個城市使用不同亮度

## 🚀 管理介面使用

啟動管理介面:
```bash
python admin_app.py
```

訪問: http://localhost:5001

功能:
- ✅ 查看所有 Rich Menu
- ✅ 預覽選單圖片
- ✅ 設定/取消預設選單
- ✅ 刪除選單
- ✅ 查看 Alias 列表

## 💡 最佳實踐

1. **使用 Alias**: 永遠透過 alias 而非 menu ID 來切換選單
2. **保留圖片**: 生成的 PNG 檔案留存以便後續修改
3. **定期清理**: 使用 `clean_richmenus.py` 清理重複選單
4. **測試切換**: 在 LINE App 中測試選單切換是否順暢
5. **記錄 ID**: 每次重建選單後更新 `MENU_IDS` 字典

## ⚠️ 注意事項

- Alias ID 必須是小寫英文字母、數字、底線、連字號
- Alias ID 長度限制：1-40 字元
- 一個 Rich Menu 只能對應一個 Alias
- 刪除 Rich Menu 前要先刪除對應的 Alias
- 圖片必須是 PNG 格式，大小限制 1MB
