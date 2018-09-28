
# broker - можно также написать "pyamqp://guest@localhost//"
broker_url = 'pyamqp://user:password@localhost//'
# backend - нужен чтобы хранить и отдавать обратно результаты выполнения
#           без него у нас не будет фидбека
result_backend = 'rpc://user:password@localhost//'

result_expires=3600

# Настройки сериализации
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# Настройки времени
timezone = 'Europe/Moscow'
enable_utc = True

# Настройки роутинга
# Все таски отправляем в очередь hipri
task_routes = {
    '*': {'queue': 'hipri'},
}

# Роутинг почему-то не получается - выдает ошибку при попытке создать таск
# task_routes = {
#     'tasks.add': 'low-priority',
# }

# Из-за этого результат выполнения _сигнатуры_ нельзя получить get()'ом
# если до этого не проверить его на ready()
# task_annotations = {
#     'tasks.add': {'rate_limit': '1000/m'}
# }
