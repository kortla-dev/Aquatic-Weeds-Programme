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
# App layout with Bootstrap components
app.layout = dbc.Container(
    id="core-container",
    children=[
        dbc.Row(
            id="graph-input-container",
            children=[
                dbc.Col(
                    children=[dcc.Graph(id="graph-content")],
                ),
                dbc.Col(
                    [
                        dbc.InputGroup(
                            children=[
                                dbc.InputGroupText("Input 1"),
                                dbc.Input(id="input-1", type="text"),
                            ],
                        ),
                        # New Code: Error message for Input 1
                        html.Div(id="input1-val-msg", style={"color": "red"}),

                        dbc.InputGroup(
                            children=[
                                dbc.InputGroupText("Input 2"),
                                dbc.Input(id="input-2", type="text"),
                            ]
                        ),
                        # New Code: Error message for Input 2
                        html.Div(id="input2-val-msg", style={"color": "red"}),

                        dbc.InputGroup(
                            children=[dbc.Button(id="button123", children="Submit")],
                        ),
                    ]
                ),
            ],
        ),
    ],
    fluid=True,
)

# Callback to update graph and display validation messages
@callback(
    Output("graph-content", "figure"),
    # New Code: Additional Outputs for validation messages
    Output("input1-val-msg", "children"),
    Output("input2-val-msg", "children"),
    [Input("button123", "n_clicks")],
    [State("input-1", "value"), State("input-2", "value")]
)
def get_prediction(n_clicks: Optional[int], input1, input2):
    # New Code: Variables to hold validation messages
    input1_msg, input2_msg = "", ""

    # Validate input1
    if not input1 or not input1.strip():
        input1_msg = "Input 1 is required."

    # Validate input2
    if not input2 or not input2.isdigit():
        input2_msg = "Input 2 must be a valid number."
    elif not (0 <= int(input2) <= 100):
        input2_msg = "Input 2 must be between 0 and 100."

    # If there are validation errors, return them without updating the graph
    if input1_msg or input2_msg:
        # New Code: Returning validation messages instead of updating the graph
        return dash.no_update, input1_msg, input2_msg

    # If all validations pass, update the graph
    fig = px.line(df[df.country == "Germany"], x="year", y="pop")
    fig.update_layout(margin=fig_margins)

    # New Code: Clear validation messages upon successful validation
    return fig, "", ""

if __name__ == "__main__":
    app.run(debug=True)
