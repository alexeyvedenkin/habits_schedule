# Указываем базовый образ
FROM python:3.12

# Устанавливаем рабочую директорию в контейнере
WORKDIR /code

# Копируем файлы для Poetry
COPY pyproject.toml poetry.lock ./

# Устанавливаем Poetry
RUN pip install poetry
RUN poetry config virtualenvs.create false

# Установка зависимостей
RUN poetry install --no-root

# Копируем остальные файлы проекта в контейнер
COPY . .

# Открываем порт 8000 для взаимодействия с приложением
EXPOSE 8000

# Определяем команду для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
