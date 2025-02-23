.PHONY: install run test clean

PYTHON := .venv/bin/python
PIP := .venv/bin/pip
DOCKER_EXEC := podman  # podman or docker

up:
	$(DOCKER_EXEC) compose up -d

down:
	$(DOCKER_EXEC) compose down

install:
	$(PIP) install -e .

mysql:
	$(DOCKER_EXEC) run --restart=always --name mysql-db -e MYSQL_ROOT_PASSWORD=root -p 127.0.0.1:3306:3306 -v mysql-data:/var/lib/mysql -d docker.io/library/mysql

redis:
	$(DOCKER_EXEC) run --restart=always --name redis-db -p 127.0.0.1:6379:6379 -v redis-data:/data -d docker.io/library/redis redis-server --appendonly yes

bot:
	pdm run python src/tg_bot/main.py

trading:
	pdm run python src/trading/main.py

wallet-tracker:
	pdm run python src/wallet_tracker/main.py

gmgn-tracker:
	pdm run python src/gmgnbot/main.py
	
pump-monitor:
	PYTHONPATH=$(PWD)/src $(PYTHON) src/pump_monitor/main.py

cache:
	pdm run python src/cache
