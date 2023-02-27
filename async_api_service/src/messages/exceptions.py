from pydantic import BaseModel


class ErrorMessages(BaseModel):
    NOT_FOUND: str = 'Не найдено'


messages = ErrorMessages()
