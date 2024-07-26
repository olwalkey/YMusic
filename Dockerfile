FROM python:3.12-alpine

WORKDIR /code

RUN apk add --no-cache ffmpeg \
    && apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev \
    && pip install --upgrade pip

COPY ./server-requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./assets/app.py ./assets/downloader.py ./assets/db.py ./assets/config.py  ./config.yaml /code/

EXPOSE 80

CMD ["fastapi", "run", "code/app.py" '--port', '80', '--proxy-headers']
