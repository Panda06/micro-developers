# Smart ЖКХ - Микро-разработчики

## Описание решения


## Стек технологий

- Backend: FastAPI
- Frontend:
- Database: PostgreSQL
- Containerization: Docker & Docker Compose

## Запуск приложения

### Требования

- Docker и Docker Compose

### Установка

Создайте файл `.env` в корневой директории:
```bash
cp .env.example .env
```

Заполните все переменные окружения


### Запуск

Запустите все сервисы:
```bash
docker-compose up -d
```

Проверьте статус сервисов:
```bash
docker-compose ps
```

## Остановка сервисов

```bash
docker-compose down
```

Для полной очистки (включая volumes):
```bash
docker-compose down -v
```

Проверьте, установлен ли уже:


```bash 
node -v
npm -v 
```
Если нету, то установите.
```bash

cd smart-zhkh

npm run dev
```