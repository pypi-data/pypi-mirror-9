#Django imports
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

#App imports
from . import referrer_url_session_key, referring_user_pk_session_key, user_successfully_created_msg
from .forms import UserSignupForm


User = get_user_model()


def index(request, referring_user_pk=None):
    referring_user = None
    has_registered = False
    referrer_count = None
    form = None
    
    if referring_user_pk is not None:
        try:
            referring_user = get_object_or_404(User, id=referring_user_pk)
        except ValueError:
            raise Http404
    
    has_registered = request.user.is_authenticated()
    
    if has_registered:
        if not referring_user_pk:
            return redirect('social_launch_referral', referring_user_pk=request.user.pk)
        
        referrer_count = User.objects.filter(referring_user=referring_user).count()
    else:
        form = UserSignupForm()
        
        if referrer_url_session_key not in request.session:
            request.session[referrer_url_session_key] = request.META.get('HTTP_REFERER', '')
        if referring_user_pk_session_key not in request.session:
            request.session[referring_user_pk_session_key] = referring_user_pk if referring_user_pk is not None else ''
        
    return render(request, 'social_launch/index.html', {
        'form' : form,
        'has_registered' : has_registered,
        'referrer_count' : referrer_count,
    })

