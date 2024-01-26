"""
Файл с описанием моделей валидации входящих и исходящих данных запросов

"""

from typing import Union, List, Dict, Any, Optional
from pydantic import BaseModel

# Модель получаемого запроса - {'warehouse': Str | None)
class Item(BaseModel):
    warehouse: Optional[str]

# Модель возвращаемого запроса - {'warehouse': 'значение', 'prices': [...]} | {'prices': [...]}

class PriceList(BaseModel):
    warehouse: Optional[str]
    prices: List[Dict[str, Any]]


class Product(BaseModel):
    articul: str
    manufacturer: str
    quantity: int


class Order(BaseModel):
    INN: str
    warehouse: str
    products: List[Product]


class OrderConfirmation(BaseModel):
    message: str
    order: str
