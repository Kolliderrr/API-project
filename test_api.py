import unittest
from fastapi.testclient import TestClient
from inserver import app  # Замените на фактический путь к вашему приложению
import requests

def load_client_credentials(client_name):
    import json
    with open('clients_config.json') as f:
        config = json.load(f)
        return config.get(client_name, None)


class TestYourApp(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_unauthorized(self):
        response = self.client.post("/query/", json={"warehouse": "example"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": 'Not authenticated'})  # Уточните ожидаемый результат

    def test_invalid_query(self):

        client_cred = load_client_credentials('client1')
        client_username = client_cred['username']
        client_password = client_cred['password']
        basic = requests.auth.HTTPBasicAuth(client_username, client_password)
        response = self.client.post("/query/", json={}, auth=basic)
        self.assertEqual(response.status_code, 422)  # Или другой код ошибки
        # Дополнительные проверки для обработки ошибок

    def test_valid_query(self):
        client_cred = load_client_credentials('client1')
        client_username = client_cred['username']
        client_password = client_cred['password']
        basic = requests.auth.HTTPBasicAuth(client_username, client_password)
        response = self.client.post("/query/", json={"warehouse": "example"}, auth=basic)
        self.assertEqual(response.status_code, 200)


    def test_invalid_order(self):
        client_cred = load_client_credentials('client1')
        client_username = client_cred['username']
        client_password = client_cred['password']
        basic = requests.auth.HTTPBasicAuth(client_username, client_password)
        response = self.client.post("/order/", json={"warehouse": None}, auth=basic)
        self.assertEqual(response.status_code, 422)


    def test_valid_order(self):
        client_cred = load_client_credentials('client1')
        client_username = client_cred['username']
        client_password = client_cred['password']
        basic = requests.auth.HTTPBasicAuth(client_username, client_password)
        response = self.client.post("/order/", json={
            'INN': '7721844807',
            'warehouse': 'Тюмень',
            'products': [
                {
                    'articul': '88-01401-SX',
                    'manufacturer': 'STELLOX',
                    'quantity': 2
                }]
        }, auth=basic)
        self.assertEqual(response.status_code, 200)