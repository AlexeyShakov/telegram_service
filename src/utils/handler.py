import asyncio
from typing import Sequence
from datetime import date
import html2text
import aiofiles as aiofiles
from sqlalchemy import select

from src.config import BOT_TOKEN, logger
from src.db.db_connection import async_session_maker
from src.db.models import Error, Post
from src.utils.enums import StepNameChoice
from src.utils.schemas import NewsSchema
from telebot.async_telebot import AsyncTeleBot


class TelegramBotHandler:
    # Логику по работе с БД можно вынести в отдельных handler
    def __init__(self, channel_name: str, news: list[NewsSchema]) -> None:
        self.channel_name = channel_name
        self.news = news
        self.bot = AsyncTeleBot(BOT_TOKEN)
        self.event_loop = asyncio.get_running_loop()
        self.semaphore = asyncio.Semaphore(3)
        self.news_with_errors = []
        self.news_posted = []

    async def handle_posting_news(self):
        tasks = [asyncio.create_task(self.send_message(post)) for post in self.news]
        await asyncio.gather(*tasks)
        if self.news_posted:
            await self.set_success_date()
        if self.news_with_errors:
            await self.handle_news_with_errors()

    async def send_message(self, post: NewsSchema) -> None:
        message = await self._get_message(post)
        try:
            async with self.semaphore:
                await self.bot.send_message(self.channel_name, message)
                self.news_posted.append(post)
                # Делаем задержку специально, чтобы не было 429 ошибки
                await asyncio.sleep(10)
        except Exception:
            logger.exception("Ошибка получена при попытке отправить в телеграмм")
            self.news_with_errors.append(post)

    async def _get_message(self, post: NewsSchema) -> str:
        async with aiofiles.open('src/message_template.html', mode='r') as f:
            content = await f.read()
            message = content.format(
                translated_title=post.translated_title,
                translated_short_description=post.translated_short_description,
                link=post.link,
                id=post.id
            )
            # Т.к. html2text.html2text синхронная фукнция, то мы должны запускать ее по-другому, чтобы
            # не блокировать поток
            message_as_string = await self.event_loop.run_in_executor(None, html2text.html2text, message)
            return message_as_string

    async def handle_news_with_errors(self) -> None:
        async with async_session_maker() as session:
            posts = await self._get_posts_from_db(self.news_with_errors)
            query = select(Error).where(Error.step == StepNameChoice.SENDING_TO_TELEGRAM.name)
            result = await session.execute(query)
            error = result.scalars().first()
            for post in posts:
                post.error_id = error.id
            session.add_all(posts)
            await session.commit()

    async def set_success_date(self) -> None:
        async with async_session_maker() as session:
            posts = await self._get_posts_from_db(self.news_posted)
            for post in posts:
                post.success_date = date.today()
            session.add_all(posts)
            await session.commit()

    async def _get_posts_from_db(self, news: list[NewsSchema]) -> Sequence[Post]:
        async with async_session_maker() as session:
            news_ids = [post.id for post in news]
            post_query = select(Post).where(Post.id.in_(news_ids))
            result = await session.execute(post_query)
            return result.scalars().all()
