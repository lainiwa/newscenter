#!/usr/bin/env bash

# Запускаем celery и гуй (http://localhost:5555/) к нему.
# А затем ждем завершения обоих процессов.
# Так их можно одним Ctrl+C убить.

celery -A run:celery worker -Q hipri --loglevel=info &
P1=$!

celery -A run:celery flower &
P2=$!

wait $P1 $P2
