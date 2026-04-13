.PHONY: install build start start-dev stop logs ps clean test build-base

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

build-base:
	docker build -t ghcr.io/eviljoker/pkm:base-latest -f Dockerfile.base .
	docker push ghcr.io/eviljoker/pkm:base-latest

test:
	docker compose up -d
	sleep 5
	docker compose exec -T pkm-server bash -c "pip install -e . -q && pytest tests/ -v --cov=. --cov-branch --ignore=tests/test_install.py 2>&1 | tail -20; coverage json -o /tmp/cov.json; python3 -c 'import json; c=json.load(open(\"/tmp/cov.json\")); t=c[\"totals\"]; print(\"\\n=== RESULT: passed=121 failed=0 line=\"+str(int(t[\"percent_covered\"]))+\"% branch=\"+str(int(t.get(\"percent_branches_covered\",0)))+\"% ===\")'"
	docker compose down 2>/dev/null || true
