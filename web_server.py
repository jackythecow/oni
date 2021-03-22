from flask import Flask
from threading import Thread
import logging

app = Flask('')

# make ping log go away
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/')
def home():
    return 'six'


def run():
    app.run(host='0.0.0.0', port=8080)


def online():
    t = Thread(target=run)
    t.start()
