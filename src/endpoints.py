from fastapi import APIRouter, Depends

from .config import SERVICE_NAME, CHANNEL_NAME
from src.utils.handler import TelegramBotHandler
from src.utils.schemas import NewsSchema


router = APIRouter(prefix=f"/api/{SERVICE_NAME}")

@router.post(f"/publish_news/", status_code=204)
async def publish_news(news: list[NewsSchema]):
    """
    news: Список новостей об одной футбольной команде с ее веб-страницы.
    """
    bot_handler = TelegramBotHandler(CHANNEL_NAME, news)
    await bot_handler.handle_posting_news()
    return