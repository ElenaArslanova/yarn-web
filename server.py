import bottle
from beaker.middleware import SessionMiddleware
from bottle import route, request, error, template, static_file
from cork import Cork, AuthException

from db.alchemy import Alchemy

alchemy = Alchemy(path='db/data.db')
app = bottle.app()


@route('/')
def login():
    return template('static/html/login.html')


@route('/<filename:path>')
def send_file(filename):
    return static_file(filename, root='static/')


if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(app=app, host='localhost', port=5050)
