import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div(children=[
    html.Br(),
    html.Br(),

    html.H2('''
        Projet réalisé dans le cadre du cours de modélisation stochastique.
    '''),

    html.Br(),
    html.Br(),

    html.Div(children='''
    JOSSET Julien
        GLASSER Emilie
        BAZIRE Martin
    '''),
    html.Br(),

    html.Div(children='''
        GLASSER Emilie
    '''),
    html.Br(),

    html.Div(children='''
        BAZIRE Martin
    ''')
])
