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
	@docker compose exec learn2slither flake8 srcs

.PHONY: exec
exec:
	docker compose exec learn2slither sh

#.PHONY: test
#test:
#	docker compose exec learn2slither pytest -v -c config/pytest.ini

.PHONY: clean
clean:
	docker compose down --rmi all

.PHONY: fclean
fclean: clean
	docker system prune -a
