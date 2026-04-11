.PHONY: install build start start-dev stop logs ps clean test

install:
	pip install -e .

build:
	docker-compose build --no-cache

start:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "PKM Server started (production) on http://localhost:8890"

start-dev:
	docker-compose -f docker-compose.yml build
	docker-compose -f docker-compose.yml up -d
	@echo "PKM Server started (dev) on http://localhost:8890"

stop:
	docker-compose -f docker-compose.yml down
	docker-compose -f docker-compose.prod.yml down

logs:
	docker-compose -f docker-compose.yml logs -f

ps:
	docker-compose -f docker-compose.yml ps

clean:
	docker-compose -f docker-compose.yml down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker rmi pkm-server_pkm-server:latest || true

test:
	docker-compose -f docker-compose.yml up -d
	sleep 3
	docker-compose -f docker-compose.yml run --rm -e PKM_API_BASE=http://pkm-server:7890 pkm-server \
		bash -c "coverage run -m pytest tests/ -v --cov=. --cov-branch && coverage report --show-missing" || true
	docker-compose -f docker-compose.yml down 2>/dev/null || true
