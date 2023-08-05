import getpass
import os
import json
import requests
import uuid

class GithubException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Github:

    def get_credential(self,scopes,save_path):
        if os.path.isfile(save_path):
            with open(save_path) as f:
                return json.loads(f.read())

        user = auth()

        hash_str = uuid.uuid1()
        payload = {"scopes": scopes, "note": "use gist_it #%s" % hash_str}

        response = requests.post("https://api.github.com/authorizations", data=json.dumps(payload), auth=(user[0], user[1]))
        if response.status_code is not 201:
            raise GithubException("github oauth api error: %s" % response.text)

        with open(save_path, "w") as f:
            f.write(response.text)
        return json.loads(response.text)

def auth():
    user_name = raw_input('user_name : ')
    password = getpass.getpass('password  : ')
    if not user_name or not password:
        raise GithubException("username or password is not found")

    return user_name, password

if __name__ == '__main__':
    pass
