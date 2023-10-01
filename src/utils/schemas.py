from pydantic import BaseModel


class NewsSchema(BaseModel):
    id: int
    link: str
    translated_title: str
    translated_short_description: str
