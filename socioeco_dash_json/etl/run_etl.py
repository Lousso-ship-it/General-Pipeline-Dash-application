
import json
from typing import List, Set
from etl.worldbank import fetch_many
from etl.db import get_conn, init_db, upsert_raw


DB_PATH = "data/socioeco.db"
COUNTRIES_JSON = "config/countries.json"
COMPOSITES_JSON = "config/composites.json"
START_YEAR = 2000
END_YEAR = 2024

def resolve_all_indicator_codes(composites_json: str) -> List[str]:
    with open(composites_json, "r") as f:
        comps = json.load(f)
    codes: Set[str] = set()
    for _, spec in comps.items():
        for c in spec.get("components", []):
            codes.add(c["code"])
    return sorted(codes)

def main():
    with open(COUNTRIES_JSON, "r") as f:
        countries = json.load(f)["countries"]
    indicators = resolve_all_indicator_codes(COMPOSITES_JSON)
    print(f"Fetching {len(indicators)} indicators for countries: {countries}")
    df = fetch_many(countries, indicators, start=START_YEAR, end=END_YEAR)
    conn = get_conn(DB_PATH)
    init_db(conn)
    n = upsert_raw(conn, df.to_dict("records"))
    conn.close()
    print(f"Upserted {n} raw rows into {DB_PATH}")

if __name__ == "__main__":
    main()
