.PHONY: install build start start-dev stop logs ps clean test test-local test-deploy build-base build-client build-server

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
	docker compose exec -e PKM_API_BASE=http://localhost:7890 -T pkm-server bash -c "pip install -e . -q && pytest tests/ --cov=. --cov-branch  && coverage json -o /tmp/cov.json"; exit $$exit_code

test-local:
	docker compose up -d
	sleep 5
	@docker compose exec -e PKM_API_BASE=http://localhost:7890 -T pkm-server bash -c "pip install -e . -q && pytest tests/ --cov=. --cov-branch  && coverage json -o /tmp/cov.json"; \
	TEST_EXIT=$$?; \
	if [ $$TEST_EXIT -eq 0 ]; then \
		docker compose exec -T pkm-server bash -c 'python3 -c "import json; c=json.load(open(\"/tmp/cov.json\")); t=c[\"totals\"]; line=int(t[\"percent_covered\"]); branch=int(t.get(\"percent_branches_covered\",0)); print(f\"line={line}% branch={branch}%\"); exit(1 if line<75 or branch<55 else 0)"'; \
		COV_EXIT=$$?; \
		docker compose down; \
		exit $$COV_EXIT; \
	else \
		docker compose down; \
		exit $$TEST_EXIT; \
	fi

test-deploy:
	@chmod +x install.sh
	@timeout 180 ./install.sh snapshot || echo "install.sh failed"
	@echo "=== Checking Docker images ==="
	@docker images | grep pkm || echo "No pkm image found"
	@echo "=== Checking pip packages ==="
	@pip list | grep -i pkm || echo "No pkm package found"
	@echo "=== Checking installed files ==="
	@ls -la ~/.pkm/ || echo ".pkm directory not found"
