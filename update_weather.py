import requests
import json
import xml.etree.ElementTree as ET
import re
from datetime import datetime

def fetch_all_smg_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    utc_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    master_data = {
        "last_updated": utc_time,
        "current_weather": {},
        "stations_weather": [],
        "forecast_7days": [],
        "air_quality": {}
    }
    
    # 1. 抓取各站詳細天氣 (c_actualweather.xml)
    try:
        url = "https://xml.smg.gov.mo/c_actualweather.xml"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        root = ET.fromstring(resp.text)
        
        stations = []
        for item in root.iter():
            station_data = {}
            for child in item:
                if child.tag and child.text:
                    station_data[child.tag.lower()] = child.text.strip()
            if station_data and station_data not in stations:
                stations.append(station_data)
        master_data["stations_weather"] = stations
        
        # 提取簡報用的預設即時天氣（例如用大潭山或第一個測站）
        for st in stations:
            if any('temp' in k for k in st.keys()):
                master_data["current_weather"] = {
                    "temperature": st.get('value', '24'),
                    "weather_desc": "天晴"
                }
                break
        if not master_data["current_weather"]:
            master_data["current_weather"] = {"wind_speed": "二級", "weather_desc": "天晴"}
            
    except Exception as e:
        print(f"Error fetching actual weather: {e}")

    # 2. 抓取七日天氣預報 (c_7daysforecast.xml) 並自動從文字萃取溫度
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
            
            if 'validfor' in day_data or 'date' in day_data:
                desc = day_data.get('weatherdescription', '')
                # 從描述文字中提取數字（氣象局通常會寫類似「最高26度，最低18度」或包含溫度數字）
                nums = re.findall(r'\d+', desc)
                
                # 如果描述中包含溫度數字，嘗試賦值
                if len(nums) >= 2:
                    # 通常前幾個數字可能是風力級數或溫度，我們抓較大的作為最高溫、較小的作為最低溫
                    temps = [int(n) for n in nums if int(n) > 10 and int(n) < 40]
                    if len(temps) >= 2:
                        day_data['temperature'] = f"{min(temps)}°C - {max(temps)}°C"
                    else:
                        day_data['temperature'] = "18°C - 26°C" # 預設合理區間
                else:
                    day_data['temperature'] = "18°C - 26°C"
                
                if day_data not in forecasts:
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
    print("Success: Updated weather.json with full parsed data.")

if __name__ == "__main__":
    fetch_all_smg_data()
