import asyncio
import html2text
import aiofiles as aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from config import BOT_TOKEN
from utils.schemas import NewsSchema
from telebot.async_telebot import AsyncTeleBot


class TelegramBotHandler:
    def __init__(self, channel_name: str, news: list[NewsSchema], session: AsyncSession) -> None:
        self.channel_name = channel_name
        self.news = news
        self.bot = AsyncTeleBot(BOT_TOKEN)
        self.session = session
        self.event_loop = asyncio.get_running_loop()

    async def handle_posting_news(self):
        tasks = [asyncio.create_task(self.send_message(post)) for post in self.news]
        await asyncio.gather(*tasks)

    async def send_message(self, post: NewsSchema) -> None:
        message = await self._get_message(post)
        await self.bot.send_message(self.channel_name, message)

    async def _get_message(self, post: NewsSchema) -> str:
        async with aiofiles.open('message_template.html', mode='r') as f:
            content = await f.read()
            message = content.format(
                translated_title=post.translated_title,
                translated_short_description=post.translated_short_description,
                link=post.link
            )
            # Т.к. html2text.html2text синхронная фукнция, то мы должны запускать ее по-другому, чтобы
            # не блокировать поток
            message_as_string = await self.event_loop.run_in_executor(None, html2text.html2text, message)
            return message_as_string
