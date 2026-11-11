import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def fetch_all_smg_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    utc_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    master_data = {
        "last_updated": utc_time,
        "current_weather": {},       # 總體簡報
        "stations_weather": [],      # 各測站詳細天氣 (來自 c_actualweather.xml)
        "forecast_7days": [],        # 7日預報
        "air_quality": []            # 空氣質量
    }
    
    # 1. 抓取實時天氣簡報 (c_actual_brief.xml)
    try:
        url = "https://xml.smg.gov.mo/c_actual_brief.xml"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        root = ET.fromstring(resp.text)
        
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
        master_data["current_weather"] = current
    except Exception as e:
        print(f"Error fetching actual brief: {e}")

    # 2. 抓取各站詳細天氣 (c_actualweather.xml)
    try:
        url = "https://xml.smg.gov.mo/c_actualweather.xml"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        root = ET.fromstring(resp.text)
        
        stations = []
        # 遍歷 XML 中代表各個測站或項目的節點
        for item in root.iter():
            station_data = {}
            for child in item:
                if child.tag and child.text:
                    station_data[child.tag.lower()] = child.text.strip()
            # 只要包含站名或測量數據就收錄
            if station_data and station_data not in stations:
                stations.append(station_data)
        master_data["stations_weather"] = stations
    except Exception as e:
        print(f"Error fetching actual weather stations: {e}")

    # 3. 抓取七日天氣預報 (c_7daysforecast.xml)
    try:
        url = "https://xml.smg.gov.mo/c_7daysforecast.xml"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        root = ET.fromstring(resp.text)
        
        forecasts = []
        for item in root.iter():
            day_data = {}
            for child in item:
                if child.tag and child.text:
                    day_data[child.tag.lower()] = child.text.strip()
            if ('validfor' in day_data or 'date' in day_data) and day_data not in forecasts:
                forecasts.append(day_data)
        master_data["forecast_7days"] = forecasts
    except Exception as e:
        print(f"Error fetching 7-day forecast: {e}")

    # 4. 抓取空氣質量 JSON
    try:
        url = "https://www.smg.gov.mo/smg/airQuality/latestAirConcentration.json"
        resp = requests.get(url, headers=headers, timeout=10)
        master_data["air_quality"] = resp.json()
    except Exception as e:
        print(f"Error fetching air quality: {e}")

    # 5. 寫入 weather.json
    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(master_data, f, ensure_ascii=False, indent=4)
    print("Success: Updated weather.json with multi-station data.")

if __name__ == "__main__":
    fetch_all_smg_data()
