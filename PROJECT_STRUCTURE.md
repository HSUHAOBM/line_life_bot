# 專案結構總覽

## 📂 檔案組織

```
line_webhook/
├── 🚀 主要服務
│   ├── app.py                      # LINE Webhook 服務 (port 5000)
│   ├── weather_service.py          # 天氣查詢 & Flex Message 生成
│   └── admin_app.py                # Rich Menu 管理後台 (port 5001)
│
├── 🎨 Rich Menu 系統
│   └── richmenu/
│       ├── generate_rich_menu_image.py   # 圖片自動生成器
│       ├── create_rich_menu.py           # 選單結構建立與上傳
│       ├── rich_menu_alias.py            # Alias 管理 & Menu ID 記錄
│       ├── clean_richmenus.py            # 重複選單清理工具
│       ├── __init__.py                   # Python 模組初始化
│       └── rich_menu_*.png (5張)         # 各區域選單圖片
│
├── 🌐 前端模板
│   └── templates/
│       └── richmenu_manager.html   # 管理介面 HTML
│
├── 📄 文檔
│   ├── README.md                   # 專案主文檔
│   ├── RICHMENU_GUIDE.md          # Rich Menu 架構詳細說明
│   ├── PROJECT_STRUCTURE.md       # 本檔案 - 結構總覽
│   └── note.md                     # 開發筆記
│
├── 🐳 部署配置
│   ├── Dockerfile                  # Docker 映像檔
│   ├── docker-compose.yml          # Docker Compose 配置
│   └── requirements.txt            # Python 依賴套件
│
└── ⚙️ 專案配置
    ├── pyproject.toml              # UV 套件管理配置
    ├── .env                        # 環境變數 (不納入版控)
    ├── .env.example                # 環境變數範例
    ├── .gitignore                  # Git 忽略規則
    └── uv.lock                     # UV 鎖定檔
```

## 🔗 模組依賴關係

```
app.py
├── weather_service.py
│   └── requests (CWA API)
└── linebot.v3.messaging (LINE SDK)

admin_app.py
├── richmenu.rich_menu_alias (MENU_IDS)
├── linebot.v3.messaging (MessagingApi, MessagingApiBlob)
└── Flask (Web Framework)

richmenu/create_rich_menu.py
├── richmenu/generate_rich_menu_image.py (生成圖片)
└── linebot.v3.messaging (建立選單)

richmenu/rich_menu_alias.py
└── linebot.v3.messaging (Alias 管理)
```

## 🎯 核心功能模組

### 1. LINE Webhook 服務 (app.py)
- **功能**: 接收 LINE 訊息，處理天氣查詢
- **端口**: 5000
- **主要端點**:
  - `POST /callback` - LINE webhook
  - `GET /health` - 健康檢查
- **依賴**:
  - `weather_service.py` - 天氣資料與 Flex Message
  - LINE Bot SDK v3

### 2. 天氣服務 (weather_service.py)
- **功能**: 中央氣象署 API 整合，Flex Message 生成
- **核心類別**: `WeatherForecast`
- **支援**: 22 個台灣縣市，36 小時預報，3 個時段
- **輸出**: JSON 格式 Flex Message (漸層卡片設計)

### 3. Rich Menu 管理後台 (admin_app.py)
- **功能**: Web 介面管理 Rich Menu
- **端口**: 5001
- **主要功能**:
  - 查看所有 Rich Menu 列表
  - 預覽選單圖片 (本地/API)
  - 設定/取消預設選單
  - 刪除選單
  - 查看 Alias 列表

### 4. Rich Menu 圖片生成 (richmenu/generate_rich_menu_image.py)
- **功能**: 使用 PIL 自動生成 5 張選單圖片
- **規格**: 2500x1686px，3層設計 (400/886/400)
- **設計**: Material Design，漸層背景，文字陰影
- **輸出**: `rich_menu_北部.png` 等 5 張圖片

### 5. Rich Menu 建立 (richmenu/create_rich_menu.py)
- **功能**: 建立選單結構並上傳到 LINE
- **特色**: 使用 `RichMenuSwitchAction` 實現區域切換
- **流程**:
  1. 呼叫圖片生成器
  2. 建立 5 個區域的選單結構
  3. 上傳圖片到 LINE
  4. 記錄 Menu ID

### 6. Alias 管理 (richmenu/rich_menu_alias.py)
- **功能**: 為每個選單建立英文別名
- **別名映射**:
  - 北部 → `north`
  - 中部 → `central`
  - 南部 → `south`
  - 東部 → `east`
  - 離島 → `islands`
- **儲存**: `MENU_IDS` 字典記錄當前 Menu ID

### 7. 清理工具 (richmenu/clean_richmenus.py)
- **功能**: 清理重複的 Rich Menu
- **使用**: `python clean_richmenus.py confirm`
- **邏輯**: 保留 `MENU_IDS` 中的選單，刪除其他

