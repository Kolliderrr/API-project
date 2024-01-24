import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Any
import ujson
import logging

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filename='1Clog.log', filemode='w')

class BaseResource:
    def __init__(self, site: str, username: str, password: str):
        self.site = site
        self.basic = HTTPBasicAuth(username, password)

    def load_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            json_data = ujson.dumps(data)
            response = requests.post(self.site, json=json_data, auth=self.basic)
            response.raise_for_status()  # Поднимает исключение, если статус HTTP не успешен
            return response.json()
        except requests.RequestException as e:
            print(f"Error during request: {e}")
            return {}

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()

    site = os.getenv('API_SITE')
    username = os.getenv('API_USERNAME')
    password = os.getenv('API_PASSWORD')

    resource = BaseResource(site, username, password)
    data = resource.load_data({})

    with open('data.json', 'w') as f:
        ujson.dump(data, f)