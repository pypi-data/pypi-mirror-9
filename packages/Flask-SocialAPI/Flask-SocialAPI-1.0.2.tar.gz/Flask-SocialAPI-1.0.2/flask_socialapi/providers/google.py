from flask import request, session

config = {
    'id': 'google',
    'name': 'Google',
    'request_token_params': {
        'scope': 'https://www.googleapis.com/auth/userinfo.email'
    },
    'base_url': 'https://www.googleapis.com/oauth2/v1/',
    'request_token_url': None,
    'access_token_method': 'POST',
    'access_token_url': 'https://accounts.google.com/o/oauth2/token',
    'authorize_url': 'https://accounts.google.com/o/oauth2/auth'
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
    session['token'] = (resp['access_token'], '')
    me = self.get('userinfo')
    return {
        'user': me.data,
        'token': session['token']
        }