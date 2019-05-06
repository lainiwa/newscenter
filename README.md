# Система загрузки новостей

Михал Михалыч меня просил сделать систему загрузки новостей для сайта, где загружаемые медиа файлы конвертировались бы в единый формат и размер. И я с ней увяз.

Проблема с "наивной реализацией" следующая - если файлы довольно большие (видео например), то конвертирование будет происходить не моментально, и у пользователя будет браузер "долго загружать" страницу после upload'а файлов.

Решения два:

* Конвертировать на стороне стороне клиента джаваскриптом
    * Снимает нагрузку с сервера
    * Мало либ для подобного (хотя ресайзить картинки точно можно)
    * Пользователи IE и старых браузеров идут мимо
* Создать очередь тасков (у меня - Celery + RabbitMQ).

Я выбрал второй подход. Но **возможно не стоит вообще решать эту "проблему"**.

Если решишь делать "наивную" реализацию - то тебе тут может быть полезно только посмотреть, как загружать несколько файлов сразу, а не заставлять пользователя выбирать по одному.

Если решишь делать "правильно", то вот как можно запустить то что я сделал (а сделал я только асинхронный ресайз картинок):

* git clone этот репозиторий
* создаешь venv, устанавливаешь зависимости
* Запускаешь брокер сообщений: `docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3`
* Запускаешь очередь: `celery -A app:celery worker -Q hipri --loglevel=info`
* Устанавливаешь зависимости для фронтенда и собираешь его: `npm install` и `npm run build` соответственно.
* Запускаешь сервер: `python run.py`
* Идешь на localhost:9998 и загружаешь несколько пикч. Они оказываются ресайзнутыми в папке `backend/uploads`. (создай ее)

Не уверен впрочем насколько это тебе будет полезно.
