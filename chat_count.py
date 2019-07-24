import json

from settings import RDB

def set_redis(to_user,from_user):
    to_user_json=RDB.get(to_user)
    if to_user_json:
        to_user_dict=json.loads(to_user_json)
        count=to_user_dict.get(from_user)
        to_user_dict[from_user] = count + 1 if count else 1
        # if count:
        #     to_user_dict[from_user]+=1
        # else:
        #     to_user_dict[from_user]=1
        to_user_json=json.dumps(to_user_dict)
        RDB.set(to_user,to_user_json)
    else:
        RDB.set(to_user,json.dumps({from_user:1}))

def get_redis(to_user,from_user):
    count=0
    to_user_json=RDB.get(to_user)
    if to_user_json:
        to_user_dict=json.loads(to_user_json)

        count=to_user_dict.pop(from_user,0)
        # count=to_user_dict.get(from_user,0)
        # if count:
        #     to_user_dict[from_user]=0

        to_user_json = json.dumps(to_user_dict)
        RDB.set(to_user, to_user_json)
    return count




