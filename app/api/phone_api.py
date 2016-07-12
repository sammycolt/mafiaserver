from app import app
from app.models.db_models import *
from flask import request, abort, jsonify
from app.utils.SqlDriver import *
import json

@app.route('/api/phone')
def api_phone():
    return "Welcome to API for phones"


@app.route('/api/phone/register_user', methods=["POST"])
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

    if gameSession == []:
        return jsonify({'result': 'error'})
    else:
        users = json.loads(gameSession.userList)

        users.append(newuserid)
        gameSession.userList = str(users)
        db.session.commit()
        return jsonify({'result': 'success'})
