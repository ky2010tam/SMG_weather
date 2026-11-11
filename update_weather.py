import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_all_smg_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    utc_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    master_data = {
        "last_updated": utc_time,
        "current_weather": {},
        "forecast_7days": [],
        "air_quality": [],
        "warnings": {
            "rainstorm": None,
            "tropical_cyclone": None,
            "thunderstorm": None
        }
    }
    
    # 1. 抓取實時天氣 (Tempo Presente)
    try:
        url = "https://xml.smg.gov.mo/c_actual_brief.xml"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        root = ET.fromstring(resp.text)
        
        current = {}
        for elem in root.iter():
            if elem.tag and elem.text and elem.text.strip():
                tag_name = elem.tag.lower()
                # 收集實時數據的常用欄位
                if 'temp' in tag_name:
                    current['temperature'] = elem.text.strip()
                elif 'humid' in tag_name:
                    current['humidity'] = elem.text.strip()
                elif 'weather' in tag_name and len(elem.text.strip()) < 30:
                    current['weather_desc'] = elem.text.strip()
                elif 'winddir' in tag_name:
                    current['wind_direction'] = elem.text.strip()
                elif 'windspeed' in tag_name:
                    current['wind_speed'] = elem.text.strip()
                    
        master_data["current_weather"] = current if current else {"status": "資料暫缺"}
    except Exception as e:
        print(f"Error fetching actual weather: {e}")

    # 2. 抓取七日天氣預報 (Previsao 7 dias)
    try:
        url = "https://xml.smg.gov.mo/c_7daysforecast.xml"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        root = ET.fromstring(resp.text)
        
        forecasts = []
        for item in root.iter():
            # 尋找預報節點
            if 'forecast' in item.tag.lower() or 'day' in item.tag.lower() or 'item' in item.tag.lower():
                day_data = {}
                for child in item:
                    if child.tag and child.text:
                        day_data[child.tag.lower()] = child.text.strip()
                if day_data and day_data not in forecasts:
                    forecasts.append(day_data)
        master_data["forecast_7days"] = forecasts
    except Exception as e:
        print(f"Error fetching 7-day forecast: {e}")

    # 3. 抓取空氣污染物實測濃度 (JSON 格式 API)
    try:
        url = "https://api.data.gov.mo/document/download/8d089bb5-5b2d-4b56-9f47-efbc35fe8870?token=null&isNeedFile=0&lang=TC"
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        master_data["air_quality"] = data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"Error fetching air quality: {e}")

    # 4. 寫入總合的 weather.json
    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(master_data, f, ensure_ascii=False, indent=4)
    print("Success: All SMG data successfully consolidated into weather.json.")

if __name__ == "__main__":
    fetch_all_smg_data()
