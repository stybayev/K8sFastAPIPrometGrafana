run-dev:
	docker-compose -f docker-compose.dev.yml up --build

stop-dev:
	docker-compose -f docker-compose.dev.yml down

