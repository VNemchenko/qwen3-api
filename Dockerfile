FROM python:3.11-slim

WORKDIR /app

RUN apt update && apt install -y build-essential cmake curl && \
    pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
