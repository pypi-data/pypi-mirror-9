from requests.auth import AuthBase

class TokenAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Token %s'%self.token
        return r
