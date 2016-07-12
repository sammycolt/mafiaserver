import json

class Json():
    @staticmethod
    def encode_user_id_list(json_users):
        user_id_list = json.loads(json_users)
        return user_id_list

    @staticmethod
    def deparseVoting(a):
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
            dict[user] = users
            ans.append(dict)
        return ans