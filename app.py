from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from dotenv import load_dotenv
import os
from weather_service import (
    get_weather,
    WeatherForecast,
    normalize_city_name,
    format_supported_cities_list
)
import json
import traceback

# 載入環境變數
load_dotenv()

app = Flask(__name__)

# LINE Bot 設定
configuration = Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


@app.route("/callback", methods=['POST'])
def callback():
    """LINE webhook callback endpoint"""

    # 取得 X-Line-Signature header
    signature = request.headers.get('X-Line-Signature', '')

    # 取得請求 body，LINE 驗簽要用原始 body
    body = request.get_data(as_text=True)

    # Cloudflare / Proxy / Flask 看到的 IP
    cf_connecting_ip = request.headers.get("CF-Connecting-IP")
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    x_real_ip = request.headers.get("X-Real-IP")
    remote_addr = request.remote_addr

    # 判斷最可能的真實來源 IP
    # 如果有 Cloudflare，CF-Connecting-IP 通常就是 LINE 的來源 IP
    client_ip = remote_addr

    if x_real_ip:
        client_ip = x_real_ip.strip()

    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0].strip()

    if cf_connecting_ip:
        client_ip = cf_connecting_ip.strip()

    # 整理要記錄的資訊
    log_data = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        # 最重要：來源 IP
        "client_ip": client_ip,
        "remote_addr": remote_addr,
        "x_real_ip": x_real_ip,
        "x_forwarded_for": x_forwarded_for,
        "cf_connecting_ip": cf_connecting_ip,

        # Cloudflare 資訊
        "cf_ray": request.headers.get("CF-Ray"),
        "cf_ipcountry": request.headers.get("CF-IPCountry"),
        "cf_visitor": request.headers.get("CF-Visitor"),

        # Request 基本資訊
        "method": request.method,
        "scheme": request.scheme,
        "host": request.host,
        "path": request.path,
        "full_path": request.full_path,
        "url": request.url,
        "base_url": request.base_url,
        "query_string": request.query_string.decode("utf-8", errors="replace"),

        # Header 重點
        "user_agent": request.headers.get("User-Agent"),
        "content_type": request.headers.get("Content-Type"),
        "content_length": request.headers.get("Content-Length"),
        "x_line_signature_exists": bool(signature),
        "x_line_signature": signature,

        # Flask / WSGI 資訊
        "access_route": list(request.access_route),
        "server_protocol": request.environ.get("SERVER_PROTOCOL"),
        "remote_port": request.environ.get("REMOTE_PORT"),

        # 全部 headers
        "headers": dict(request.headers),

        # 原始 body
        "body": body
    }

    app.logger.info(
        "LINE Webhook Request Detail:\n%s",
        json.dumps(log_data, ensure_ascii=False, indent=2)
    )

    # 驗證請求來源
    try:
        handler.handle(body, signature)

    except InvalidSignatureError:
        app.logger.warning(
            "Invalid signature. client_ip=%s, cf_connecting_ip=%s, body=%s",
            client_ip,
            cf_connecting_ip,
            body
        )
        abort(400)

    except Exception as ex:
        app.logger.error(
            "Webhook exception. client_ip=%s, error=%s, traceback=%s",
            client_ip,
            str(ex),
            traceback.format_exc()
        )
        abort(500)

    app.logger.info(
        "LINE Webhook OK. client_ip=%s, cf_connecting_ip=%s, cf_ray=%s",
        client_ip,
        cf_connecting_ip,
        request.headers.get("CF-Ray")
    )

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理文字訊息 - 天氣查詢 (地區切換已由 RichMenuSwitchAction 處理)"""
    user_message = event.message.text.strip()
    user_id = event.source.user_id

    # 檢查是否以「天氣」開頭
    if not user_message.startswith("天氣"):
        cities_list = format_supported_cities_list()
        help_text = f"請輸入「天氣 城市名稱」\n\n{cities_list}"
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=help_text)]
                )
            )
        return

    # 提取城市名稱（移除「天氣」和空格）
    city_input = user_message[2:].strip()

    if not city_input:
        cities_list = format_supported_cities_list()
        help_text = f"請輸入城市名稱\n\n{cities_list}"
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=help_text)]
                )
            )
        return

    # 正規化城市名稱
    city_name = normalize_city_name(city_input)

    # 使用 WeatherForecast 類別取得天氣資訊
    forecast = WeatherForecast(location=city_name)
    forecast.fetch()

    # 嘗試使用 Flex Message
    flex_data = forecast.get_flex_message()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if flex_data:
            # 使用漂亮的 Flex Message 回覆
            flex_msg = FlexMessage(
                alt_text=flex_data["altText"],
                contents=FlexContainer.from_dict(flex_data["contents"])
            )
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_msg]
                )
            )
        else:
            # 降級使用純文字回覆
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=forecast.result)]
                )
            )


@app.route("/health", methods=['GET'])
def health():
    """健康檢查 endpoint"""
    return 'OK', 200


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
