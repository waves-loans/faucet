FROM python:3.8.5-slim

RUN apt-get update && apt-get -y install gcc

WORKDIR /app
COPY . /app

RUN pip3 install --no-cache-dir -r requirements.txt


EXPOSE 8080

CMD ["python3","app.py"]
