"""The functionality of the coordinator in defined in this file"""

import os
import ast
from enum import Enum
from typing import List, TypedDict, Tuple
import datetime as dt
from cv2.typing import MatLike
import requests
import pandas as pd
import joblib
import requests_cache
from PIL import Image, ImageFile
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import cv2
import numpy as np


class PredictionType(Enum):
    """This enum represents the completeness of the prediciton"""

    PARTIAL = 1
    FULL = 2


def get_weather_data(date: dt.date) -> Tuple[PredictionType, pd.DataFrame]:
    """Retrieves weather data for a given date.

    Args:
        date (tbd): The date for which to retrieve weather data.

    Returns:
        pd.DataFrame: A DataFrame containing the weather data returned by the API.

    Raises:
        requests.RequestException: If the API request fails, an exception is raised.
    """

    # Setup caching and retry mechanism
    cache_session = requests_cache.CachedSession(".cache", expire_after=-1)

    # Retry configuration for HTTP requests
    retry_strategy = Retry(
        total=5,
        backoff_factor=0.2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],  # Updated this argument
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    cache_session.mount("https://", adapter)
    cache_session.mount("http://", adapter)

    # Define the Open-Meteo API URL and parameters
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": -25.7257,
        "longitude": 27.8483,
        "start_date": date.isoformat(),
        "end_date": date.isoformat(),
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "rain_sum",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "wind_direction_10m_dominant",
            "shortwave_radiation_sum",
            "surface_pressure_min",
            "surface_pressure_max",
            "relative_humidity_2m_min",
            "relative_humidity_2m_max",
        ],
        "timezone": "auto",
    }

    # Make the API request
    response = cache_session.get(url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        print("response was not 200")

        data = pd.read_csv("./data/partial_prediction_data.csv")
        return (PredictionType.PARTIAL, data)

    # Parse JSON data
    data = response.json()
    daily = data.get("daily", {})

    # Prepare the daily data into a DataFrame
    daily_data = {
        "temperature_2m_max": daily.get("temperature_2m_max", []),
        "temperature_2m_min": daily.get("temperature_2m_min", []),
        "temperature_2m_mean": daily.get("temperature_2m_mean", []),
        "precipitation_sum": daily.get("precipitation_sum", []),
        "rain_sum": daily.get("rain_sum", []),
        "wind_speed_10m_max": daily.get("wind_speed_10m_max", []),
        "wind_gusts_10m_max": daily.get("wind_gusts_10m_max", []),
        "wind_direction_10m_dominant": daily.get("wind_direction_10m_dominant", []),
        "shortwave_radiation_sum": daily.get("shortwave_radiation_sum", []),
        "surface_pressure_min": daily.get("surface_pressure_min", []),
        "surface_pressure_max": daily.get("surface_pressure_max", []),
        "relative_humidity_2m_min": daily.get("relative_humidity_2m_min", []),
        "relative_humidity_2m_max": daily.get("relative_humidity_2m_max", []),
    }

    return (PredictionType.FULL, pd.DataFrame(data=daily_data))


#########################################
# PREDICTION HELPERS
#########################################


def predict_bounding_boxes(weather_data: List[float], num_boxes: int) -> List[float]:

    model = joblib.load("./data/model/bounding_box_model.pkl")

    # Predict the flattened bounding boxes
    prediction = model.predict([weather_data])[0]

    # Extract the bounding boxes from the flattened prediction
    bounding_boxes = []
    for i in range(num_boxes):
        start_index = i * 4
        end_index = start_index + 4
        if end_index <= len(prediction):
            box = prediction[start_index:end_index]
            bounding_boxes.append(tuple(map(int, box)))
        else:
            bounding_boxes.append(
                (0, 0, 0, 0)
            )  # Default value if prediction length is shorter

    return bounding_boxes


def draw_bounding_boxes(image: MatLike, bounding_boxes):
    image_with_boxes = image.copy()
    for x, y, w, h in bounding_boxes:
        cv2.rectangle(
            image_with_boxes, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2
        )
    return image_with_boxes


# Function to process input weather data and generate bounding box image
def process_and_visualize(weather_data, reference_image_path, output_folder, date):
    num_boxes = 1587

    # Predict bounding boxes using the model
    predicted_boxes = predict_bounding_boxes(weather_data, num_boxes)

    # Load the reference image
    reference_image = cv2.imread(reference_image_path)
    if reference_image is None:
        print(
            f"Error: Reference image not found or unable to load at path {reference_image_path}"
        )
        return

    # Draw bounding boxes on the reference image
    image_with_boxes = draw_bounding_boxes(reference_image, predicted_boxes)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save the image
    output_image_path = os.path.join(output_folder, f"predic-img.png")
    cv2.imwrite(output_image_path, image_with_boxes)


def predict(data: dt.date) -> Tuple[PredictionType, ImageFile.ImageFile]:
    """Predicts the outcome based on user input and returns a tuple of prediction type and results.

    Args:
        user_input (UserInput): The input data for making a prediction.

    Returns:
        Tuple[PredictionType, pd.DataFrame]: A tuple containing:
            - PredictionType: Indicates the completeness of the prediction.
            - pd.DataFrame: A DataFrame containing prediction results.
    """

    weather_data_tuple = get_weather_data(data)

    prediction_type: PredictionType = weather_data_tuple[0]
    weather_data: pd.DataFrame = weather_data_tuple[1].to_numpy().flatten().tolist()

    ref_img_path = "./data/images/ref-img.jpg"
    output_path = ".output"
    date = data.isoformat()

    process_and_visualize(weather_data, ref_img_path, output_path, date)

    predic_img = Image.open("./.output/predic-img.png")
    return (prediction_type, predic_img)
