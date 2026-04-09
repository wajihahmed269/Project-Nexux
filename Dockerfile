FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p memory/tasks memory/checkpoints memory/logs

EXPOSE 8000

CMD ["python", "dashboard/server.py", "--host", "0.0.0.0", "--port", "8000"]
