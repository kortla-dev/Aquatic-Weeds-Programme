"""
This file is the entry point into the system. It is where the User Interface is created and managed.
"""

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# used by placeholder graph
df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)

# NOTE: Stylesheets defined in assets/ are automatically loaded
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)


app.layout = dbc.Container(
    id="core-container",
    children=[
        # div wrapper that will be used to display invalid input messages
        dbc.Row(
            html.Div(
                id="inpt-val-msg-wrapper", children="Invalid input messages go here"
            )
        ),
        # container for the graph and user input
        dbc.Row(
            id="figure-input-container",
            children=[
                # This contains the graph
                dbc.Col(
                    id="graph-content",
                    children=[
                        dcc.Graph(
                            # id="graph-content",
                            figure=px.line(
                                # placeholder graph
                                df[df.country == "Canada"],
                                x="year",
                                y="pop",
                            ),
                        )
                    ],
                ),
                # This contains the
                dbc.Col(
                    [
                        dbc.Row([dbc.Label("input 1"), dbc.Input(type="text")]),
                        dbc.Row([dbc.Label("input 2"), dbc.Input(type="text")]),
                    ]
                ),
            ],
        ),
    ],
    fluid=True,
)


# TODO: implement funciton to use @callback and return the prediction
def get_prediction():
    """tbd"""
    return None


if __name__ == "__main__":
    app.run(debug=True)
