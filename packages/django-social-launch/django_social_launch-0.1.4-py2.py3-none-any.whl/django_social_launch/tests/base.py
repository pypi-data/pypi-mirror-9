#Python imports
from importlib import import_module

#Django imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase


User = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        self.username = 'foo'
        self.password = 'foopw'
        self.user1 = User.objects.create_user(self.username, 'sean@the.jedi', self.password)
    
    def set_session(self, **kwargs):
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        
        # if the cookie isn't set, self.client.session is just a dict instead of a session object.
        if isinstance(self.client.session, dict):
            self.client.cookies[settings.SESSION_COOKIE_NAME] = ''
        
        session = self.client.session
        for k, v in kwargs.items():
            session[k] = v
        
        session.save()
        
        self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key
