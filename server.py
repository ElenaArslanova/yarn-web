import json

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
    # TODO пересылка на страницу синсетов, если авторизован
    return template('static/html/login.html')


@route('/contribute')
def contribute():
    # TODO проверка авторизации
    # TODO добавить логику выдачи синсетов
    yarn_ids, synset_definitions = alchemy.get_synsets_definitions((45, 55))
    answers = active_model.clean(synset_definitions)
    result = results_as_dict(yarn_ids, answers)
    return template('static/html/synsets.html', synsets=result)


@route('/receive_edition', method='POST')
def receive_edition():
    # TODO добавить проверку авторизации
    response = request.json
    syn_id, correct, wrong = int(response.get('id').replace('syn-', '')), response.get('correct'), response.get('wrong')
    # TODO хранение изменений в базе
    # TODO отправлять ответ об ошибке
    print(syn_id, correct, wrong)
    return json.dumps({'status': 'ok'})


@route('/word_definition', method='POST')
def word_definition():
    # TODO проверка авторизации
    word = request.json.get('word')
    definitions = alchemy.get_word_definitions(word)
    return json.dumps(definitions)


@route('/<filename:path>')
def send_file(filename):
    return static_file(filename, root='static/')


if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(app=app, host='localhost', port=5050)
