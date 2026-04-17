.PHONY: install build start start-dev stop logs ps clean test test-deploy build-base build-client build-server status

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
	docker-compose -f docker-compose.yml up -d
	@echo "PKM Server started (production) on http://localhost:8890"

start-dev:
	docker-compose -f docker-compose.dev.yml build --no-cache
	docker-compose -f docker-compose.dev.yml up -d
	@echo "PKM Server started (dev) on http://localhost:7890"

status:
	@docker-compose -f docker-compose.dev.yml ps
	@echo "=== Health Check ==="
	@curl -s http://localhost:8891/health && echo "" || echo "Service not ready"

stop:
	docker-compose -f docker-compose.yml down

logs:
	docker-compose -f docker-compose.yml logs -f

logs-dev:
	docker-compose -f docker-compose.dev.yml logs -f

ps:
	docker-compose -f docker-compose.yml ps

ps-dev:
	docker-compose -f docker-compose.dev.yml ps

clean:
	docker-compose -f docker-compose.yml down -v
	docker-compose -f docker-compose.dev.yml down -v || true
	docker rmi pkm:local || true

build-server:
	docker build --cache-from ghcr.io/eviljoker/pkm:base-latest -t ghcr.io/eviljoker/pkm:snapshot .

build-base:
	docker build -t ghcr.io/eviljoker/pkm:base-latest -f Dockerfile.base .
	docker push ghcr.io/eviljoker/pkm:base-latest

test:
	docker compose -f docker-compose.dev.yml down || true
	docker compose -f docker-compose.dev.yml build --no-cache
	docker compose -f docker-compose.dev.yml up -d
	@echo "Waiting for server to start (180s)..."
	@sleep 180
	docker compose -f docker-compose.dev.yml exec -e PKM_API_BASE=http://localhost:7890 -T pkm-server bash -c "pip install -e . -q && pytest tests/ --cov=. --cov-branch --cov-config=.coveragerc && coverage json -o /tmp/cov.json"; \
	TEST_EXIT=$$?; \
	if [ $$TEST_EXIT -eq 0 ]; then \
		docker compose -f docker-compose.dev.yml exec -T pkm-server bash -c 'python3 -c "import json; c=json.load(open(\"/tmp/cov.json\")); t=c[\"totals\"]; line=int(t.get(\"percent_statements_covered\", t[\"percent_covered\"])); branch=int(t.get(\"percent_branches_covered\",0)); print(f\"line={line}% branch={branch}%\"); exit(1 if line<75 or branch<55 else 0)"'; \
		COV_EXIT=$$?; \
	else \
		COV_EXIT=$$TEST_EXIT; \
	fi; \
	docker compose -f docker-compose.dev.yml down; \
	exit $$COV_EXIT

test-deploy:
	@chmod +x install.sh
	@timeout 180 ./install.sh snapshot || echo "install.sh failed"
	@echo "=== Checking Docker images ==="
	@docker images | grep pkm || echo "No pkm image found"
	@echo "=== Checking pip packages ==="
	@pip list | grep -i pkm || echo "No pkm package found"
	@echo "=== Checking installed files ==="
	@ls -la ~/.pkm/ || echo ".pkm directory not found"
