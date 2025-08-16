
# Socio-Economic ETL → SQLite → Dash (JSON configs, no PyYAML)

## Pipeline
1) Extract WDI indicators (World Bank API) → SQLite (`data/socioeco.db`)
2) Compute 21 composites from JSON config → SQLite
3) Dash app reads SQLite and shows Components + Composites

## Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python etl\run_etl.py
python etl\compute.py
python app\app.py
```
Open http://127.0.0.1:8050