## 🔄 完整工作流程

### 初次設定
```bash
# 1. 安裝依賴
uv pip install -r requirements.txt

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env 填入 LINE Token 和 CWA API Key

# 3. 生成 Rich Menu
cd richmenu
python generate_rich_menu_image.py  # 生成圖片
python rich_menu_alias.py create    # 建立 alias
python create_rich_menu.py           # 建立並上傳選單

# 4. 設定預設選單
cd ..
python -c "..."  # 見 RICHMENU_GUIDE.md

# 5. 啟動服務
python app.py          # Webhook (port 5000)
python admin_app.py    # 管理介面 (port 5001)
```

### 日常開發
```bash
# 啟動 Webhook
python app.py

# 啟動管理介面
python admin_app.py

# 使用 Docker
docker-compose up -d
```

### 更新 Rich Menu
```bash
cd richmenu
python generate_rich_menu_image.py  # 修改設計後重新生成
python create_rich_menu.py           # 重新上傳
python clean_richmenus.py confirm    # 清理舊選單
```

## 📊 資料流向

### 天氣查詢流程
```
LINE User
    ↓ (點擊城市按鈕 "天氣 台北市")
LINE Platform
    ↓ (POST /callback)
app.py (handle_message)
    ↓
weather_service.py (WeatherForecast)
    ↓ (API Request)
中央氣象署 Open Data
    ↓ (JSON Response)
weather_service.py (create_flex_message)
    ↓ (FlexMessage JSON)
app.py (reply_message)
    ↓
LINE Platform
    ↓
LINE User (顯示 Flex Message)
```

### Rich Menu 切換流程
```
LINE User
    ↓ (點擊區域標籤 "北部")
RichMenuSwitchAction (前端直接切換)
    ↓ (使用 alias "north")
LINE Platform
    ↓ (切換到對應 Menu ID)
顯示北部城市列表
```

### 管理介面流程
```
管理員
    ↓ (瀏覽器訪問 :5001)
admin_app.py
    ↓ (GET /api/richmenus)
LINE Messaging API
    ↓ (返回選單列表)
admin_app.py
    ↓ (讀取本地圖片或下載)
richmenu/*.png 或 MessagingApiBlob
    ↓
管理員瀏覽器 (顯示卡片)
```

## 🔧 維護要點

### 程式碼維護
1. **不要手動編輯** `richmenu/__pycache__/`
2. **Menu ID 更新**後記得修改 `richmenu/rich_menu_alias.py` 的 `MENU_IDS`
3. **圖片設計修改**在 `generate_rich_menu_image.py` 的常數區
4. **城市列表更新**在 `weather_service.py` 的 `SUPPORTED_CITIES`

### 環境變數
必須設定：
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`
- `CWA_API_KEY`

選填：
- `PORT` (預設 5000)
- `ADMIN_PORT` (預設 5001)

### 版本控制
已忽略：
- `.env` (環境變數)
- `.venv/` (虛擬環境)
- `__pycache__/` (編譯快取)
- `*.pyc` (編譯檔案)

應提交：
- `richmenu/*.png` (選單圖片)
- `richmenu/rich_menu_alias.py` (Menu ID 記錄)
- 所有 `.py` 原始碼

## 📚 文檔索引

- **README.md** - 快速開始指南
- **RICHMENU_GUIDE.md** - Rich Menu 詳細架構與 API 說明
- **PROJECT_STRUCTURE.md** - 本檔案，專案結構總覽
- **note.md** - 開發筆記與問題記錄

## 🎓 技術棧

| 類別 | 技術 |
|------|------|
| 語言 | Python 3.11.13 |
| 套件管理 | UV |
| Web 框架 | Flask 3.1.2 |
| LINE SDK | line-bot-sdk 3.21.0 |
| 圖片處理 | Pillow 10.0.0 |
| HTTP 請求 | requests 2.32.3 |
| 環境變數 | python-dotenv 1.0.1 |
| 容器化 | Docker + Docker Compose |
| WSGI | Gunicorn (生產環境) |

## ✅ 檢查清單

啟動前確認：
- [ ] `.env` 已設定所有必要環境變數
- [ ] 虛擬環境已啟用 (UV)
- [ ] 所有依賴已安裝 (`uv pip install -r requirements.txt`)
- [ ] Rich Menu 已建立並設定預設選單
- [ ] LINE Webhook URL 已設定並啟用
- [ ] 防火牆允許 port 5000 (可選 5001)

部署前確認：
- [ ] `.env` 不在版控中
- [ ] Docker 映像檔可正常建置
- [ ] 健康檢查端點正常回應
- [ ] HTTPS 憑證已設定 (LINE 要求)
- [ ] 網域指向正確的伺服器
