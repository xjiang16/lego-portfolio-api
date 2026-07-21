import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("REBRICKABLE_API_KEY")

set_number = "10329"  # Tiny Plants
url = f"https://rebrickable.com/api/v3/lego/sets/{set_number}-1/"

headers = {
    "Authorization": f"key {API_KEY}"
}

response = requests.get(url, headers=headers)
print("Status code:", response.status_code)
print(response.json())