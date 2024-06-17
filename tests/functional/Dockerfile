FROM python:3.10-slim

WORKDIR /tests

# Установка зависимостей
COPY requirements.txt /tests/
RUN pip install -r requirements.txt

# Установка netcat-openbsd для скриптов ожидания
RUN apt-get update && apt-get install -y netcat-openbsd

# Копирование тестового кода
COPY . /tests/

# Копирование и установка прав для entrypoint.sh
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Установка entrypoint.sh как точки входа
ENTRYPOINT ["entrypoint.sh"]
CMD ["pytest", "tests/functional"]