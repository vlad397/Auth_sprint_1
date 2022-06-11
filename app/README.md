# Реализация API для кинотеатра

Ваша задача – создать API, возвращающий список фильмов в формате, описанном в [openapi-файле 💾](https://code.s3.yandex.net/middle-python/learning-materials/06_django2_phantom_menace_docs_openapi.yml), и позволяющий получить информацию об одном фильме.

Проверить результат работы API можно при помощи Postman. Запустите сервер на 127.0.0.1:8000 и воспользуйтесь тестами [из файла 💾](https://code.s3.yandex.net/middle-python/learning-materials/06_django2_phantom_menace_docs_movies_API.postman_collection.json). В тестах предполагается, что в вашем API установлена пагинация и выводится по 50 элементов на странице.

**Для проверки**
- cd 01_doker_compose (файл .env добавлен для облегчения проверки)
- docker-compose up
- запуск postman-тестов
