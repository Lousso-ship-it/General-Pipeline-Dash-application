
import os
import json
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "data/socioeco.db")
COMPOSITES_JSON = os.environ.get("COMPOSITES_JSON", "config/composites.json")

def read_table(query: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def load_composite_names():
    with open(COMPOSITES_JSON, "r") as f:
        comps = json.load(f)
    return list(comps.keys())

app = Dash(__name__)
app.title = "Socio-Economic Dashboard (SQLite, JSON)"

# preload options from DB (created by ETL)
raw_codes_df = read_table("SELECT DISTINCT code, indicator_name FROM raw_values ORDER BY code")
raw_codes = raw_codes_df["code"].tolist()
code_to_name = dict(zip(raw_codes_df["code"], raw_codes_df["indicator_name"]))

countries_df = read_table("SELECT DISTINCT country, country_name FROM raw_values ORDER BY country")
countries = countries_df["country"].tolist()
country_to_name = dict(zip(countries_df["country"], countries_df["country_name"]))

composite_names = load_composite_names()

app.layout = html.Div([
    html.H2("Socio-Economic ETL → SQLite → Dash (JSON)"),
    dcc.Tabs([
        dcc.Tab(label="Bibliothèque des composantes", children=[
            html.Div([
                html.Label("Indicateur brut (code WDI)"),
                dcc.Dropdown(options=[{"label": f"{c} – {code_to_name.get(c,'')}", "value": c} for c in raw_codes],
                             value=raw_codes[0] if raw_codes else None,
                             id="comp-code"),
                html.Label("Pays"),
                dcc.Dropdown(options=[{"label": f"{c} – {country_to_name.get(c,'')}", "value": c} for c in countries],
                             value=countries[:5],
                             id="comp-countries",
                             multi=True),
                dcc.Graph(id="comp-graph")
            ], style={"padding":"10px"}),
        ]),
        dcc.Tab(label="Dashboard composites", children=[
            html.Div([
                html.Label("Indicateur composite"),
                dcc.Dropdown(options=[{"label": c, "value": c} for c in composite_names],
                             value=composite_names[0] if composite_names else None,
                             id="compst-name"),
                html.Label("Pays"),
                dcc.Dropdown(options=[{"label": f"{c} – {country_to_name.get(c,'')}", "value": c} for c in countries],
                             value=countries[:5],
                             id="compst-countries",
                             multi=True),
                dcc.Graph(id="compst-graph")
            ], style={"padding":"10px"}),
        ])
    ])
])

@app.callback(
    Output("comp-graph", "figure"),
    Input("comp-code", "value"),
    Input("comp-countries", "value"),
)
def update_component_graph(code, selected_countries):
    if code is None or not selected_countries:
        return px.line()
    in_clause = ",".join([f"'{c}'" for c in selected_countries])
    q = f"""
        SELECT country, date, value FROM raw_values
        WHERE code = '{code.replace("'", "''")}' AND country IN ({in_clause})
        ORDER BY date
    """
    df = read_table(q)
    fig = px.line(df, x="date", y="value", color="country", markers=True, title=code_to_name.get(code, code))
    return fig

@app.callback(
    Output("compst-graph", "figure"),
    Input("compst-name", "value"),
    Input("compst-countries", "value"),
)
def update_composite_graph(comp_name, selected_countries):
    if comp_name is None or not selected_countries:
        return px.line()
    in_clause = ",".join([f"'{c}'" for c in selected_countries])
    q = f"""
        SELECT country, date, value FROM composite_values
        WHERE composite = '{comp_name.replace("'", "''")}'
          AND country IN ({in_clause})
        ORDER BY date
    """
    df = read_table(q)
    fig = px.line(df, x="date", y="value", color="country", markers=True, title=comp_name)
    return fig

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)
