# Запуск проекта

- Клонируйте репозиторий
```shell
git clone https://github.com/sqqqwer/Zadan2ParserTradeResult.git
```
- Перейдите в проект
```shell
cd Zadan2ParserTradeResult/
```
- Подготовьте .env файл.
- Запустите docker

- Поднимите контейнеры
```shell
docker-compose up -d
```
- Распарсить 2 страницы (50-51)
```shell
docker-compose exec backend parse_spimex_oil_bulletin_two_pages
```
- Распарсить всё
```shell
docker-compose exec backend parse_spimex_oil_bulletin_all
```
