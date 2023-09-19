# Виберіть базовий образ, який містить Python та інше необхідне ПЗ
FROM python:3.10.11

# Встановлення робочого каталогу контейнера
WORKDIR /app

# Скопіюйте файли залежностей проекту (наприклад, requirements.txt) в контейнер
COPY requirements.txt requirements.txt

# Встановлення залежностей
RUN pip install -r requirements.txt

# Копіювання всіх файлів вашого додатку в контейнер
COPY . .

# Вказати команду для запуску вашого додатку FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]