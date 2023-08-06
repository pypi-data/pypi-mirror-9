#Django imports
from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class UserSignupForm(forms.ModelForm):
    referrer_url = forms.CharField(required=False, widget=forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['email'].widget.attrs['placeholder'] = 'me@example.com'
    
    class Meta:
        model = User
        fields = ('email',)
