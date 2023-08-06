from flask import request, session
from flask_oauthlib.client import OAuthException

config = {
    'id': 'facebook',
    'name': 'Facebook',
    'request_token_params': {'scope': 'email'},
    'base_url': 'https://graph.facebook.com',
    'request_token_url': None,
    'access_token_url': '/oauth/access_token',
    'authorize_url': 'https://www.facebook.com/dialog/oauth'
}


def initial(self, callback, *args, **kwargs):
    return self.authorize(callback=callback, *args, **kwargs)


def login(self):
    resp = self.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message
    session['token'] = (resp['access_token'], '')
    me = self.get('/me')
    return {
        'user': me.data,
        'token': session['token']
        }