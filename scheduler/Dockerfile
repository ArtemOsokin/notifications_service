FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app/

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt  --no-cache-dir

COPY /src/ .

CMD python main.py