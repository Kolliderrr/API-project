'''
Базовая версия API для работы с HTTP-интерфейсами. Данный пример написан для работы с бд 1С
Логика работы с HTTP-интерфейсом бд вынесена в модуль main.
'''
from API_models import Item, PriceList, Order, OrderConfirmation

from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Union, List, Dict, Any, Annotated
from pydantic import BaseModel, ValidationError
from main import BaseResource
from dotenv import load_dotenv
import logging, json, secrets, os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


def load_client_credentials(client_name):
    with open('clients_config.json') as f:
        config = json.load(f)
        return config.get(client_name, None)


# Добавил отдельный логгер, но, честно говоря, не совсем пока понял как правильно создать второй экземпляр логгера
logger = logging.getLogger()
logger.addHandler(logging.FileHandler('inserver.log'))

logging.basicConfig(filename='inserver.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='a')

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(docs_url="/documentation", redoc_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# конфиденциальные данные хранятся в переменных среды
load_dotenv()

site = os.getenv('API_SITE')
username = os.getenv('API_USERNAME')
password = os.getenv('API_PASSWORD')

client_username = os.getenv('API_CLIENT_USERNAME')
client_password = os.getenv('API_CLIENT_PASSWORD')

security = HTTPBasic()


# Проверка логина\пароля
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    client_credentials = load_client_credentials(credentials.username)
    if client_credentials is None:
        logger.error("Unauthorized access attempt: %s", credentials.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка авторизации! Введите правильные логин/пароль или обратитесь к администратору.",
            headers={"WWW-Authenticate": "Basic"},
        )
    correct_username = secrets.compare_digest(credentials.username, client_credentials["username"])
    correct_password = secrets.compare_digest(credentials.password, client_credentials["password"])
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
@limiter.limit("5/minute")
async def return_data(request: Request, item: Item, client_username: Annotated[str, Depends(get_current_username)]):
    resource = BaseResource(site, username, password)
    data = resource.load_data(item if item.warehouse else ' ')

    # Валидация ответа
    try:
        if item.warehouse:
            return PriceList(warehouse=item.warehouse, prices=data)
        else:
            return PriceList(warehouse='', prices=data)
    except ValidationError as e:
        logger.error("Validation error: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Invalid response from BaseResource")


@app.post("/order/", response_model=OrderConfirmation)
@limiter.limit("5/minute")
async def create_order(request: Request, order: Order, client_username: Annotated[str, Depends(get_current_username)]):
    resource = BaseResource(site, username, password)
    data = resource.create_order(order)

    try:
        return OrderConfirmation(**data)
    except ValidationError as e_1:
        logger.error('Validation error: %s', str(e_1))
        raise HTTPException(status_code=500, detail=f'Invalid response from BaseResource')


