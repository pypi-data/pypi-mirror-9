from flask import session
from flask_oauthlib.client import OAuth, OAuthRemoteApp as Base
from importlib import import_module


class OAuthRemoteApp(Base):
    def __init__(self, id, *args, **kwargs):
        Base.__init__(self, oauth=None, *args, **kwargs)
        self.id = id
        module_name = "flask_socialapi.providers.%s" % self.id
        self.module = import_module(module_name)

    def initial(self, callback, *args, **kwargs):
        return self.module.initial(self, callback, *args, **kwargs)

    def login(self):
        return self.module.login(self)


def _get_token():
    return session.get('token')


class Social(object):
    providers = None

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = OAuth(app)
        providers = dict()
        for k, c in app.config.items():
            if not k.startswith('SOCIAL_') or c is None or k.endswith('ID'):
                continue
            name = k.split("_")[1]
            appid = app.config.get("SOCIAL_%s_APP_ID" % name.upper())
            appsecret = app.config.get("SOCIAL_%s_APP_SECRET" % name.upper())
            name = name.lower()
            module_name = "flask_socialapi.providers.%s" % name
            module = import_module(module_name)
            config = module.config
            config['consumer_key'] = appid
            config['consumer_secret'] = appsecret
            providers[name] = OAuthRemoteApp(**config)
            providers[name].tokengetter(_get_token)
        self.providers = providers