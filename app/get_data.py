import json
import os
import csv
import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib
# use a non-interactive backend for environments without a display (containers, CI)
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def fetch_and_process(latitude=28.6519, longitude=77.2315, place_name="Unknown"):
    today = datetime.now()
    week_ago = today - timedelta(days=7)

    start_date = week_ago.strftime('%Y-%m-%d')
    end_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&daily=weather_code,sunrise,sunset"
        "&hourly=temperature_2m"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
        "&timezone=auto"
    )

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # prepare output paths
    os.makedirs('plots', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_place = place_name.replace(' ', '_')
    raw_json_path = os.path.join('plots', f'{safe_place}_data_raw_{timestamp}.json')
    selected_csv_path = os.path.join('plots', f'{safe_place}_data_selected_{timestamp}.csv')
    plot_path = os.path.join('plots', f'{safe_place}_temperature_plot_{timestamp}.png')

    # save raw JSON backup
    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    daily = data.get('daily', {}) or {}
    hourly = data.get('hourly', {}) or {}

    daily_dates = daily.get('time', [])
    # try possible weather key names
    daily_weather = daily.get('weather_code', daily.get('weathercode', []))

    hourly_times = hourly.get('time', [])
    hourly_temp = hourly.get('temperature_2m', [])

    if hourly_times and hourly_temp:
        hourly_df = pd.DataFrame({'time': hourly_times, 'temperature': hourly_temp})
        hourly_df['time'] = pd.to_datetime(hourly_df['time'])
        hourly_df['date'] = hourly_df['time'].dt.date.astype(str)
        daily_temp = hourly_df.groupby('date', as_index=False)['temperature'].mean()
    else:
        daily_temp = pd.DataFrame({'date': [str(d) for d in daily_dates], 'temperature': [None] * len(daily_dates)})

    daily_df = pd.DataFrame({'date': [str(d) for d in daily_dates], 'weather': daily_weather})

    merged = pd.merge(daily_df, daily_temp, on='date', how='left')

    # select only required columns and save
    selected = merged[['date', 'weather', 'temperature']]
    selected.to_csv(selected_csv_path, index=False)

    # plot temperature
    plt.figure(figsize=(10, 5))
    x = pd.to_datetime(selected['date'])
    y = selected['temperature'].astype(float)
    plt.plot(x, y, marker='o')
    plt.title('Daily Average Temperature')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.grid(True)

    # annotate weather codes above points
    for xi, yi, w in zip(x, y, selected['weather']):
        if pd.notna(yi):
            plt.text(xi, yi, str(w), fontsize=8, ha='center', va='bottom', rotation=30)

    plt.tight_layout()
    plt.savefig(plot_path)
    print(f'Saved: {selected_csv_path}, {plot_path}, {raw_json_path}')

    # append run metadata to a log CSV
    log_path = 'saved_data_log.csv'
    header = ['timestamp', 'place', 'latitude', 'longitude', 'selected_csv', 'plot_image', 'raw_json']
    row = [timestamp, place_name, latitude, longitude, selected_csv_path, plot_path, raw_json_path]
    write_header = not os.path.exists(log_path)
    with open(log_path, 'a', newline='', encoding='utf-8') as lf:
        writer = csv.writer(lf)
        if write_header:
            writer.writerow(header)
        writer.writerow(row)

    # return paths for external callers
    return {
        'timestamp': timestamp,
        'place': place_name,
        'latitude': latitude,
        'longitude': longitude,
        'selected_csv': selected_csv_path,
        'plot_image': plot_path,
        'raw_json': raw_json_path,
    }


def get_place_from_user_and_geocode():
    default_place = "New Delhi"
    inp = input(f"Enter place name (or press Enter for default '{default_place}'): ").strip()
    place = inp if inp else default_place
    # use Open-Meteo geocoding API
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(place)}&count=1"
    try:
        r = requests.get(geo_url, timeout=10)
        r.raise_for_status()
        res = r.json()
        results = res.get('results') or []
        if results:
            first = results[0]
            lat = first.get('latitude')
            lon = first.get('longitude')
            name = first.get('name') or place
            country = first.get('country')
            display_name = f"{name}, {country}" if country else name
            print(f"Geocoded '{place}' -> {display_name} ({lat},{lon})")
            return lat, lon, display_name
        else:
            print(f"No geocoding results for '{place}'. Using default coordinates.")
            return 28.6519, 77.2315, place
    except Exception as e:
        print(f"Geocoding failed ({e}). Using default coordinates.")
        return 28.6519, 77.2315, place


def get_place_from_user_and_geocode_for_web(place: str):
    """Geocode a provided place name (non-interactive) and return lat, lon, display name."""
    if not place:
        place = "New Delhi"
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(place)}&count=1"
    try:
        r = requests.get(geo_url, timeout=10)
        r.raise_for_status()
        res = r.json()
        results = res.get('results') or []
        if results:
            first = results[0]
            lat = first.get('latitude')
            lon = first.get('longitude')
            name = first.get('name') or place
            country = first.get('country')
            display_name = f"{name}, {country}" if country else name
            return lat, lon, display_name
        else:
            return 28.6519, 77.2315, place
    except Exception:
        return 28.6519, 77.2315, place


if __name__ == '__main__':
    lat, lon, place_display = get_place_from_user_and_geocode()
    fetch_and_process(latitude=lat, longitude=lon, place_name=place_display)
