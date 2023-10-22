import asyncio
from src.config import console_logger, TELEGRAM_QUEUE, RABBITMQ_USER, RABBITMQ_PASS, CHANNEL_NAME

from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage
import base64
from src.utils.schemas import NewsSchema
import json

from src.utils.handler import TelegramBotHandler


async def validate(news: list[dict]) -> list[NewsSchema]:
    return [NewsSchema(id=el["id"], link=el["link"], translated_title=el["translated_title"],
                       translated_short_description=el["translated_short_description"])
            for el in news]


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        news = json.loads(base64.b64decode(message.body).decode())
        validated_news = await validate(news)
        bot_handler = TelegramBotHandler(CHANNEL_NAME, validated_news)
        await bot_handler.handle_posting_news()


async def main() -> None:
    console_logger.info("В ожидании сообщений. Для выхода нажать CTRL+C")

    connection = await connect(f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@localhost/")

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(
            TELEGRAM_QUEUE,
            durable=True,
        )

        await queue.consume(on_message)
        await asyncio.Future()  # для того, чтобы программа работала бесконечно


if __name__ == "__main__":
    asyncio.run(main())
