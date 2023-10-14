import asyncio
from typing import Optional

from grpc_service import telegram_pb2, telegram_pb2_grpc
import grpc

from src.config import logger, console_logger, GRPC_TRANSLATION_PORT, CHANNEL_NAME
from src.utils.schemas import NewsSchema
from src.utils.handler import TelegramBotHandler


class TelegramServicer(telegram_pb2_grpc.NewsTelegramServicer):
    async def GetNews(self, request: telegram_pb2.TranslatedNews, context) -> telegram_pb2.TranslatedNewsResponse:
        result = await self._validate_news(request)
        if not result:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Error while validating data!')
            return telegram_pb2.TranslatedNewsResponse()
        bot_handler = TelegramBotHandler(CHANNEL_NAME, result)
        await bot_handler.handle_posting_news()
        return telegram_pb2.TranslatedNewsResponse()

    async def _validate_news(self, news: telegram_pb2.TranslatedNews) -> Optional[list[NewsSchema]]:
        try:
            return [
                NewsSchema(id=int(post.id["id"]), link=post.link["link"], translated_title=post.translated_title["translated_title"],
                           translated_short_description=post.translated_short_description["translated_short_description"])
                for post in news.news]
        except Exception as e:
            logger.exception(f"При попытке валидировать данные возникла ошибка - {e}")
            return


async def serve():
    console_logger.info("Grpc-сервер поднят")
    server = grpc.aio.server()
    telegram_pb2_grpc.add_NewsTelegramServicer_to_server(TelegramServicer(), server)
    server.add_insecure_port(f"[::]:{GRPC_TRANSLATION_PORT}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
