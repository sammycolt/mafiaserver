from app.models.db_models import *
from flask import session

class SqlDriver():
    @staticmethod
    def getUsersByIds(ids):
        return db.session.query(User).filter(User.id.in_(ids)).all()

    @staticmethod
    def setGameStatus(gameStatus):
        game = SqlDriver.getGame()
        game.gameStatus = gameStatus.value
        db.session.commit()

    @staticmethod
    def getGame():
        return GameSession.query.get(session['game_id'])

