from random import randint, shuffle

from enum import Enum
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import json


class GameStatus(Enum):
    day = 1
    night = 2
    introduction = 4
    initialization = 5
    night_introduction = 6
    finished = 7


class Json():
    @staticmethod
    def encode_user_id_list(json_users):
        user_id_list = json.loads(json_users)
        return user_id_list

    @staticmethod
    def deparseVoting(a):
        #printa
        b = list(a[1:-2].replace(' ', '').split('},'))
        ans = []
        for i in b:
            user = i[1:].split(':')[0]
            users = list(i[1:-1].split(':')[1][1:].split(','))
            dict = {}
            if users[0] == "":
                users = []
            else:
                users = [int(i) for i in users]
            dict[int(user)] = users
            ans.append(dict)
        return ans

def SUCCESS():
    return jsonify({"result" : "success"})


def ERROR():
    return jsonify({"result" : "error"})


class SqlDriver():
    @staticmethod
    def getUsers(join_id):
        game = SqlDriver.getGameSessionByJoinId(join_id)
        return SqlDriver.getUsersByIds(Json.encode_user_id_list(game.userList))

    @staticmethod
    def getUsersByIds(ids):
        return db.session.query(User).filter(User.id.in_(ids)).all()

    @staticmethod
    def setGameStatus(game_id, gameStatus):
        game = SqlDriver.getGameSessionById(game_id)
        game.gameStatus = gameStatus
        db.session.commit()

    @staticmethod
    def getGameSessionById(game_id):
        return GameSession.query.get(game_id)

    @staticmethod
    def getGameSessionByJoinId(id):
        list = db.session.query(GameSession).filter(GameSession.joinCode==id).all()
        if len(list) > 0:
            return list[0]
        else:
            return None

    @staticmethod
    def getVotingById(id):
        return Voting.query.get(id)

    @staticmethod
    def fillVoting(join_id, isDay):
        game = SqlDriver.getGameSessionByJoinId(join_id)
        voting = SqlDriver.getVotingById(game.currentVoting)

        user_ids = []
        for user in SqlDriver.getUsers(join_id):
            if user.isAlive:
                if isDay:
                    user_ids.append(user.id)
                else:
                    if user.role != "mafia":
                        user_ids.append(user.id)

        votingObject = []
        for user_id in user_ids:
            dict = {}
            dict[user_id] = []
            votingObject.append(dict)

        voting.dictionary = str(votingObject)
        db.session.commit()

    @staticmethod
    def addUserToVoting(join_id, user_id, target_id):
        game = SqlDriver.getGameSessionByJoinId(join_id)
        voting = SqlDriver.getVotingById(game.currentVoting)
        voting_arr = Json.deparseVoting(voting.dictionary)

        #print"old voting"
        #printvoting_arr
        for user in voting_arr:
            if target_id in user.keys():
                user[target_id].append(user_id)


        #print"new voting"
        #printvoting_arr

        voting.dictionary = str(voting_arr)
        voting.count += 1
        db.session.commit()

    @staticmethod
    def kill(join_id):
        game = SqlDriver.getGameSessionByJoinId(join_id)
        voting = SqlDriver.getVotingById(game.currentVoting)
        #printvoting.dictionary
        voting_ar = Json.deparseVoting(voting.dictionary)

        #print"kill:"
        #printvoting_ar

        maxLen = 0

        for voteOb in voting_ar:
            l = len(voteOb[voteOb.keys()[0]])
            if l > maxLen:
                maxLen = l

        result = []
        for voteOb in voting_ar:
            l = len(voteOb[voteOb.keys()[0]])
            if l == maxLen:
                result.append(voteOb)

        #print"result:"
        #printresult
        resultVote = result[randint(0, len(result) - 1)]

        user_id = resultVote.keys()[0]
        user = SqlDriver.getUsersByIds([user_id])[0]

        user.isAlive = False

        db.session.commit()

        return user

    @staticmethod
    def isFinished(join_id):
        game = SqlDriver.getGameSessionByJoinId(join_id)
        return game.gameStatus == GameStatus.finished


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test148.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

