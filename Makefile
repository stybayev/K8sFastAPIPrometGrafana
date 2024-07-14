run-dev:
	docker-compose -f docker-compose.dev.yml up --build

stop-dev:
	docker-compose -f docker-compose.dev.yml down

test:
	pytest tests/unit -p no:warnings

del-all:
	docker system prune -a
