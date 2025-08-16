
# Create venv & install deps, then run ETL, compute and app
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python etl\run_etl.py
python etl\compute.py
python app\app.py
