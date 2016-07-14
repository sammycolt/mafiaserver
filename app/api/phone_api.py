from app import app
from app.models.db_models import *
from flask import request, abort, jsonify
from app.utils.SqlDriver import *
from app.utils import SqlDriver
from app.utils.Json import *
import json
from app.utils.Jsonify import *

@app.route('/api/phone')
def api_phone():
    return "Welcome to API for phones"


@app.route('/api/phone/register_user')
def register_user():
    if not request.args  \
            or 'name' not in request.args or 'image_url' not in request.args:
        abort(400)
    newuser = User(request.args.get('name'), request.args.get('image_url'))
    db.session.add(newuser)
    db.session.commit()

    newuserid = newuser.id
    return jsonify({"user_id": newuserid})


@app.route('/api/phone/join_user_to_game')
def join_user_to_game():
    if not request.args or 'join_id' not in request.args\
            or 'user_id' not in request.args:
        abort(400)

    newuserid = int(request.args.get('user_id'))

    join_id = request.args.get('join_id')
    gameSession = SqlDriver.getGameSessionByJoinId(join_id)

    if gameSession == None:
        return jsonify({'result': 'error'})
    else:
        users = json.loads(gameSession.userList)

        users.append(newuserid)
        gameSession.userList = str(users)
        db.session.commit()
        return SUCCESS()

@app.route('/api/phone/check_game_status')
def check_game_status():
    if 'join_id' not in request.args:
        abort(400)

    join_id = request.args.get('join_id')
    game = SqlDriver.getGameSessionByJoinId(join_id)

    if game != None:
        if game.gameStatus != GameStatus.initialization:
            return SUCCESS()

    return ERROR()

@app.route('/api/phone/get_role')
def get_role():
    join_id = request.args.get('join_id')
    user_id = int(request.args.get('user_id'))

    game = SqlDriver.getGameSessionByJoinId(join_id)
    ids = Json.encode_user_id_list(game.userList)

    users = SqlDriver.getUsersByIds(ids)

    print users

    for user in users:
        if user.id == user_id:
            return jsonify({'result' : user.role})

    return ERROR()

@app.route('/api/phone/get_vote_list')
def get_vote_list():
    join_id = request.args.get('join_id')
    print join_id
    user_id = int(request.args.get('user_id'))
    is_for_mafia_list = False
    if request.args.get('is_for_mafia_list') == "true":
        is_for_mafia_list = True

    print is_for_mafia_list

    game = SqlDriver.getGameSessionByJoinId(join_id)
    ids = Json.encode_user_id_list(game.userList)
    users = SqlDriver.getUsersByIds(ids)

    alive_users = []
    for user in users:
        if user.isAlive and user.id != user_id:
            if is_for_mafia_list:
                if user.role != 'mafia':
                    alive_users.append(user)
            else:
                print user.id
                alive_users.append(user)

    list = [json.loads(str(i)) for i in alive_users]
    return jsonify({'result':list})

@app.route('/api/phone/finish_introduction')
def finish_introduction():
    join_id = request.args.get('join_id')

    game = SqlDriver.getGameSessionByJoinId(join_id)
    voting = SqlDriver.getVotingById(game.currentVoting)

    voting.count += 1
    db.session.commit()

    return SUCCESS()

@app.route('/api/phone/waiting_for_night')
def waiting_for_night():
    join_id = request.args.get('join_id')
    game = SqlDriver.getGameSessionByJoinId(join_id)
    if game.gameStatus == GameStatus.night or \
                    game.gameStatus == GameStatus.night_introduction:
        return SUCCESS()
    else:
        return ERROR()


@app.route('/api/phone/waiting_for_day')
def waiting_for_day():
    join_id = request.args.get('join_id')
    game = SqlDriver.getGameSessionByJoinId(join_id)
    if game.gameStatus == GameStatus.day:
        return SUCCESS()
    else:
        return ERROR()

@app.route('/api/phone/waiting_for_mafia_start_voting')
def waiting_for_mafia_start_voting():
    join_id = request.args.get('join_id')
    game = SqlDriver.getGameSessionByJoinId(join_id)
    voting = SqlDriver.getVotingById(game.currentVoting)

    if voting.dictionary != "[]":
        return SUCCESS()
    else:
        return ERROR()

@app.route('/api/phone/vote_for_user_by_id')
def vote_for_user_by_id():
    join_id = request.args.get('join_id')
    user_id = int(request.args.get('user_id'))
    targer_user = int(request.args.get('target_user'))

    SqlDriver.addUserToVoting(join_id, user_id, targer_user)

    return SUCCESS()

@app.route('/api/phone/is_finished')
def is_finished():
    join_id = request.args.get('join_id')
