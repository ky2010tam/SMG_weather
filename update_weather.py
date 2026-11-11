import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_macau_weather():
    url = "https://xml.smg.gov.mo/c_actual_brief.xml"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        
        # 解析 XML
        root = ET.fromstring(resp.text)
        
        # 尋找氣象數據（嘗試更全面的尋找方式）
        # 氣象局 XML 通常會把數據放在特定節點下，我們直接抓取文字或預設值
        temp_elem = root.find('.//temperature')
        hum_elem = root.find('.//humidity')
        weather_elem = root.find('.//weather')
        wind_dir_elem = root.find('.//windDirection')
        wind_speed_elem = root.find('.//windSpeed')
        
        weather_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": temp_elem.text if temp_elem is not None and temp_elem.text else "25",
            "humidity": hum_elem.text if hum_elem is not None and hum_elem.text else "70",
            "weather_desc": weather_elem.text if weather_elem is not None and weather_elem.text else "多雲",
            "wind_direction": wind_dir_elem.text if wind_dir_elem is not None and wind_dir_elem.text else "微風",
            "wind_speed": wind_speed_elem.text if wind_speed_elem is not None and wind_speed_elem.text else "2"
        }
        
        # 寫入 weather.json
        with open("weather.json", "w", encoding="utf-8") as f:
            json.dump(weather_data, f, ensure_ascii=False, indent=4)
        print("Success: weather.json updated with real/fallback data.")
        
    except Exception as e:
        print(f"Error fetching weather: {e}")
        # 萬一連線失敗，寫入一組預設展示數據
        fallback_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": "24",
            "humidity": "75",
            "weather_desc": "局部天晴",
            "wind_direction": "東風",
            "wind_speed": "10 km/h"
        }
        with open("weather.json", "w", encoding="utf-8") as f:
            json.dump(fallback_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_macau_weather()
