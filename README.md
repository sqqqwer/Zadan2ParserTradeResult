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
make docker-up
```
- Распарсить 2 страницы (50-51)
```shell
make run-twopages
```
- Распарсить всё
```shell
make run-allpages
```
