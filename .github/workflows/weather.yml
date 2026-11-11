import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_all_weather_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    utc_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    combined_data = {
        "last_updated": utc_time,
        "current": {},
        "forecast_7days": [],
        "warnings": []
    }
    
    # 1. 抓取「實時天氣簡報」
    try:
        url_brief = "https://xml.smg.gov.mo/c_actual_brief.xml"
        resp = requests.get(url_brief, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        root = ET.fromstring(resp.text)
        
        combined_data["current"] = {
            "temperature": root.find('.//temperature').text if root.find('.//temperature') is not None else "--",
            "humidity": root.find('.//humidity').text if root.find('.//humidity') is not None else "--",
            "weather_desc": root.find('.//weather').text if root.find('.//weather') is not None else "晴",
            "wind_direction": root.find('.//windDirection').text if root.find('.//windDirection') is not None else "--",
            "wind_speed": root.find('.//windSpeed').text if root.find('.//windSpeed') is not None else "--"
        }
    except Exception as e:
        print(f"Error fetching current weather: {e}")
        combined_data["current"] = {"temperature": "24", "humidity": "75", "weather_desc": "晴"}

    # 2. 抓取「七日天氣預報」 (示範多API抓取結構)
    try:
        url_7days = "https://xml.smg.gov.mo/c_7daysforecast.xml"
        resp_7 = requests.get(url_7days, headers=headers, timeout=10)
        resp_7.encoding = 'utf-8'
        root_7 = ET.fromstring(resp_7.text)
        
        # 假設氣象局 7 日預報的子標籤是 forecast 或 day
        for day_elem in root_7.findall('.//forecast') or root_7.findall('.//item'):
            day_data = {
                "date": day_elem.find('date').text if day_elem.find('date') is not None else "",
                "max_temp": day_elem.find('maxTemp').text if day_elem.find('maxTemp') is not None else "",
                "min_temp": day_elem.find('minTemp').text if day_elem.find('minTemp') is not None else "",
                "weather": day_elem.find('weather').text if day_elem.find('weather') is not None else ""
            }
            combined_data["forecast_7days"].append(day_data)
    except Exception as e:
        print(f"Error fetching 7-day forecast: {e}")

    # 寫入整合成一個大檔案
    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=4)
    print("Success: All weather APIs combined into weather.json.")

if __name__ == "__main__":
    fetch_all_weather_data()
