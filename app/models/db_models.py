from app import db
from random import randint
from app.enums.game_status import GameStatus
from flask import jsonify

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
        return jsonify({'name': self.username, 'is_alive': self.isAlive, 'image_url': self.imageUrl}).get_data(as_text=True)

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    joinCode = db.Column(db.Integer)
    userList = db.Column(db.String(1488), default="[7]")
    gameStatus = db.Column(db.Integer)

    def genJoinCode(self):
        return randint(1000, 9999)

    def __init__(self):
        self.gameStatus = GameStatus.initialization
        self.joinCode = self.genJoinCode()

