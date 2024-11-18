FROM python:3.12-bookworm

WORKDIR /workspace

COPY . .

RUN pip install --no-cache-dir --upgrade -r server-requirements.txt


EXPOSE 8080

CMD ["python3", "app.py", "--log-level=DEBUG"]

