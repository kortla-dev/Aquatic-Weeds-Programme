"""The functionality of the coordinator in defined in this file"""

from enum import Enum
from typing import TypedDict, Tuple
import requests
import pandas as pd


class PredictionType(Enum):
    """This enum represents the completeness of the prediciton"""

    PARTIAL = 1
    FULL = 2


class UserInput(TypedDict):
    """A type alias for a dictionary that represents user input.

    Example usage:
        var_name: UserInput = {
            'input1': 'example_value'
        }
    """

    input1: str


def transform_input(data: UserInput) -> pd.DataFrame:
    """Converts data from dict to pandas DataFrame"""

    df = pd.DataFrame()

    df["input1"] = data["input1"]

    return df


def partial_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """Returns the general predicton from model A"""
    return df


def full_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a full prediction from model B"""
    return df


def get_weather_data(date) -> pd.DataFrame:
    """Retrieves weather data for a given date.

    Args:
        date (tbd): The date for which to retrieve weather data.

    Returns:
        pd.DataFrame: A DataFrame containing the weather data returned by the API.

    Raises:
        requests.RequestException: If the API request fails, an exception is raised.
    """
    return pd.DataFrame()


def predict(data: UserInput) -> Tuple[PredictionType, pd.DataFrame]:
    """Predicts the outcome based on user input and returns a tuple of prediction type and results.

    Args:
        user_input (UserInput): The input data for making a prediction.

    Returns:
        Tuple[PredictionType, pd.DataFrame]: A tuple containing:
            - PredictionType: Indicates the completeness of the prediction.
            - pd.DataFrame: A DataFrame containing prediction results.
    """

    partial_predict: pd.DataFrame = transform_input(data)

    try:
        weather_data: pd.DataFrame = get_weather_data("date")

        full_df = pd.concat([partial_predict, weather_data], axis=1)
    except requests.RequestException:
        # if the api service is not available a partial prediction will be returned
        return (PredictionType.PARTIAL, partial_predict)

    full_predict: pd.DataFrame = full_prediction(full_df)

    return (PredictionType.FULL, full_predict)
