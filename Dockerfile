FROM python:3.11-alpine
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src/ .

ENTRYPOINT ["python", "main.py"]