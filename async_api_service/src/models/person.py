from models.base import BaseOrjsonModel


class Person(BaseOrjsonModel):
    id: str
    name: str
