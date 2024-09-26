FROM python:3.12-alpine

WORKDIR /app


RUN apk add --no-cache ffmpeg 
RUN apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev 
RUN pip install --upgrade pip


COPY app.py /app/app.py
COPY utils/ /app/utils/
COPY server-requirements.txt /app/requirements.txt


RUN pip install --trusted-host pypi.python.org -r server-requirements.txt \
    && apk --purge del build-deps

EXPOSE 80

ENV NAME World

CMD ["fastapi", "run", "app.py", "--port", "80"]
