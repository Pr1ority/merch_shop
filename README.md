## Описание проекта

Данный проект реализует внутренний сервис магазина мерча для сотрудников Avito. Сотрудники могут приобретать товары за монеты, которыми им выделяются при вступлении в компанию. Кроме того, возможен обмен монет между сотрудниками.

## Автор

Бондаренко Алексей Олегович
- Telegram: [@alovsemprivet](https://t.me/alovsemprivet)
- GitHub: [Pr1ority](https://github.com/Pr1ority)

## Технологический стек

- Backend: Django, Django REST Framework
- Web server: Gunicorn
- Database: PostgreSQL
- Контейнеризация: Docker, Docker Compose
- Язык программирования: Python 3
- Аутентификация: JWT

## Как развернуть репозиторий на сервере

1. Клонируйте репозиторий
```bash
git clone https://github.com/Pr1ority/merch_shop.git
```
2. Перейдите в корневую директорию
```bash
cd merch_shop
```
3. Настройте виртуальное окружение
```bash
python -m venv venv
```
Для macOS/Linux
```bash
source venv/bin/activate
```
Для Windows
```bash
source venv/Scripts/activate
```
4. Заполните .env
Пример:
```example.env
SECRET_KEY=your_secret_key
```
5. Поднимите контейнеры в Докере
Находясь в папке merch_shop, выполните команду
```bash
docker-compose up --build
```
6. Подготовьте базу данных
```bash
docker-compose exec web python manage.py migrate
```
## Запуск тестов

Запустите тесты через pytest
```bash
docker-compose exec web pytest --maxfail=1 --disable-warnings -q
```

## API

1. POST /api/auth/ — аутентификация и получение JWT-токена. При первой авторизации пользователь создаётся автоматически.
2. GET /api/info/ — получение информации о балансе, инвентаре и истории транзакций.
3. GET /api/buy/<item>/ — покупка мерча (например, /api/buy/t-shirt/).
4. POST /api/sendCoin/ — перевод монет другому пользователю.

При обращении к защищённым эндпоинтам необходимо передавать заголовок:
```bash
Authorization: Bearer <access_token>
```
