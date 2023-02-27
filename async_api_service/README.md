## Структура проекта async_api_service:

    src - код проекта 
    envs - переменные окружения необходимые для запуска проекта

## Работа с проектом:

1. В terminale(cmd) запустим docker-compose с помощью команды `docker-compose up` или `docker-compose up -d` для запуска в фоновом режиме, убедитесь что вы находитесь в папке async_api_service.
2. Для завершения работы docker-compose выполните `docker-compose down` команду

## Запуск тестов:
1. Перейти в папку tests/functional/
2. В terminale(cmd) запустить docker-compose с помощью команды `docker-compose up --build`