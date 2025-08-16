
import json
import pandas as pd
from typing import Dict, Any
from .db import get_conn, upsert_composite
from .normalize import min_max_normalize

def compute_composites(db_path: str="data/socioeco.db", composites_json: str="config/composites.json") -> None:
    conn = get_conn(db_path)
    raw = pd.read_sql_query("SELECT country, date, code, value FROM raw_values", conn)
    with open(composites_json, "r") as f:
        comps: Dict[str, Any] = json.load(f)

    all_rows = []
    for cname, spec in comps.items():
        components = spec.get("components", [])
        if not components:
            continue
        codes = [c["code"] for c in components]
        sub = raw[raw["code"].isin(codes)].copy()
        if sub.empty:
            continue
        frames = []
        for c in components:
            code = c["code"]
            invert = bool(c.get("invert", False))
            tmp = sub[sub["code"] == code].copy()
            if tmp.empty:
                continue
            tmp["norm"] = min_max_normalize(tmp, value_col="value", group_cols=("date",), invert=invert)
            frames.append(tmp[["country","date","norm"]].rename(columns={"norm": code}))
        if not frames:
            continue
        merged = None
        for f in frames:
            if merged is None:
                merged = f
            else:
                merged = merged.merge(f, on=["country","date"], how="outer")
        cols = [c["code"] for c in components if c["code"] in merged.columns]
        merged["value"] = merged[cols].mean(axis=1, skipna=True)
        merged["composite"] = cname
        for row in merged[["country","composite","date","value"]].itertuples(index=False):
            all_rows.append({"country": row.country, "composite": row.composite, "date": int(row.date), "value": None if pd.isna(row.value) else float(row.value)})
    if all_rows:
        upsert_composite(conn, all_rows)
    conn.close()

if __name__ == "__main__":
    compute_composites()
