# LINE Weather Bot

使用 Python Flask + UV + Docker Compose 建立的 LINE 天氣查詢 Bot

## 功能

- 輸入台灣縣市名稱，查詢 36 小時天氣預報
- 包含天氣現象、溫度範圍、降雨機率、舒適度等資訊
- 使用中央氣象署開放資料 API

## 架構

```
line_webhook/
├── app.py                 # Flask 主應用程式 (webhook endpoint)
├── weather_service.py     # 天氣查詢服務
├── requirements.txt       # Python 套件依賴
├── pyproject.toml         # UV 專案配置
├── Dockerfile             # Docker 映像檔設定
├── docker-compose.yml     # Docker Compose 配置
├── .env.example           # 環境變數範例
├── .gitignore            # Git 忽略檔案
└── note.md               # 專案筆記
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

- `POST /callback` - LINE webhook endpoint
- `GET /health` - 健康檢查

## 使用範例

在 LINE Bot 中輸入台灣縣市名稱即可查詢 36 小時天氣預報：
- `台北` 或 `臺北` 或 `台北市`
- `高雄`
- `台中`
- `新北`

支援所有台灣縣市（共 22 個縣市）

## 注意事項

- 需要有公開的 HTTPS URL 才能設定 LINE Webhook
- 可使用 ngrok 進行本地測試
- 中央氣象署 API 有呼叫次數限制，請注意用量
- 僅支援台灣 22 個縣市的天氣預報

## License

MIT
