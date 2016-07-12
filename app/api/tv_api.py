from app.models.db_models import *
from flask import jsonify, request, abort
from app import app
from app import utils
from random import shuffle

@app.route('/api/tv')
def api_tv():
    return "Welcome to API for Apple TV"

@app.route('/api/tv/create_game')
def create_game():
    game = GameSession()
    joinCode = game.joinCode

    db.session.add(game)
    db.session.commit()

    # print GameSession.query.all()

    # session['game_id'] = game.id

    return jsonify({'joinCode': joinCode, 'game_id': game.id})

@app.route('/api/tv/get_current_user_list')
def get_current_user_list():
    # game_id = session['game_id']

    if not request.args or 'game_id' not in request.args:
        abort(400)

    game_id = request.args.get('game_id')
    game = GameSession.query.get(game_id)

    ids = utils.Json.encode_user_id_list(game.userList)

    users = utils.SqlDriver.getUsersByIds(ids)

    # print users

    list = [str(i) for i in users]

    print list
    return jsonify({'users': list})

@app.route('/api/tv/start_game')
def start_game():
    if not request.args or 'game_id' not in request.args:
        abort(400)

    game_id = request.args.get('game_id')

    utils.SqlDriver.setGameStatus(game_id, GameStatus.day)

    jsoned_list = utils.SqlDriver.getGameSessionById(game_id).userList
    nm_of_players = len(json.loads(jsoned_list))

    nm_of_mafia = nm_of_players // 3
    roles = ["civilian" for i in range(nm_of_players - nm_of_mafia)]
    for i in range(nm_of_mafia):
        roles.append("mafia")
    shuffle(roles)

    game = GameSession.query.get(game_id)
    ids = utils.Json.encode_user_id_list(game.userList)
    users = utils.SqlDriver.getUsersByIds(ids)

    index = 0
    for user in users:
        user.role = roles[index]
        index += 1

    db.session.commit()

    return jsonify({'result': "success"})



@app.route('/api/tv/get_vote/<vote_id>')
def get_vote(vote_id):
    pass
