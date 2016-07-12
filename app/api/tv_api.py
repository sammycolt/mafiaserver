from app.models.db_models import *
from flask import jsonify, request
from app import app
from app import utils

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

    game_id = request.args.get('game_id')
    game = GameSession.query.get(game_id)

    ids = utils.Json.encode_user_id_list(game.userList)
    users = utils.SqlDriver.getUsersByIds(ids)

    print users

    list = [str(i) for i in users]
    return jsonify({'users': str(list)})

@app.route('/api/tv/start_game')
def start_game():
    utils.SqlDriver.setGameStatus(GameStatus.day)
    return "success"


