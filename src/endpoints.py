from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import SERVICE_NAME
from db_connection import get_async_session
from schemas import NewsSchema

router = APIRouter(prefix=f"/{SERVICE_NAME}")

@router.post(f"/publish_news/", status_code=204)
async def translate_news(news: list[NewsSchema], session: AsyncSession = Depends(get_async_session)):
    """
    news: Список новостей об одной футбольной команде с ее веб-страницы.
    """
    print(news[0].translated_title)
    return