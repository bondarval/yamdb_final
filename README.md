# API для проекта YaMDB в контейнере Docker
[![API for YaMDB project workflow](https://github.com/bondarval/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=main)](https://github.com/bondarval/yamdb_final/actions/workflows/yamdb_workflow.yml)
## Описание
### Возможности проекта
Представляет собой расширение возможностей проекта YaMDB для совершения удаленных операций.   
Благодаря этому проекту зарегистрированные и аутентифицированные пользователи получают 
возможность оставлять рецензии на произведения различных категорий, 
комментировать рецензии других пользователей,просматривать сформированные на основе оценок рейтинги произведений. 
Сайт не предоставляет прямой доступ или ссылки для ознакомления непосредственно с произведениями.
### Расширение функциональности
Функционал проекта адаптирован для использования PostgreSQL и развертывания в контейнерах Docker. Используются инструменты CI и CD.
### Ссылка на сайт
(не актуальная!)
http://bondaryatube.ddns.net
## Технологии
 - Python 3.7
 - Django 2.2.16
 - REST Framework 3.12.4
 - PyJWT 2.1.0
 - Django filter 21.1
 - Gunicorn 20.0.4
 - PostgreSQL 12.2
 - Docker 20.10.2
## Установка
### Шаблон описания файла .env
 - DB_ENGINE=<ENGINE>
 - DB_NAME=<NAME>
 - POSTGRES_USER=<USER_NAME>
 - POSTGRES_PASSWORD=<PASSWORD>
 - DB_HOST=<HOST>
 - DB_PORT=<PORT>
### Команды для запуска приложения в контейнерах
- собрать и запустить контейнер:
```bash
docker-compose up -d --build
```
- Выполнить миграции внутри контейнеров:
```bash
docker-compose exec web python manage.py migrate
```
- Создать суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```
- Собрать статику проекта:
```bash
docker-compose exec web python manage.py collectstatic --no-input
``` 
### Команды для заполнения базы данными
- Заполнить базу данными
- Создать резервную копию данных:
```bash
docker-compose exec web python manage.py dumpdata > fixtures.json
```
## Примеры API-запросов
Подробные примеры запросов и коды ответов приведены в прилагаемой документации в формате ReDoc 
## Авторы
- Абрамов Кирилл
- Бондарь Валерий
- Кулеш Иван
