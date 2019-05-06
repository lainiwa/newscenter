"""The only sript yet.

It would be devided in the future.

Useful commands:
    celery -A app:celery worker -Q hipri --loglevel=info
    docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3
"""

from app import create_app, socketio

app = create_app(debug=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9998)


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=9998)
