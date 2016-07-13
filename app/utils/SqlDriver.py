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

        print voting_arr
        for user in voting_arr:
            if target_id in user.keys():
                user[target_id].append(user_id)

        print voting_arr
        print str(voting_arr)
        voting.dictionary = str(voting_arr)
        voting.count += 1
        db.session.commit()

    @staticmethod
    def kill(join_id):
        game = SqlDriver.getGameSessionByJoinId(join_id)
        voting = SqlDriver.getVotingById(game.currentVoting)
        voting_ar = Json.deparseVoting(voting.dictionary)

        maxLen = 0
        resultVote = None

        for voteOb in voting_ar:
            l = len(voteOb.values())
            if l > maxLen:
                maxLen = l
                resultVote = voteOb

        user_id = voteOb.keys()[0]
        user = SqlDriver.getUsersByIds([user_id])[0]

        user.isAlive = False

        db.session.commit()

        return user

    @staticmethod
    def isFinished(join_id):
        game = SqlDriver.getGameSessionByJoinId(join_id)
        return game.gameStatus == GameStatus.finished.value

