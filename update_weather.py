import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_macau_weather():
    url = "https://xml.smg.gov.mo/c_actual_brief.xml"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 抓取 UTC 標準時間，讓前端可以自動轉成用戶端時區
    utc_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        
        root = ET.fromstring(resp.text)
        
        temp_elem = root.find('.//temperature')
        hum_elem = root.find('.//humidity')
        weather_elem = root.find('.//weather')
        wind_dir_elem = root.find('.//windDirection')
        wind_speed_elem = root.find('.//windSpeed')
        
        weather_data = {
            "last_updated": utc_time,
            "temperature": temp_elem.text if temp_elem is not None and temp_elem.text else "24",
            "humidity": hum_elem.text if hum_elem is not None and hum_elem.text else "75",
            "weather_desc": weather_elem.text if weather_elem is not None and weather_elem.text else "晴",
            "wind_direction": wind_dir_elem.text if wind_dir_elem is not None and wind_dir_elem.text else "微風",
            "wind_speed": wind_speed_elem.text if wind_speed_elem is not None and wind_speed_elem.text else "10 km/h"
        }
        
        with open("weather.json", "w", encoding="utf-8") as f:
            json.dump(weather_data, f, ensure_ascii=False, indent=4)
        print("Success: weather.json updated.")
        
    except Exception as e:
        print(f"Error fetching weather: {e}")
        fallback_data = {
            "last_updated": utc_time,
            "temperature": "24",
            "humidity": "75",
            "weather_desc": "晴",
            "wind_direction": "微風",
            "wind_speed": "10 km/h"
        }
        with open("weather.json", "w", encoding="utf-8") as f:
            json.dump(fallback_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_macau_weather()
