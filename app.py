import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

from var_case import SIG_OBS_VALUES, SIG_ORG_VALUES, SIG_CONSTRUCTEUR, PRED_VARIABLES

# Initialisation de l'application Dash
app = dash.Dash(__name__)

# Mise en place de la mise en page de l'application
app.layout = html.Div([
    html.H1('Projet modélisation stochastique'),
    html.H2('Sélection des variables'),
    html.Label('SIG_ORGANE :'),
    dcc.Dropdown(
        id='sig-organe-dropdown',
        options=[{'label': col, 'value': col} for col in SIG_ORG_VALUES],
        value="None",
        multi=False
    ),
    html.Label('SIG_OBS :'),
    dcc.Dropdown(
        id='sig-obs-dropdown',
        options=[{'label': col, 'value': col} for col in SIG_OBS_VALUES],
        value="None",
        multi=False
    ),
    html.Label('CONSTRUCTEUR :'),
    dcc.Dropdown(
        id='sig-constructeur-dropdown',
        options=[{'label': col, 'value': col} for col in SIG_CONSTRUCTEUR_VALUES],
        value="None",
        multi=False
    ),
    html.H2('Résultats : '),
    html.H2(children='', id='specify-text', style={"color": "red", "text-decoration": "underline"}),
    dcc.Graph(id='graph-system-n1'),
    dcc.Graph(id='graph-system-n2'),
    dcc.Graph(id='graph-system-n3'),
    dcc.Graph(id='graph-odr-libelle'),
    dcc.Graph(id='graph-type-travail'),
])


# Callback pour la mise à jour des graphiques en fonction des variables sélectionnées
@app.callback(Output('graph-system-n1', 'figure'),
              Output('graph-system-n2', 'figure'),
              Output('graph-system-n3', 'figure'),
              Output('graph-odr-libelle', 'figure'),
              Output('graph-type-travail', 'figure'),
              Output('specify-text', 'children'),
              [Input('sig-organe-dropdown', 'value'),
               Input('sig-obs-dropdown', 'value'),
               Input('sig-constructeur-dropdown', 'value')])
def update_graph(sig_org, sig_obs):
    figures = []
    title = ""
    results = None # query julien script

    if "None" in [sig_org, sig_obs, sig_constructeur]:
        title += "Please specify : "
        if sig_org == "None":
            title += "SIG_ORG "
        if sig_obs == "None":
            title += "SIG_OBS "
        if sig_constructeur == "None":
            title += "SIG_CONSTRUCTEUR "
        results = {k: {"": 0.5} for k in PRED_VARIABLES}

    for graph in PRED_VARIABLES:
        if len(results[graph].keys()) >= 5:
            results[graph] = sorted(results[graph].items(), key=lambda _x: _x[1])
            x = results[graph].keys()[:5]
            y = results[graph].values()[:5]
            n = 5
        else:
            x = list(results[graph].keys())
            y = list(results[graph].values())
            n = len(x)

        data = [
            go.Bar(
                x=x,
                y=y
            )
        ]
        layout = go.Layout(
            title=f'{graph} :',
            font_family="Courier New",
            font_color="blue",
            title_font_family="Times New Roman",
            title_font_color="#1a1b1c",
            xaxis=dict(title=f'TOP {n}'),
            yaxis=dict(title="probability", range=[0, 1])
        )
        figure = {'data': data, 'layout': layout}
        figures.append(figure)
    if len(figures) >= 5:
        return \
            figures[0], \
            figures[1], \
            figures[2], \
            figures[3], \
            figures[4], \
            title
    else:
        None


# Exécution de l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True)
