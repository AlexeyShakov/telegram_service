from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import SERVICE_NAME, CHANNEL_NAME
from db.db_connection import get_async_session
from utils.handler import TelegramBotHandler
from utils.schemas import NewsSchema


router = APIRouter(prefix=f"/api/{SERVICE_NAME}")

@router.post(f"/publish_news/", status_code=204)
async def publish_news(news: list[NewsSchema], session: AsyncSession = Depends(get_async_session)):
    """
    news: Список новостей об одной футбольной команде с ее веб-страницы.
    """
    bot_handler = TelegramBotHandler(CHANNEL_NAME, news, session)
    await bot_handler.handle_posting_news()
    return