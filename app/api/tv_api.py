from app.models.db_models import *
from flask import jsonify, request, abort
from app import app
from app import utils
from random import shuffle
from app.utils.Jsonify import *

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

    list = [json.loads(str(i)) for i in users]

    print list
    return jsonify({'users': list})

@app.route('/api/tv/start_game')
def start_game():
    if not request.args or 'game_id' not in request.args:
        abort(400)

    game_id = request.args.get('game_id')

    utils.SqlDriver.setGameStatus(game_id, GameStatus.introduction)

    emptyVoting = Voting()
    db.session.add(emptyVoting)
    db.session.commit()

    jsoned_list = utils.SqlDriver.getGameSessionById(game_id).userList
    nm_of_players = len(json.loads(jsoned_list))

    nm_of_mafia = nm_of_players // 3
    roles = ["civilian" for i in range(nm_of_players - nm_of_mafia)]
    for i in range(nm_of_mafia):
        roles.append("mafia")
    shuffle(roles)

    game = GameSession.query.get(game_id)
    game.currentVoting = emptyVoting.id

    ids = utils.Json.encode_user_id_list(game.userList)
    users = utils.SqlDriver.getUsersByIds(ids)

    index = 0
    for user in users:
        user.isAlive = True
        user.role = roles[index]
        index += 1

    db.session.commit()

    return SUCCESS()



@app.route('/api/tv/get_current_voting')
def get_vote():
    join_id = request.args.get('join_id')
    game = utils.SqlDriver.getGameSessionByJoinId(join_id)
    voting = utils.SqlDriver.getVotingById(game.currentVoting)
    v = utils.Json.deparseVoting(voting.dictionary)
    return jsonify({'voting': v})


@app.route('/api/tv/wait_for_voting_end')
def wait_for_voting_end():
    join_id = request.args.get('join_id')
    game = utils.SqlDriver.getGameSessionByJoinId(join_id)
    voting = utils.SqlDriver.getVotingById(game.currentVoting)


    if voting.count >= len([i for i in utils.SqlDriver.getUsersByIds(utils.Json.encode_user_id_list(game.userList))
                            if i.isAlive]):
        old_status = game.gameStatus
        print "old: "
        print old_status
        new_status = GameStatus.night
        if old_status == GameStatus.introduction.value:
            new_status = GameStatus.night_introduction

        print "new:"
        print new_status

        utils.SqlDriver.setGameStatus(game.id, new_status)
        newVoting = Voting()
        db.session.add(newVoting)
        db.session.commit()
        game.currentVoting = newVoting.id

        db.session.commit()

        if old_status != GameStatus.introduction.value:
            killed = utils.SqlDriver.kill(join_id)
            winner = ""
            users = utils.SqlDriver.getUsers(join_id)
            alive_citizens = [i for i in users if i.isAlive and i.role == "citizen"]
            alive_mafia = [i for i in users if i.isAlive and i.role == "mafia"]

            if len(alive_mafia) == 0:
                winner = "citizens"
            else:
                if len(alive_mafia) > len(alive_citizens):
                    winner = "mafia"

            if winner != "":
                utils.SqlDriver.setGameStatus(game.id, GameStatus.finished)

            return jsonify({"result": "success", "killed": killed.id, "winner" : winner})

        return SUCCESS()
    else:
        return ERROR()

@app.route('/api/tv/wait_for_mafia_voting_end')
def wait_for_mafia_voting_end():
    join_id = request.args.get('join_id')
    game = utils.SqlDriver.getGameSessionByJoinId(join_id)
    voting = utils.SqlDriver.getVotingById(game.currentVoting)

    if voting.count >= len([i for i in utils.SqlDriver.getUsersByIds(utils.Json.encode_user_id_list(game.userList))
                                                                 if i.isAlive and i.role == "mafia"]):
        old_status = game.gameStatus
        print "old: "
        print old_status

        utils.SqlDriver.setGameStatus(game.id, GameStatus.day)
        newVoting = Voting()
        db.session.add(newVoting)
        db.session.commit()
        game.currentVoting = newVoting.id
        utils.SqlDriver.fillVoting(join_id, True)
        db.session.commit()

        if old_status != GameStatus.night_introduction.value:
            killed = utils.SqlDriver.kill(join_id)
            winner = ""
            users = utils.SqlDriver.getUsers(join_id)
            alive_citizens = [i for i in users if i.isAlive and i.role == "citizen"]
            alive_mafia =  [ i for i in users if i.isAlive and i.role == "mafia"]

            if len(alive_mafia) == 0:
                winner = "citizens"
            else:
                if len(alive_mafia) > len(alive_citizens):
                    winner = "mafia"

            if winner != "":
                utils.SqlDriver.setGameStatus(game.id, GameStatus.finished)

            return jsonify({"result": "success", "killed": killed.id, "winner" : winner})

        return SUCCESS()
    else:
        return ERROR()

@app.route('/api/tv/start_mafia_voting')
def start_mafia_voting():
    join_id = request.args.get('join_id')
    game = utils.SqlDriver.getGameSessionByJoinId(join_id)
    print game.gameStatus
    if (game.gameStatus != GameStatus.night_introduction.value):
        utils.SqlDriver.setGameStatus(game.id, GameStatus.mafia_voting)

    return SUCCESS()

# helper for tests:
@app.route('/api/tv/start_first_day')
def start_first_day():
    if not request.args or 'game_id' not in request.args:
        abort(400)

    game_id = request.args.get('game_id')

    utils.SqlDriver.setGameStatus(game_id, GameStatus.day)

    emptyVoting = Voting()
    db.session.add(emptyVoting)
    db.session.commit()

    jsoned_list = utils.SqlDriver.getGameSessionById(game_id).userList
    nm_of_players = len(json.loads(jsoned_list))

    nm_of_mafia = nm_of_players // 3
    roles = ["civilian" for i in range(nm_of_players - nm_of_mafia)]
    for i in range(nm_of_mafia):
        roles.append("mafia")
    shuffle(roles)

    game = GameSession.query.get(game_id)
    game.currentVoting = emptyVoting.id
    
    utils.SqlDriver.fillVoting(game.joinCode, True)

    ids = utils.Json.encode_user_id_list(game.userList)
    users = utils.SqlDriver.getUsersByIds(ids)

    index = 0
    for user in users:
        user.isAlive = True
        user.role = roles[index]
        index += 1

    db.session.commit()

    return SUCCESS()




