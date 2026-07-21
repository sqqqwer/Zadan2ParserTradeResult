.PHONY: help install docker-up run-twopages run-allpages format lint ruff check clean

help:			## Все команды
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

install:		## Установить зависимости
	poetry install

docker-up:		## Поднять docker-compose
	docker-compose up -d

run-twopages:	## Запустить парсер на 2 страницы
	docker-compose exec backend parse_spimex_oil_bulletin_two_pages

run-allpages:	## Запустить парсер на все страницы
	docker-compose exec backend parse_spimex_oil_bulletin_all

format:			## Только форматирование
	poetry run ruff format .

lint:			## Только проверка линтером с автофиксом
	poetry run ruff check . --fix

ruff:			## Ruff на всё сразу: форматирование + линт с автофиксом
	poetry run ruff format .
	poetry run ruff check . --fix

check:			## Проверка без изменений (для CI): формат + линт в режиме "только проверить"
	poetry run ruff format . --check
	poetry run ruff check .

clean:			## Удалить кэши
	rm -rf .ruff_cache .pytest_cache __pycache__
