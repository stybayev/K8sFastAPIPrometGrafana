FROM --platform=linux/amd64 python:3.10-slim-buster

# Устанавливаем переменную окружения для отключения буферизации вывода
ENV PYTHONUNBUFFERED=1

# Задаем рабочую директорию
WORKDIR /ugc_service

# Копируем файл с зависимостями
COPY requirements.txt /ugc_service

# Обновляем pip и устанавливаем системные зависимости
RUN /usr/local/bin/python -m pip install --upgrade pip && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends gcc curl netcat && \
    pip install -r requirements.txt && \
    pip install --upgrade 'sentry-sdk[flask]' && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем исходный код в контейнер

COPY . /ugc_service

# Определяем команду запуска контейнера
CMD ["sh", "-c", "echo 'Starting Gevent WSGI Server...' && python ugc_service/pywsgi.py"]
