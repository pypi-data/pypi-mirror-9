#Django imports
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory

from social.apps.django_app.utils import load_strategy
from social.backends.email import EmailAuth
from social.backends.google import GoogleOAuth2
from social.exceptions import AuthException

#App imports
from .. import referrer_url_session_key, referring_user_pk_session_key
from ..pipeline import check_password, set_password, set_referral_data

#Test imports
from .base import BaseTestCase


User = get_user_model()


class CheckPasswordTestCase(BaseTestCase):
    def setUp(self):
        super(CheckPasswordTestCase, self).setUp()
        
        self.factory = RequestFactory()
        
        self.set_session()
        
        self.session = self.client.session
        self.session.save()
    
    def test_no_user(self):
        request = self.factory.get('/?password=bar')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        ret = check_password(backend=backend, user=None)
    
    def test_no_user_no_password(self):
        request = self.factory.get('/')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        with self.assertRaises(AuthException):
            check_password(backend=backend, user=None)
    
    def test_existing_user_wrong_password(self):
        request = self.factory.get('/?password=bar')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        with self.assertRaises(AuthException):
            check_password(backend=backend, user=user)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertTrue(user.check_password('foo'))
    
    def test_existing_user_right_password(self):
        request = self.factory.get('/?password=foo')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        ret = check_password(backend=backend, user=user)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertTrue(user.check_password('foo'))
    
    def test_new_user_but_not_email_backend(self):
        request = self.factory.get('/?password=bar')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = GoogleOAuth2(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        ret = check_password(backend=backend, user=user)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertTrue(user.check_password('foo'))


class SetPasswordTestCase(BaseTestCase):
    def setUp(self):
        super(SetPasswordTestCase, self).setUp()
        
        self.factory = RequestFactory()
        
        self.set_session()
        
        self.session = self.client.session
        self.session.save()
    
    def test_new_user(self):
        request = self.factory.get('/?password=bar')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        ret = set_password(backend=backend, user=user, is_new=True)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertTrue(user.check_password('bar'))
    
    def test_new_user_no_password(self):
        request = self.factory.get('/')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        with self.assertRaises(AuthException):
            set_password(backend=backend, user=user, is_new=True)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertTrue(user.check_password('foo'))
    
    def test_existing_user_wrong_password(self):
        """
        A different pipeline makes sure the password is correct.
        """
        request = self.factory.get('/?password=bar')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        set_password(backend=backend, user=user)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertTrue(user.check_password('foo'))
    
    def test_existing_user_right_password(self):
        request = self.factory.get('/?password=foo')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        ret = set_password(backend=backend, user=user)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertTrue(user.check_password('foo'))
    
    def test_new_user_but_not_email_backend(self):
        request = self.factory.get('/?password=bar')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = GoogleOAuth2(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        ret = set_password(backend=backend, user=user, is_new=True)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertTrue(user.check_password('foo'))


class SetReferralDataTestCase(BaseTestCase):
    def setUp(self):
        super(SetReferralDataTestCase, self).setUp()
        
        self.factory = RequestFactory()
        
        self.set_session()
        
        self.session = self.client.session
        self.session.save()
    
    def test_data_not_present(self):
        request = self.factory.get('/')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        set_referral_data(backend=backend, user=user)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertEqual(user.referrer_url, '')
        self.assertEqual(user.referring_user, None)
    
    def test_data_present(self):
        referrer_url = 'http://example.com/'
        
        self.session[referring_user_pk_session_key] = self.user1.pk
        self.session[referrer_url_session_key] = referrer_url
        self.session.save()
        
        request = self.factory.get('/')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        set_referral_data(backend=backend, user=user)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertEqual(user.referrer_url, referrer_url)
        self.assertEqual(user.referring_user, self.user1)
    
    def test_user_pk_not_found(self):
        referrer_url = 'http://example.com/'
        
        self.session[referring_user_pk_session_key] = 100
        self.session[referrer_url_session_key] = referrer_url
        self.session.save()
        
        request = self.factory.get('/')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        set_referral_data(backend=backend, user=user)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertEqual(user.referrer_url, referrer_url)
        self.assertEqual(user.referring_user, None)
    
    def test_invalid_user_pk(self):
        referrer_url = 'http://example.com/'
        
        self.session[referring_user_pk_session_key] = 'foo'
        self.session[referrer_url_session_key] = referrer_url
        self.session.save()
        
        request = self.factory.get('/')
        request.session = self.session
        
        strategy = load_strategy(request=request)
        
        backend = EmailAuth(strategy=strategy)
        
        user = User.objects.create_user('foo@example.com', password='foo')
        
        set_referral_data(backend=backend, user=user)
        
        user = User.objects.get(pk=user.pk)
        
        self.assertEqual(user.referrer_url, referrer_url)
        self.assertEqual(user.referring_user, None)

