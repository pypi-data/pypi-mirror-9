#Django imports
from django.conf.urls import *

#App imports
from .views import index

# place app url patterns here
urlpatterns = patterns('',
    url(r'^$', index, name='social_launch_index'),
    url(r'^referrers/(?P<referring_user_pk>.+)/$', index, name='social_launch_referral'),
)
