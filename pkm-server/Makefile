.PHONY: install build start start-dev stop logs ps clean test build-base build-client build-server

install:
	pip install -e .

build-client:
	pip install build
	rm -rf dist/*.whl dist/*.tar.gz
	python -m build
	mv dist/*.whl dist/pkm-0.0.0-py3-none-any.whl

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

build-server:
	docker build --cache-from ghcr.io/eviljoker/pkm:base-latest -t ghcr.io/eviljoker/pkm:snapshot .

build-base:
	docker build -t ghcr.io/eviljoker/pkm:base-latest -f Dockerfile.base .
	docker push ghcr.io/eviljoker/pkm:base-latest

test:
	docker compose up -d
	sleep 5
	docker compose exec -e PKM_API_BASE=http://localhost:7890 -T pkm-server bash -c "pip install -e . -q && pytest tests/ --cov=. --cov-branch --ignore=tests/test_install.py && coverage json -o /tmp/cov.json"; exit $$exit_code
