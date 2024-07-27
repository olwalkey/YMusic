FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache ffmpeg \
    && apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev \
    && pip install --upgrade pip
COPY ./assets/app.py ./assets/downloader.py ./assets/db.py ./assets/config.py ./server-requirements.txt ./config.yaml /app/

RUN pip install --trusted-host pypi.python.org -r server-requirements.txt \
    && apk --purge del build-deps

EXPOSE 5000

ENV NAME World

#CMD ["fastapi", "run", "code/app.py" '--port', '80', '--proxy-headers']
CMD ["python", "app.py"]
