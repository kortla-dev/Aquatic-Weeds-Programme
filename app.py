"""
This file is the entry point into the system. It is where the User Interface is created and managed.
"""

import datetime as dt
from typing import Optional

import dash_bootstrap_components as dbc
from dash import Dash, callback, dcc, Input, State, Output, html, no_update
import pandas as pd
import plotly.express as px
from PIL import Image, ImageFile

from coordinator import PredictionType, predict
from typing import Optional

import dash_bootstrap_components as dbc
from dash import Dash, callback, dcc, Input, State, Output, html, no_update
import pandas as pd
import plotly.express as px
from PIL import Image
from cv2.typing import MatLike

from coordinator import predict

ZWSP = "\u200b"


# used by placeholder graph
df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)

# NOTE: Stylesheets defined in assets/ are automatically loaded
app = Dash(
    __name__,
    # NOTE: there are multiple preset themes, you can see them at
    # https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/
    external_stylesheets=[dbc.themes.SUPERHERO],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# NOTE: this exposes flask and allows us to debug the application
server = app.server

# used to remove all the whitespace around graphs
fig_margins = {"t": 0, "b": 0, "l": 0, "r": 0}

user_date_input = dbc.InputGroup(
    # style={"marginBottom": "10px"},
    children=[
        dbc.InputGroupText("Date"),
        dbc.Input(id="user-date", type="date"),
    ],
)

default_img = Image.open("./data/images/ref-img.jpg")

# NOTE: we use the dbc.Row and dbc.Col to support mobile and desktop
# see https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/ for more information
# App layout with Bootstrap components
app.layout = dbc.Container(
    id="core-container",
    style={"padding": "1rem", "paddingTop": "0.5rem"},
    children=[
        dbc.Row(
            id="graph-input-container",
            children=[
                dbc.Col(
                    style={
                        "padding": "0px",
                        "border": "1px solid #df6919",
                    },
                    children=[
                        dbc.Card(
                            [dbc.CardImg(id="predict-img", src=default_img)],
                            style={"maxWidth": "100%", "minWidth": "300px"},
                        ),
                    ],
                ),
                dbc.Col(
                    className="border border-secondary rounded",
                    style={"paddingTop": "10px", "paddingBottom": "10px"},
                    children=[
                        user_date_input,
                        html.Div(
                            id="date-val-msg", style={"color": "#f00"}, children=[ZWSP]
                        ),
                        dbc.InputGroup(
                            children=[dbc.Button(id="submit-btn", children="Submit")],
                        ),
                        html.P(id="predic-note-msg", children=[ZWSP]),
                    ],
                ),
            ],
        ),
    ],
    fluid=True,
)


# Callback to update graph and display validation messages
@callback(
    Output("predict-img", "src"),
    # New Code: Additional Outputs for validation messages
    Output("date-val-msg", "children"),
    Output("predic-note-msg", "children"),
    [Input("submit-btn", "n_clicks")],
    [State("user-date", "value")],
)
def get_prediction(n_clicks: Optional[int], user_date):

    date_val_msg = ZWSP
    predic_note_msg = ZWSP

    if n_clicks is None:
        return no_update

    if user_date is None:
        date_val_msg = "No Date Provided"
        return no_update, date_val_msg, predic_note_msg

    date: dt.date = dt.date.fromisoformat(user_date)

    predict_tuple = predict(date)
    predict_type = predict_tuple[0]
    predict_img = predict_tuple[1]

    if predict_type == PredictionType.PARTIAL:
        predic_note_msg = "Failed to get weater data returned partial prediction"

    # New Code: Clear validation messages upon successful validation
    return predict_img, date_val_msg, predic_note_msg


if __name__ == "__main__":
    app.run(debug=True)
