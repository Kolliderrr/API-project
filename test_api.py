import unittest
from fastapi.testclient import TestClient
from inserver import app  # Замените на фактический путь к вашему приложению
from unittest.mock import patch

class TestYourApp(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_unauthorized(self):
        response = self.client.post("/query/", json={"warehouse": "example"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": 'Ошибка авторизации! Введите правильные логин/пароль или обратитесь к администратору.'})  # Уточните ожидаемый результат

    @patch('inserver.load_client_credentials', return_value={"username": "test_user", "password": "test_pass"})
    def test_invalid_query(self, mock_load_client_credentials):
        response = self.client.post("/query/", json={})
        self.assertEqual(response.status_code, 422)  # Или другой код ошибки
        # Дополнительные проверки для обработки ошибок

    @patch('inserver.load_client_credentials', return_value={"username": "test_user", "password": "test_pass"})
    def test_valid_query(self, mock_load_client_credentials):
        response = self.client.post("/query/", json={"warehouse": "example"})
        self.assertEqual(response.status_code, 200)

    @patch('inserver.load_client_credentials', return_value={"username": "test_user", "password": "test_pass"})
    def test_invalid_order(self, mock_load_client_credentials):
        response = self.client.post("/order/", json={"warehouse": None})
        self.assertEqual(response.status_code, 422)

    @patch('inserver.load_client_credentials', return_value={"username": "test_user", "password": "test_pass"})
    def test_valid_order(self, mock_load_client_credentials):
        response = self.client.post("/order/", json={
            'INN': '7721844807',
            'warehouse': 'Тюмень',
            'products': [
                {
                    'articul': '88-01401-SX',
                    'manufacturer': 'STELLOX',
                    'quantity': 2
                }]
        })
        self.assertEqual(response.status_code, 200)
