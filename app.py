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
    signature = request.headers['X-Line-Signature']

    # 取得請求 body
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 驗證請求來源
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理文字訊息 - 支援 Flex Message"""
    user_message = event.message.text.strip()

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
