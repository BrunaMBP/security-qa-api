FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py database.py ./

RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]