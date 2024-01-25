'''
Базовая версия API для работы с HTTP-интерфейсами. Данный пример написан для работы с бд 1С
Логика работы с HTTP-интерфейсом бд вынесена в модуль main.
'''


from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Union, List, Dict, Any, Annotated
from pydantic import BaseModel, ValidationError
from main import BaseResource
import os
from dotenv import load_dotenv
import logging
import secrets

# Добавил отдельный логгер, но, честно говоря, не совсем пока понял как правильно создать второй экземпляр логгера
logger = logging.getLogger()
logger.addHandler(logging.FileHandler('inserver.log'))

logging.basicConfig(filename='inserver.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filemode='a')

app = FastAPI()
# конфиденциальные данные хранятся в переменных среды
load_dotenv()

site = os.getenv('API_SITE')
username = os.getenv('API_USERNAME')
password = os.getenv('API_PASSWORD')

client_username = os.getenv('API_CLIENT_USERNAME')
client_password = os.getenv('API_CLIENT_PASSWORD')

security = HTTPBasic()
# Модель получаемого запроса - {'warehouse': Str | None)
class Item(BaseModel):
    warehouse: Union[str, None]

# Модель возвращаемого запроса - {'warehouse': 'значение', 'prices': [...]} | {'prices': [...]}
class PriceList(BaseModel):
    warehouse: Union[str, None]
    prices: List[Dict[str, Any]]

# Проверка логина\пароля
def get_current_username(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    correct_username = secrets.compare_digest(credentials.username, client_username)
    correct_password = secrets.compare_digest(credentials.password, client_password)
    if not (correct_username and correct_password):
        logger.error("Unauthorized access attempt: %s", credentials.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка авторизации! Введите правильные логин/пароль или обратитесь к администратору.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Путь POST-запроса
@app.post("/query/", response_model=PriceList)
async def return_data(item: Item, client_username: Annotated[str, Depends(get_current_username)]):
    resource = BaseResource(site, username, password)
    data = resource.load_data(item.warehouse if item.warehouse else ' ')

    # Валидация ответа
    try:
        if item.warehouse:
            return PriceList(warehouse=item.warehouse, prices=data)
        else:
            return PriceList(prices=data)
    except ValidationError as e:
        logger.error("Validation error: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Invalid response from BaseResource")

