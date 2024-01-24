from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Union, List, Dict, Any, Annotated
from pydantic import BaseModel, ValidationError
from main import BaseResource
import os
from dotenv import load_dotenv
import logging
import secrets

logging.basicConfig(filename='inserver.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filemode='a')

app = FastAPI()

load_dotenv()

site = os.getenv('API_SITE')
username = os.getenv('API_USERNAME')
password = os.getenv('API_PASSWORD')

client_username = os.getenv('API_CLIENT_USERNAME')
client_password = os.getenv('API_CLIENT_PASSWORD')

security = HTTPBasic()

class Item(BaseModel):
    warehouse: Union[str, None]


class PriceList(BaseModel):
    prices: List[Dict[str, Any]]


# Dependency to get current username and password
def get_current_username(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    correct_username = secrets.compare_digest(credentials.username, client_username)
    correct_password = secrets.compare_digest(credentials.password, client_password)
    if not (correct_username and correct_password):
        logging.error("Unauthorized access attempt: %s", credentials.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка авторизации! Введите правильные логин/пароль или обратитесь к администратору.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.post("/query/", response_model=PriceList)
async def return_data(item: Item, client_username: Annotated[str, Depends(get_current_username)]):
    resource = BaseResource(site, username, password)
    data = resource.load_data(item.warehouse if item.warehouse else ' ')

    # Валидация ответа
    try:
        return PriceList(prices=data)
    except ValidationError as e:
        logging.error("Validation error: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Invalid response from BaseResource")

