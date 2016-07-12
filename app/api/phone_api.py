from app import app
from app.models.db_models import *
from flask import request, abort

@app.route('/api/phone')
def api_phone():
    return "Welcome to API for phones"

@app.route('/api/phone/join_user_to_game', methods=["POST"])
def join_user_to_game():
    if not request.json or 'game_id' not in request.json or 'name' not in request.json:
        abort(400)

    join_id = request.json['game_id']
    gameSession = GameSession.query.filter_by(joinCode==join_id)