GREEN = \033[0;32m
NC = \033[0m

.PHONY: all
all: build

.PHONY: build
build:
	docker compose up --build -d

.PHONY: notebook
notebook:
	docker compose exec learn2slither jupyter notebook \
		--ip=0.0.0.0 \
		--port=8888 \
		--no-browser \
		--allow-root \
		--ServerApp.token='' \
		--ServerApp.password=''

.PHONY: down
down:
	docker compose down

.PHONY: info
info:
	@docker compose exec learn2slither python --version

.PHONY: lint
lint:
	@if docker compose exec learn2slither flake8 --config=config/.flake8 srcs; then \
		echo "${GREEN}LINT OK${NC}"; \
	fi

.PHONY: exec
exec:
	docker compose exec learn2slither sh

.PHONY: run
run:
	docker compose exec learn2slither python3 srcs/snake.py

.PHONY: test
test:
	docker compose exec learn2slither pytest -v -c config/pytest.ini

.PHONY: clean
clean:
	docker compose down --rmi all

.PHONY: fclean
fclean: clean
	docker system prune -a
