from app import db, app
from app.models.db_models import GameSession
from flask import jsonify, session

@app.route('/api/tv')
def api_rv():
    return "Welcome to API for Apple TV"

@app.route('/api/tv/create_game')
def create_game():
    print("kek")
    game = GameSession()
    joinCode = game.joinCode

    db.session.add(game)
    db.session.commit()

    session['id'] = game.id
    print GameSession.query.all()
    return jsonify({'joinCode': joinCode})

