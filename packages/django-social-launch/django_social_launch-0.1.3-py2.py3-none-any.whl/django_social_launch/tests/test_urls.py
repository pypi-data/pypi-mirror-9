#Django imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib.sessions.backends.db import SessionStore

#App imports
from .. import user_successfully_created_msg, referrer_url_session_key

#Test imports
from .base import BaseTestCase


User = get_user_model()


class IndexTestCase(BaseTestCase):
    def test_get(self):
        response = self.client.get(reverse('social_launch_index'))
        
        self.assertEqual(response.status_code, 200)
        
    def test_get_with_referrer(self):
        referrer_url = 'http://facebook.com'
        response = self.client.get(reverse('social_launch_index'), HTTP_REFERER=referrer_url)
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(self.client.session[referrer_url_session_key], referrer_url)
    
    def test_get_logged_in(self):
        self.client.login(username=self.username, password=self.password)
        
        response = self.client.get(reverse('social_launch_index'))
        
        self.assertRedirects(response, reverse('social_launch_referral', kwargs={'referring_user_pk': self.user1.pk}))


class ReferralTestCase(BaseTestCase):
    def test_get_success(self):
        response = self.client.get(reverse('social_launch_referral', kwargs={'referring_user_pk' : self.user1.id}))
        
        self.assertEqual(response.status_code, 200)
    
    def test_get_success_logged_in(self):
        self.client.login(username=self.username, password=self.password)
        
        response = self.client.get(reverse('social_launch_referral', kwargs={'referring_user_pk' : self.user1.id}))
        
        self.assertEqual(response.status_code, 200)
        
    def test_get_fails_invalid_id(self):
        response = self.client.get(reverse('social_launch_referral', kwargs={'referring_user_pk' : 'foo'}))
        
        self.assertEqual(response.status_code, 404)
        
    def test_get_fails_no_such_user(self):
        response = self.client.get(reverse('social_launch_referral', kwargs={'referring_user_pk' : 1000}))
        
        self.assertEqual(response.status_code, 404)
