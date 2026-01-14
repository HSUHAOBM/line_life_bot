FROM python:3.11-slim

WORKDIR /app

# 安裝 uv
RUN pip install --no-cache-dir uv

# 複製專案檔案
COPY pyproject.toml requirements.txt ./

# 使用 uv 安裝依賴
RUN uv pip install --system -r requirements.txt

# 複製應用程式碼
COPY . .

# 設定環境變數
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 5000

# 使用 gunicorn 執行應用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
