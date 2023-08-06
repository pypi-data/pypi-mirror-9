#Django imports
from django.conf import settings
from django.db import models

# Create your models here.

class SocialLaunchUserMixin(models.Model):
    referrer_url        = models.CharField(blank=True, max_length=255, help_text="The URL that led the user to this site.")
    referring_user      = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='referred_users')
    
    class Meta:
        abstract = True

