from app.models.db_models import *
from flask import session
from app.utils.Json import *

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
        game.gameStatus = gameStatus.value
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

        votingObject = {}
        for user_id in user_ids:
            votingObject[user_id] = []

        voting.dictionary = str(votingObject)
        db.session.commit()