app.secret_key = "azazaazazaza228"
db.create_all()




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    isAlive = db.Column(db.Boolean, default=True)
    imageUrl = db.Column(db.String(120), default="")
    role = db.Column(db.String(120), default="civilian")

    def __init__(self, username, imageUrl, isAlive=True):
        self.username = username
        self.imageUrl = imageUrl
        self.isAlive = isAlive

    def __repr__(self):
        data = {}
        data['name'] = self.username
        data['is_alive'] = self.isAlive
        data['image_url'] = self.imageUrl
        data['role'] = self.role
        data['id'] = self.id
        return json.dumps(data)

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    joinCode = db.Column(db.Integer)
    userList = db.Column(db.String(1488), default="[]")
    gameStatus = db.Column(db.Integer)
    currentVoting = db.Column(db.Integer, default=0)

    def genJoinCode(self):
        return randint(1000, 9999)

    def __init__(self):
        self.gameStatus = GameStatus.initialization
        self.joinCode = self.genJoinCode()

class Voting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dictionary = db.Column(db.String, default="[]")
    count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return self.dictionary

@app.route('/')
def api_root():
    return "Welcome"

@app.route('/api')
def api_api():
    return "Welcome to API"

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

    #printusers

    for user in users:
        if user.id == user_id:
            return jsonify({'result':user.role})

    return ERROR()

@app.route('/api/phone/get_vote_list')
def get_vote_list():
    join_id = request.args.get('join_id')
    #printjoin_id
    user_id = int(request.args.get('user_id'))
    is_for_mafia_list = False
    if request.args.get('is_for_mafia_list') == "true":
        is_for_mafia_list = True

    #printis_for_mafia_list

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
                #printuser.id
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

@app.route('/api/tv')
def api_tv():
    return "Welcome to API for Apple TV"

@app.route('/api/tv/create_game')
def create_game():
    game = GameSession()
    joinCode = game.joinCode

    db.session.add(game)
    db.session.commit()

    # #printGameSession.query.all()

    # session['game_id'] = game.id

    return jsonify({'joinCode': joinCode, 'game_id': game.id})

@app.route('/api/tv/get_current_user_list')
def get_current_user_list():
    # game_id = session['game_id']

    if not request.args or 'game_id' not in request.args:
        abort(400)

    game_id = request.args.get('game_id')
    game = GameSession.query.get(game_id)

    ids = Json.encode_user_id_list(game.userList)

    users = SqlDriver.getUsersByIds(ids)

    # #printusers

    list = [json.loads(str(i)) for i in users]

    #printlist
    return jsonify({'users': list})

@app.route('/api/tv/start_game')
def start_game():
    if not request.args or 'game_id' not in request.args:
        abort(400)

    game_id = request.args.get('game_id')

    SqlDriver.setGameStatus(game_id, GameStatus.introduction)

    emptyVoting = Voting()
    db.session.add(emptyVoting)
    db.session.commit()

    jsoned_list = SqlDriver.getGameSessionById(game_id).userList
    nm_of_players = len(json.loads(jsoned_list))

    nm_of_mafia = nm_of_players // 3
    roles = ["civilian" for i in range(nm_of_players - nm_of_mafia)]
    for i in range(nm_of_mafia):
        roles.append("mafia")
    shuffle(roles)

    game = GameSession.query.get(game_id)
    game.currentVoting = emptyVoting.id

    ids = Json.encode_user_id_list(game.userList)
    users = SqlDriver.getUsersByIds(ids)

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
    game = SqlDriver.getGameSessionByJoinId(join_id)
    voting = SqlDriver.getVotingById(game.currentVoting)
    v = Json.deparseVoting(voting.dictionary)
    return jsonify({'voting': v})


