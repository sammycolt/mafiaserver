from app.models.db_models import *
from flask import session

class SqlDriver():
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
