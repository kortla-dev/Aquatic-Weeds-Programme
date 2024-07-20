"""
This file is the entry point into the system. It is where the User Interface is created and managed.
"""

from typing import Optional

from dash import Dash, callback, html, dcc, Input, State, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# used by placeholder graph
df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)

# NOTE: Stylesheets defined in assets/ are automatically loaded
app = Dash(
    __name__,
    # NOTE: there are multiple preset themes, you can see them at
    # https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/
    external_stylesheets=[dbc.themes.ZEPHYR],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# NOTE: this exposes flask and allows us to debug the application
server = app.server

# used to remove all the whitespace around graphs
fig_margins = {"t": 0, "b": 0, "l": 0, "r": 0}

# NOTE: we use the dbc.Row and dbc.Col to support mobile and desktop
# see https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/ for more information
app.layout = dbc.Container(
    id="core-container",
    children=[
        # div wrapper that will be used to display invalid input messages
        dbc.Row(
            dbc.Col(
                html.Div(
                    id="inpt-val-msg-wrapper", children="Invalid input messages go here"
                )
            )
        ),
        # container for the graph and user input
        dbc.Row(
            id="graph-input-container",
            children=[
                # This contains the graph
                dbc.Col(
                    children=[dcc.Graph(id="graph-content")],
                ),
                # This contains the input fields and submition button
                dbc.Col(
                    [
                        # TODO: add tooltips to the inputs
                        dbc.InputGroup(
                            children=[
                                dbc.InputGroupText("input 1"),
                                dbc.Input(id="input-1", type="text"),
                            ],
                        ),
                        dbc.InputGroup(
                            children=[
                                dbc.InputGroupText("input 2"),
                                dbc.Input(id="input-2", type="text"),
                            ]
                        ),
                        dbc.InputGroup(
                            children=[dbc.Button(id="button123", children="hello?")],
                        ),
                    ]
                ),
            ],
        ),
    ],
    fluid=True,
)


@callback(
    Output("graph-content", "figure"),
    [Input("button123", "n_clicks")],
    [
        State("input-1", "value"),
        State("input-2", "value"),
        State("inpt-val-msg-wrapper", "children"),
    ],
)
def get_prediction(
    n_clicks: Optional[int], input1, input2, val_msg: Optional[str]
) -> go.Figure:
    """tbd"""

    # TODO: load a empty graph of the dam
    # loads a default graph
    if n_clicks is None:
        fig = px.line(df[df.country == "Canada"], x="year", y="pop")
        fig.update_layout(margin=fig_margins)

        return fig

    # HACK: i don't know if this is a good way to do it
    # if there is a invalid input message the graph will not be updated
    if val_msg:
        raise PreventUpdate

    # TODO: call request a prediction from the Coordinator
    fig = px.line(df[df.country == "Germany"], x="year", y="pop")
    fig.update_layout(margin=fig_margins)

    return fig


if __name__ == "__main__":
    # NOTE: debug=True should not be sent to production
    app.run(debug=True)
