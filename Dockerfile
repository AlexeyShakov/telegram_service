FROM python:3.10

RUN mkdir /telegram_app

WORKDIR  /telegram_app

COPY ./telegram_service/requirements.txt /telegram_app

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y gettext
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY ./telegram_service .

COPY ./grpc_translations /telegram_app/grpc_translations

RUN pip install -e ./grpc_translations/
