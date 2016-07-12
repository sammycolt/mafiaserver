import json

class Json():
    @staticmethod
    def encode_user_id_list(json_users):
        user_id_list = json.loads(json_users)
        return user_id_list