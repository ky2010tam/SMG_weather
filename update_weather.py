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
        
        # 遍歷所有節點，精準抓取常見的氣象實況欄位名稱
        current = {}
        for elem in root.iter():
            tag = elem.tag.lower()
            val = elem.text.strip() if elem.text else ""
            if not val:
                continue
            
            if 'temp' in tag and 'temperature' not in current:
                current['temperature'] = val
            elif 'humid' in tag and 'humidity' not in current:
                current['humidity'] = val
            elif ('weather' in tag or 'cond' in tag) and len(val) < 15 and 'weather_desc' not in current:
                current['weather_desc'] = val
            elif 'winddir' in tag and 'wind_direction' not in current:
                current['wind_direction'] = val
            elif 'windspeed' in tag and 'wind_speed' not in current:
                current['wind_speed'] = val
                
        if current:
            master_data["current_weather"].update(current)
    except Exception as e:
        print(f"Error fetching actual weather: {e}")

    # 2. 抓取七日天氣預報 (c_7daysforecast.xml)
    try:
        url = "https://xml.smg.gov.mo/c_7daysforecast.xml"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        root = ET.fromstring(resp.text)
        
        forecasts = []
        # 放寬條件，抓取所有包含預報日期的節點
        for item in root.iter():
            day_data = {}
            for child in item:
                if child.tag and child.text:
                    day_data[child.tag.lower()] = child.text.strip()
            # 只要包含有效日期或星期就當作一筆預報
            if ('validfor' in day_data or 'date' in day_data) and day_data not in forecasts:
                forecasts.append(day_data)
                
        master_data["forecast_7days"] = forecasts
    except Exception as e:
        print(f"Error fetching 7-day forecast: {e}")

    # 3. 抓取真實空氣質量 JSON
    try:
        url = "https://www.smg.gov.mo/smg/airQuality/latestAirConcentration.json"
        resp = requests.get(url, headers=headers, timeout=10)
        master_data["air_quality"] = resp.json()
    except Exception as e:
        print(f"Error fetching air quality: {e}")

    # 4. 寫入 weather.json
    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(master_data, f, ensure_ascii=False, indent=4)
    print("Success: Updated weather.json with robust parser.")

if __name__ == "__main__":
    fetch_all_smg_data()
