from app import app
from app.models.db_models import *
from flask import request, abort, jsonify
from app.utils.SqlDriver import *
import json

@app.route('/api/phone')
def api_phone():
    return "Welcome to API for phones"

@app.route('/api/phone/join_user_to_game', methods=["POST"])
def join_user_to_game():
    if not request.args or 'game_id' not in request.args \
            or 'name' not in request.args or 'image_url' not in request.args:
        abort(400)

    if 'user_id' not in session.keys():
        print "1"
        newuser = User(request.args.get('name'), request.args.get('image_url'))
        print newuser.isAlive
        db.session.add(newuser)
        print "2"
        db.session.commit()

        session['user_id'] = newuser.id

    newuserid = session['user_id']

    join_id = request.args.get('game_id')
    gameSession = SqlDriver.getGameSessionByJoinId(join_id)

    if gameSession == []:
        return jsonify({'result': 'error'})
    else:
        users = json.loads(gameSession.userList)

        users.append(newuserid)
        gameSession.userList = str(users)
        db.session.commit()
        return jsonify({'result': 'success'})