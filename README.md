# LINE Weather Bot

使用 Python Flask + UV + Docker Compose 建立的 LINE 天氣查詢 Bot

## 功能

- 輸入台灣縣市名稱，查詢 36 小時天氣預報
- 包含天氣現象、溫度範圍、降雨機率、舒適度等資訊
- 使用中央氣象署開放資料 API

## 架構

```
line_webhook/
├── app.py                      # Flask 主應用程式 (webhook)
├── weather_service.py          # 天氣查詢服務 (Flex Message)
├── admin_app.py                # Rich Menu 管理後台 (port 5001)
├── richmenu/                   # Rich Menu 相關檔案
│   ├── generate_rich_menu_image.py  # 自動生成選單圖片
│   ├── create_rich_menu.py          # 建立選單結構
│   ├── rich_menu_alias.py           # Alias 管理
│   ├── clean_richmenus.py           # 清理工具
│   └── *.png                        # 選單圖片 (5個區域)
├── templates/
│   └── richmenu_manager.html   # 管理介面前端
├── requirements.txt            # Python 套件依賴
├── pyproject.toml              # UV 專案配置
├── Dockerfile                  # Docker 映像檔設定
├── docker-compose.yml          # Docker Compose 配置
├── RICHMENU_GUIDE.md          # Rich Menu 架構說明
├── .env.example                # 環境變數範例
└── .gitignore                 # Git 忽略檔案
```

## 環境設定

1. 複製環境變數範例檔案並填入實際值：
```bash
cp .env.example .env
```

2. 編輯 `.env` 檔案，填入以下資訊：
   - `LINE_CHANNEL_ACCESS_TOKEN`: LINE Bot 的 Channel Access Token
   - `LINE_CHANNEL_SECRET`: LINE Bot 的 Channel Secret
   - `CWA_API_KEY`: 中央氣象署 API 授權碼 (至 https://opendata.cwa.gov.tw/ 註冊取得)

## 使用 UV 本地開發

```bash
# 安裝 uv (如果還沒安裝)
pip install uv

# 安裝依賴
uv pip install -r requirements.txt

# 執行應用
python app.py
```

## 使用 Docker Compose

```bash
# 建置並啟動容器
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止容器
docker-compose down
```

## LINE Bot 設定

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 建立新的 Messaging API Channel
3. 取得 Channel Secret 和 Channel Access Token
4. 設定 Webhook URL: `https://your-domain.com/callback`
5. 啟用 Webhook

## API 端點

### Webhook 服務 (port 5000)
- `POST /callback` - LINE webhook endpoint
- `GET /health` - 健康檢查

### 管理後台 (port 5001)
- `GET /` - Rich Menu 管理介面
- `GET /api/richmenus` - 取得所有選單
- `GET /api/richmenu/<id>/image` - 取得選單圖片
- `GET /api/richmenu/default` - 取得預設選單
- `POST /api/richmenu/default` - 設定預設選單
- `DELETE /api/richmenu/<id>` - 刪除選單
- `GET /api/aliases` - 取得所有別名

啟動管理介面：
```bash
python admin_app.py
# 訪問 http://localhost:5001
```

## 使用範例

### 天氣查詢
在 LINE Bot 中點選 Rich Menu 的城市按鈕，或直接輸入：
- `天氣 台北市`
- `天氣 高雄市`
- `天氣 台中市`

### Rich Menu
- 點擊下方區域標籤（北部/中部/南部/東部/離島）自動切換城市列表
- 點擊城市按鈕直接查詢該城市天氣
- 使用管理介面查看、設定、刪除選單

支援所有台灣縣市（共 22 個縣市）

詳細的 Rich Menu 架構說明請參閱 [RICHMENU_GUIDE.md](RICHMENU_GUIDE.md)

## 注意事項

- 需要有公開的 HTTPS URL 才能設定 LINE Webhook
- 可使用 ngrok 進行本地測試
- 中央氣象署 API 有呼叫次數限制，請注意用量
- 僅支援台灣 22 個縣市的天氣預報

## License

MIT
