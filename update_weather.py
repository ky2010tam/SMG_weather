import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_all_smg_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    utc_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    master_data = {
        "last_updated": utc_time,
        "current_weather": {
            "temperature": "--",
            "humidity": "--",
            "weather_desc": "--",
            "wind_direction": "--",
            "wind_speed": "--"
        },
        "forecast_7days": [],
        "air_quality": [],
        "warnings": {
            "rainstorm": None,
            "tropical_cyclone": None,
            "thunderstorm": None
        }
    }
    
    # 1. 抓取實時天氣 (c_actual_brief.xml)
    try:
        url = "https://xml.smg.gov.mo/c_actual_brief.xml"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        root = ET.fromstring(resp.text)
        
        # 根據 SMG 實時天氣的常見標籤精準提取
        for elem in root.iter():
            tag = elem.tag.lower()
            if 'temp' in tag and elem.text:
                master_data["current_weather"]["temperature"] = elem.text.strip()
            elif 'humid' in tag and elem.text:
                master_data["current_weather"]["humidity"] = elem.text.strip()
            elif 'weather' in tag and elem.text and len(elem.text.strip()) < 10:
                master_data["current_weather"]["weather_desc"] = elem.text.strip()
            elif 'winddir' in tag and elem.text:
                master_data["current_weather"]["wind_direction"] = elem.text.strip()
            elif 'windspeed' in tag and elem.text:
                master_data["current_weather"]["wind_speed"] = elem.text.strip()
    except Exception as e:
        print(f"Error fetching actual weather: {e}")

    # 2. 抓取七日天氣預報 (c_7daysforecast.xml)
    try:
        url = "https://xml.smg.gov.mo/c_7daysforecast.xml"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        root = ET.fromstring(resp.text)
        
        forecasts = []
        # 在 7 日預報中，通常每一天是一個結點（如 forecast 或 data）
        for item in root.iter():
            # 檢查是否包含日期欄位
            validfor = item.find('validFor') or item.find('date')
            if validfor is not None:
                day_data = {
                    "date": validfor.text if validfor is not None else "",
                    "day_of_week": item.find('c_dayOfWeek').text if item.find('c_dayOfWeek') is not None else "",
                    "weather_desc": item.find('weatherDescription').text if item.find('weatherDescription') is not None else "",
                    "weather_status": item.find('weatherStatus').text if item.find('weatherStatus') is not None else ""
                }
                if day_data not in forecasts:
                    forecasts.append(day_data)
        master_data["forecast_7days"] = forecasts
    except Exception as e:
        print(f"Error fetching 7-day forecast: {e}")

    # 3. 抓取真實的空氣污染物濃度 JSON
    try:
        url = "https://www.smg.gov.mo/smg/airQuality/latestAirConcentration.json"
        resp = requests.get(url, headers=headers, timeout=10)
        master_data["air_quality"] = resp.json()
    except Exception as e:
        print(f"Error fetching air quality: {e}")

    # 4. 寫入 weather.json
    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(master_data, f, ensure_ascii=False, indent=4)
    print("Success: Fixed and updated weather.json.")

if __name__ == "__main__":
    fetch_all_smg_data()
