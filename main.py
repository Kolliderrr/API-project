import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Any
import ujson
import logging
from typing import Union
from API_models import Item, Order, Product



logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filename='1Clog.log', filemode='a')

class BaseResource:
    def __init__(self, site: str, username: str, password: str):
        self.site = site
        self.basic = HTTPBasicAuth(username, password)

    def load_data(self, data: Union[Item, str]) -> Dict[str, Any]:
        try:
            if not isinstance(data, str):
                json_data = data.model_dump_json()
                response = requests.post(self.site + 'remains/products/', json=json_data, auth=self.basic)
            else:
                response = requests.post(self.site + 'remains/products/', json=ujson.dumps({}), auth=self.basic)
            response.raise_for_status()  # Поднимает исключение, если статус HTTP не успешен
            return response.json()
        except requests.RequestException as e:
            logging.error(e, exc_info=True)
            return {}

    def create_order(self, data: Order) -> Dict[str, Any]:
        try:
            dict_data = data.model_dump()
            response = requests.post(self.site + 'selling/order/', json=dict_data, auth=self.basic)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e_order:
            logging.error(e_order, exc_info=True)
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