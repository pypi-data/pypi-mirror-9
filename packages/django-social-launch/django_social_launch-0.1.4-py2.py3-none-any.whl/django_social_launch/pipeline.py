from django.contrib.auth import get_user_model

from social.exceptions import AuthException

from . import referrer_url_session_key, referring_user_pk_session_key


User = get_user_model()


def check_password(backend, user, *args, **kwargs):
    if backend.name != 'email':
        return

    password = backend.strategy.request_data().get('password')
    
    if password is None:
        raise AuthException(backend)
    
    if user and not user.check_password(password):
        raise AuthException(backend)


def set_password(backend, user, is_new=False, *args, **kwargs):
    if backend.name != 'email':
        return

    password = backend.strategy.request_data().get('password')
    
    if password is None:
        raise AuthException(backend)
    
    if is_new:
        user.set_password(password)
        user.save()


def set_referral_data(backend, user, *args, **kwargs):
    referring_user = None
    
    referrer_url = backend.strategy.session_get(referrer_url_session_key, '')
    referring_user_pk = backend.strategy.session_get(referring_user_pk_session_key, None)
    
    if referring_user_pk:
        try:
            referring_user = User.objects.get(pk=referring_user_pk)
        except ValueError:
            pass
        except User.DoesNotExist:
            pass
    
    user.referrer_url = referrer_url
    user.referring_user = referring_user
    user.save()

