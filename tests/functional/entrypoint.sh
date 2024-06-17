#!/bin/bash

# Подождать доступности Elasticsearch
python3 tests/functional/utils/wait_for_es.py

# Подождать доступности Redis
python3 tests/functional/utils/wait_for_redis.py

# Запустить тесты
pytest tests/functional -p no:warnings


