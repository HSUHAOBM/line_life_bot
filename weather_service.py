import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CWA_API_KEY = os.getenv('CWA_API_KEY')
cwa_api_key = CWA_API_KEY  # 別名，供類別使用
CWA_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

# 支援的縣市列表
SUPPORTED_CITIES = [
    '臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市',
    '基隆市', '新竹市', '新竹縣', '苗栗縣', '彰化縣', '南投縣',
    '雲林縣', '嘉義市', '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣',
    '臺東縣', '澎湖縣', '金門縣', '連江縣'
]


def format_supported_cities_list() -> str:
    """
    格式化支援的縣市列表

    Returns:
        格式化的縣市列表字串
    """
    lines = ["📍 支援的縣市（共22個）："]
    lines.append("")

    # 分區顯示
    north = ['臺北市', '新北市', '基隆市', '桃園市', '新竹市', '新竹縣']
    central = ['臺中市', '苗栗縣', '彰化縣', '南投縣', '雲林縣']
    south = ['臺南市', '高雄市', '嘉義市', '嘉義縣', '屏東縣']
    east = ['宜蘭縣', '花蓮縣', '臺東縣']
    islands = ['澎湖縣', '金門縣', '連江縣']

    lines.append("北部：" + '、'.join(north))
    lines.append("中部：" + '、'.join(central))
    lines.append("南部：" + '、'.join(south))
    lines.append("東部：" + '、'.join(east))
    lines.append("離島：" + '、'.join(islands))

    return "\n".join(lines)


def normalize_city_name(city_input: str) -> str:
    """
    正規化城市名稱（處理台/臺的差異）

    Args:
        city_input: 使用者輸入的城市名稱

    Returns:
        正規化後的城市名稱
    """
    # 將「台」統一替換成「臺」
    normalized = city_input.replace('台', '臺')

    # 如果沒有「市」或「縣」後綴，嘗試加上
    if not (normalized.endswith('市') or normalized.endswith('縣')):
        # 先嘗試加「市」
        if f"{normalized}市" in SUPPORTED_CITIES:
            return f"{normalized}市"
        # 再嘗試加「縣」
        elif f"{normalized}縣" in SUPPORTED_CITIES:
            return f"{normalized}縣"

    return normalized


def get_period_name(start_time: str) -> str:
    """
    根據時間判斷時段並加上 emoji

    Args:
        start_time: 開始時間字串 (格式: YYYY-MM-DD HH:MM:SS)

    Returns:
        帶有 emoji 的時段名稱
    """
    hour = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").hour
    if 5 <= hour < 12:
        return "🌅 早上"
    elif 12 <= hour < 18:
        return "☀️ 白天"
    elif 18 <= hour < 24:
        return "🌃 晚上"
    else:
        return "🌙 凌晨"


