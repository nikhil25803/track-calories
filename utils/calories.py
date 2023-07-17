from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

# Loading the required variables from the .env file
NUTRITIONIX_APIKEY = os.environ.get("NUTRITIONIX_APIKEY")
NUTRITIONIX_APPID = os.environ.get("NUTRITIONIX_APPID")

# URL to make the API call
URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"

# Required header needs to be passed
HEADERS = {
    "x-app-id": f"{NUTRITIONIX_APPID}",
    "x-app-key": f"{NUTRITIONIX_APIKEY}",
    "x-remote-user-id": "0",
}


# Function to accept the text and return the calories corresponding to it - if not able to fetch it returns None
def calculate(query: str):
    BODY = {
        "query": f"{query}",
        "timezone": "US/Eastern",
    }
    try:
        response = requests.post(url=URL, headers=HEADERS, data=BODY)
        json_response = json.loads(response.text)
        data = json_response["foods"]
        calorie_data = {}
        for i in range(len(data)):
            food = data[i]
            calorie_data[f"{food['food_name']}"] = food["nf_calories"]
        total_calories = sum(calorie_data.values())
        return total_calories
    except:
        return None