@app.route('/api/tv/wait_for_voting_end')
def wait_for_voting_end():
    join_id = request.args.get('join_id')
    game = SqlDriver.getGameSessionByJoinId(join_id)
    voting = SqlDriver.getVotingById(game.currentVoting)


    if voting.count >= len([i for i in SqlDriver.getUsersByIds(Json.encode_user_id_list(game.userList))
                            if i.isAlive]):
        old_status = game.gameStatus
        new_status = GameStatus.night

        #print"-------------------------------------"
        #printold_status
        #printGameStatus.introduction
        #print"-------------------------------------"

        if old_status == GameStatus.introduction:
            new_status = GameStatus.night_introduction

            SqlDriver.setGameStatus(game.id, new_status)
            newVoting = Voting()
            db.session.add(newVoting)
            db.session.commit()
            game.currentVoting = newVoting.id

            db.session.commit()

            return SUCCESS()

        else:
            killed = SqlDriver.kill(join_id)
            winner = ""
            users = SqlDriver.getUsers(join_id)
            alive_citizens = [i for i in users if i.isAlive and i.role == "civilian"]
            alive_mafia = [i for i in users if i.isAlive and i.role == "mafia"]

            if len(alive_mafia) == 0:
                winner = "civilians"
            else:
                if len(alive_mafia) >= len(alive_citizens):
                    winner = "mafia"

            if winner != "":
                SqlDriver.setGameStatus(game.id, GameStatus.finished)

            else:
                SqlDriver.setGameStatus(game.id, new_status)
                newVoting = Voting()
                db.session.add(newVoting)
                db.session.commit()
                game.currentVoting = newVoting.id

                db.session.commit()

            return jsonify({"result": "success", "killed": killed.id, "winner": winner})

    else:
        return ERROR()

@app.route('/api/tv/wait_for_mafia_voting_end')
def wait_for_mafia_voting_end():
    join_id = request.args.get('join_id')
    game = SqlDriver.getGameSessionByJoinId(join_id)
    voting = SqlDriver.getVotingById(game.currentVoting)

    if voting.count >= len([i for i in SqlDriver.getUsersByIds(Json.encode_user_id_list(game.userList))
                                                                 if i.isAlive and i.role == "mafia"]):
        old_status = game.gameStatus
        #print"old: "
        #printold_status

        if old_status != GameStatus.night_introduction:
            killed = SqlDriver.kill(join_id)
            winner = ""
            users = SqlDriver.getUsers(join_id)
            alive_citizens = [i for i in users if i.isAlive and i.role == "civilian"]
            alive_mafia =  [ i for i in users if i.isAlive and i.role == "mafia"]

            if len(alive_mafia) == 0:
                winner = "civilians"
            else:
                if len(alive_mafia) >= len(alive_citizens):
                    winner = "mafia"

            if winner != "":
                SqlDriver.setGameStatus(game.id, GameStatus.finished)
            else:
                SqlDriver.setGameStatus(game.id, GameStatus.day)
                newVoting = Voting()
                db.session.add(newVoting)
                db.session.commit()
                game.currentVoting = newVoting.id
                SqlDriver.fillVoting(join_id, True)
                db.session.commit()

            return jsonify({"result": "success", "killed": killed.id, "winner" : winner})

        SqlDriver.setGameStatus(game.id, GameStatus.day)
        newVoting = Voting()
        db.session.add(newVoting)
        db.session.commit()
        game.currentVoting = newVoting.id
        SqlDriver.fillVoting(join_id, True)
        db.session.commit()

        return SUCCESS()
    else:
        return ERROR()

@app.route('/api/tv/start_mafia_voting')
def start_mafia_voting():
    join_id = request.args.get('join_id')
    game = SqlDriver.getGameSessionByJoinId(join_id)
    #printgame.gameStatus
    if (game.gameStatus != GameStatus.night or game.gameStatus != GameStatus.night_introduction):
        SqlDriver.fillVoting(join_id, False)

    return SUCCESS()

# helper for tests:
@app.route('/api/tv/start_first_day')
def start_first_day():
    if not request.args or 'game_id' not in request.args:
        abort(400)

    game_id = request.args.get('game_id')

    SqlDriver.setGameStatus(game_id, GameStatus.day)

    emptyVoting = Voting()
    db.session.add(emptyVoting)
    db.session.commit()

    jsoned_list = SqlDriver.getGameSessionById(game_id).userList
    nm_of_players = len(json.loads(jsoned_list))

    nm_of_mafia = nm_of_players // 3
    roles = ["civilian" for i in range(nm_of_players - nm_of_mafia)]
    for i in range(nm_of_mafia):
        roles.append("mafia")
    shuffle(roles)

    game = GameSession.query.get(game_id)
    game.currentVoting = emptyVoting.id

    SqlDriver.fillVoting(game.joinCode, True)

    ids = Json.encode_user_id_list(game.userList)
    users = SqlDriver.getUsersByIds(ids)

    index = 0
    for user in users:
        user.isAlive = True
        user.role = roles[index]
        index += 1

    db.session.commit()

    return SUCCESS()

def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()

#clear_data(session=db.session)

# app.run()