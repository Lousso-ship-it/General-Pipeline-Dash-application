
import time
import requests
import pandas as pd
from typing import List

WDI_BASE = "https://api.worldbank.org/v2"

def fetch_indicator(countries: List[str], indicator: str, start: int=2000, end: int=2024, sleep=0.1) -> pd.DataFrame:
    dfs = []
    per_page = 20000
    for c in countries:
        url = f"{WDI_BASE}/country/{c}/indicator/{indicator}?format=json&per_page={per_page}&date={start}:{end}"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        js = r.json()
        if not isinstance(js, list) or len(js) < 2:
            continue
        rows = js[1] or []
        for row in rows:
            val = row.get("value")
            date = row.get("date")
            ind_name = (row.get("indicator") or {}).get("value")
            if date is None:
                continue
            dfs.append({
                "country": (row.get("country") or {}).get("id"),
                "country_name": (row.get("country") or {}).get("value"),
                "code": indicator,
                "indicator_name": ind_name,
                "date": int(date),
                "value": None if val is None else float(val),
            })
        time.sleep(sleep)
    if not dfs:
        return pd.DataFrame(columns=["country","country_name","code","indicator_name","date","value"])
    return pd.DataFrame(dfs)

def fetch_many(countries: List[str], indicators: List[str], start: int=2000, end: int=2024) -> pd.DataFrame:
    frames = []
    for ind in indicators:
        frames.append(fetch_indicator(countries, ind, start=start, end=end))
    if not frames:
        return pd.DataFrame(columns=["country","country_name","code","indicator_name","date","value"])
    return pd.concat(frames, ignore_index=True)