def get_weather(city_name: str) -> str:
    """
    查詢指定城市的天氣預報（使用中央氣象署 API）

    Args:
        city_name: 城市名稱（例如：台北、高雄、台中）

    Returns:
        格式化的 36 小時天氣預報字串
    """
    if not CWA_API_KEY:
        return "⚠️ 中央氣象署 API 金鑰未設定，請檢查 .env 檔案"

    # 正規化城市名稱
    location = normalize_city_name(city_name)

    # 檢查是否為支援的城市
    if location not in SUPPORTED_CITIES:
        # 將縣市分組顯示
        cities_formatted = format_supported_cities_list()
        return f"❌ 找不到「{city_name}」的天氣資料\n\n{cities_formatted}"

    try:
        # 呼叫中央氣象署 API
        params = {
            'Authorization': CWA_API_KEY,
            'locationName': location
        }

        response = requests.get(CWA_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 解析資料
        location_data = data['records']['location'][0]
        location_name = location_data['locationName']
        elements = location_data['weatherElement']

        # 建立元素對照表
        element_map = {el['elementName']: el['time'] for el in elements}

        # 格式化訊息
        lines = [f"📍 {location_name} 36 小時天氣預報"]

        # 取得三個時段的預報
        for i in range(3):
            start = element_map['Wx'][i]['startTime']
            end = element_map['Wx'][i]['endTime']
            period = get_period_name(start)

            # 天氣現象
            wx = element_map['Wx'][i]['parameter']['parameterName']
            # 舒適度
            ci = element_map['CI'][i]['parameter']['parameterName']
            # 最低溫
            minT = element_map['MinT'][i]['parameter']['parameterName']
            # 最高溫
            maxT = element_map['MaxT'][i]['parameter']['parameterName']
            # 降雨機率
            pop = element_map['PoP'][i]['parameter']['parameterName']

            lines.append("")
            lines.append(f"{period}（{start[5:16]} ~ {end[11:16]}）")
            lines.append(f"☁️ {wx}，{ci}")
            lines.append(f"🌡️ 溫度：{minT}°C ~ {maxT}°C")
            lines.append(f"💧 降雨機率：{pop}%")

        return "\n".join(lines)

    except requests.exceptions.HTTPError as e:
        return f"⚠️ API 請求失敗 (HTTP {response.status_code})"
    except requests.exceptions.Timeout:
        return "⏱️ 查詢逾時，請稍後再試"
    except requests.exceptions.RequestException as e:
        return f"❌ 網路錯誤: {str(e)}"
    except KeyError as e:
        return f"❌ 資料解析錯誤，請確認 API 回應格式"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"


class WeatherForecast:
    """天氣預報類別 - 支援 Flex Message"""

    def __init__(self, location='高雄市'):
        self.location = location
        self.api_url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001'
        self.result = ''
        self.weather_data = []  # 儲存結構化資料用於 Flex Message

    def get_period_name(self, start_time):
        """根據時間判斷時段並加上 emoji"""
        hour = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").hour
        if 5 <= hour < 12:
            return "🌅 早上"
        elif 12 <= hour < 18:
            return "☀️ 白天"
        elif 18 <= hour < 24:
            return "🌃 晚上"
        else:
            return "🌙 凌晨"

    def fetch(self):
        """取得天氣預報資料"""
        if not cwa_api_key:
            print("Warning: CWA_API_KEY not set")
            self.result = "無法取得天氣資料：API Key 未設定"
            return self.result

        # 檢查是否為支援的城市
        if self.location not in SUPPORTED_CITIES:
            cities_formatted = format_supported_cities_list()
            self.result = f"❌ 找不到「{self.location}」的天氣資料\n\n{cities_formatted}"
            return self.result

        params = {
            'Authorization': cwa_api_key,
            'locationName': self.location
        }
        try:
            # 禁用 SSL 驗證以避免 GitHub Actions 環境的憑證問題
            response = requests.get(self.api_url, params=params, verify=False)
            response.raise_for_status()
            data = response.json()

            location_data = data['records']['location'][0]
            location_name = location_data['locationName']
            elements = location_data['weatherElement']

            # 建立元素對照表
            element_map = {el['elementName']: el['time'] for el in elements}

            # 格式化訊息
            lines = [f"*{location_name} 36 小時天氣預報*"]
            self.weather_data = []  # 清空並重新填充

            for i in range(3):
                start = element_map['Wx'][i]['startTime']
                end = element_map['Wx'][i]['endTime']
                period = self.get_period_name(start)

                wx = element_map['Wx'][i]['parameter']['parameterName']
                ci = element_map['CI'][i]['parameter']['parameterName']
                minT = element_map['MinT'][i]['parameter']['parameterName']
                maxT = element_map['MaxT'][i]['parameter']['parameterName']
                pop = element_map['PoP'][i]['parameter']['parameterName']

                lines.append("")
                lines.append(f"{period}({start[0:16]} ~ {end[11:16]})")
                lines.append(f"{wx},{ci}")
                lines.append(f"溫度:{minT}°C ~ {maxT}°C")
                lines.append(f"降雨:{pop}%")

                # 儲存結構化資料用於 Flex Message
                emoji_map = {"🌅 早上": "🌅", "☀️ 白天": "☀️",
                             "🌃 晚上": "🌃", "🌙 凌晨": "🌙"}
                period_text = period.replace(
                    emoji_map.get(period, ""), "").strip()

                # 第 3 個時段(索引 2)如果是"早上",加上"明天"前綴
                if i == 2 and "早上" in period_text:
                    period_text = "明天" + period_text

                self.weather_data.append({
                    "period": period_text,
                    "emoji": emoji_map.get(period, "🌤️"),
                    "time": f"{start[5:16]} - {end[5:16]}",
                    "weather": wx,
                    "comfort": ci,
                    "minTemp": minT,
                    "maxTemp": maxT,
                    "rain": pop
                })

            self.result = "\n".join(lines)
            return self.result

        except Exception as e:
            print(f"Failed to fetch weather data: {e}")
            self.result = f"無法取得{self.location}天氣資料"
            return self.result

    def get_flex_message(self):
        """取得 Flex Message 格式的天氣預報"""
        if not self.weather_data:
            self.fetch()

        if "無法取得" in self.result or "未設定" in self.result:
            return None

        return create_weather_flex_message(self.location, self.weather_data)


def create_weather_flex_message(location_name, weather_data):
    """
    建立天氣預報的 Flex Message - V3 緊湊卡片風格

    Args:
        location_name: 地點名稱
        weather_data: list of dict, 每個 dict 包含:
            - period: 時段名稱
            - emoji: emoji 圖示
            - time: 時間範圍
            - weather: 天氣狀況
            - comfort: 舒適度
            - minTemp: 最低溫度
            - maxTemp: 最高溫度
            - rain: 降雨機率
    """
    # 建立天氣項目
    contents = [
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"🌤️ {location_name}天氣",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#2C3E50"
                },
                {
                    "type": "text",
                    "text": "36 小時預報",
                    "size": "xs",
                    "color": "#95A5A6",
                    "margin": "xs"
                }
            ],
            "paddingBottom": "15px"
        },
        {
            "type": "separator"
        }
    ]

    for i, weather in enumerate(weather_data):
        # 降雨機率顏色
        rain_percent = int(weather["rain"])
        if rain_percent >= 70:
            rain_color = "#E53935"
        elif rain_percent >= 30:
            rain_color = "#FB8C00"
        else:
            rain_color = "#43A047"

        # 卡片式設計
        weather_card = {
            "type": "box",
            "layout": "vertical",
            "contents": [
                # 標題列: emoji + 時段 + 時間
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": weather["emoji"],
                            "size": "lg",
                            "flex": 0,
                            "margin": "none"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": weather["period"],
                                    "weight": "bold",
                                    "size": "md",
                                    "color": "#2C3E50"
                                },
                                {
                                    "type": "text",
                                    "text": weather["time"],
                                    "size": "xxs",
                                    "color": "#95A5A6"
                                }
                            ],
                            "margin": "md"
                        }
                    ]
                },
                {
                    "type": "separator",
                    "margin": "md"
                },
                # 天氣資訊
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": weather["weather"],
                            "size": "md",
                            "color": "#34495E",
                            "weight": "bold",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": weather["comfort"],
                            "size": "sm",
                            "color": "#7F8C8D",
                            "margin": "xs",
                            "wrap": True
                        }
                    ],
                    "margin": "md"
                },
                # 溫度和降雨 - 並排顯示
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🌡️",
                                    "size": "md",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": f"{weather['minTemp']}° - {weather['maxTemp']}°",
                                    "size": "md",
                                    "weight": "bold",
                                    "color": "#FF6B35",
                                    "margin": "sm",
                                    "flex": 0
                                }
                            ],
                            "flex": 1
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "💧",
                                    "size": "md",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": f"{weather['rain']}%",
                                    "size": "md",
                                    "weight": "bold",
                                    "color": rain_color,
                                    "margin": "sm",
                                    "flex": 0
                                }
                            ],
                            "flex": 1
                        }
                    ],
                    "margin": "md",
                    "spacing": "md"
                }
            ],
            "backgroundColor": "#FAFAFA",
            "cornerRadius": "10px",
            "paddingAll": "15px",
            "margin": "md"
        }
        contents.append(weather_card)

    # 直接回傳 Flex Message 的 JSON 結構
    flex_message = {
        "type": "flex",
        "altText": f"🌤️ {location_name} 36 小時天氣預報",
        "contents": {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px"
            },
            "styles": {
                "body": {
                    "backgroundColor": "#FFFFFF"
                }
            }
        }
    }
    return flex_message
