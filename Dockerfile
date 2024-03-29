FROM python:alpine

WORKDIR /app

COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/src

CMD [ "python", "main.py" ]