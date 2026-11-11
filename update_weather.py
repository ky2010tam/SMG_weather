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
        
        # 根據氣象局 XML 的實際結構提取數據 (以下為常見欄位示範)
        # 實際標籤名稱可根據下載的 XML 調整
        weather_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": root.find('.//temperature').text if root.find('.//temperature') is not None else "--",
            "humidity": root.find('.//humidity').text if root.find('.//humidity') is not None else "--",
            "weather_desc": root.find('.//weather').text if root.find('.//weather') is not None else "晴",
            "wind_direction": root.find('.//windDirection').text if root.find('.//windDirection') is not None else "--",
            "wind_speed": root.find('.//windSpeed').text if root.find('.//windSpeed') is not None else "--"
        }
        
        # 寫入 weather.json
        with open("weather.json", "w", encoding="utf-8") as f:
            json.dump(weather_data, f, ensure_ascii=False, indent=4)
        print("Success: weather.json updated.")
        
    except Exception as e:
        print(f"Error fetching weather: {e}")

if __name__ == "__main__":
    fetch_macau_weather()
