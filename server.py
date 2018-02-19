import bottle
from beaker.middleware import SessionMiddleware
from bottle import route, request, error, template, static_file
from cork import Cork, AuthException

from db.alchemy import Alchemy
from models.launcher import create_majority_row_model
from models.utils import results_as_dict

alchemy = Alchemy(path='db/data.db')
app = bottle.app()
active_model = create_majority_row_model()


@route('/')
def login():
    return template('static/html/login.html')


@route('/contribute')
def contribute():
    # TODO добавить логику выдачи синсетов
    yarn_ids, synset_definitions = alchemy.get_synsets_definitions((10, 15))
    answers = active_model.clean(synset_definitions)
    result = results_as_dict(yarn_ids, answers)
    return template('static/html/synsets.html', synsets=result)


@route('/<filename:path>')
def send_file(filename):
    return static_file(filename, root='static/')


if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(app=app, host='localhost', port=5050)
