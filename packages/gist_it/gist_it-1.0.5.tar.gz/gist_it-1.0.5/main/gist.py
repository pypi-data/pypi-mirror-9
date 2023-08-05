import os
import requests
import json
from github import Github

class GistException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Gist:

    scope = ["gist"]

    def __init__(self,credential_path):
        self.credential_path = credential_path

    def create(self,file_name,content,description="",public=False,is_auth=False):
        headers = {}
        if is_auth:
            credential = Github().get_credential(Gist.scope, self.credential_path)
            if not credential:
                raise GistException("Github oauth error")

            headers = {'Authorization': 'token %s' % str(credential["token"])}

        payload = {"description": description, "public": public, "files": { file_name: {"content": content}}}
        response = requests.post("https://api.github.com/gists", data=json.dumps(payload), headers=headers)
        if response.status_code is not 201:
            raise GistException("gist api error: %s" % response.text)
        return json.loads(response.text)

if __name__ == '__main__':
    pass
