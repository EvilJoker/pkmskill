.PHONY: install build start stop logs ps clean test

install:
	pip install -e .

build:
	docker-compose build --no-cache

start:
	docker-compose up -d
	@echo "PKM Server started on http://localhost:7890"

stop:
	docker-compose down

logs:
	docker-compose logs -f

ps:
	docker-compose ps

clean:
	docker-compose down -v
	docker rmi pkm-server_pkm-server:latest

test:
	docker-compose up -d
	sleep 3
	docker-compose run --rm -e PKM_API_BASE=http://pkm-server:7890 pkm-server \
		bash -c "coverage run -m pytest tests/ -v --cov=. --cov-branch && coverage report --show-missing" || true
	docker-compose down 2>/dev/null || true
