from django import forms
from django.utils.translation import ugettext_lazy as _
#import settings
from cmsplugin_contact.nospam.forms import HoneyPotForm, RecaptchaForm, AkismetForm
  
class ContactForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    subject = forms.CharField(label=_("Subject"), required=False)
    content = forms.CharField(label=_("Content"), widget=forms.Textarea())

    template = "cmsplugin_contact/contact.html"
  
class HoneyPotContactForm(HoneyPotForm):
    pass

class AkismetContactForm(AkismetForm):
    akismet_fields = {
        'comment_author_email': 'email',
        'comment_content': 'content'
    }
    akismet_api_key = None
    

class RecaptchaContactForm(RecaptchaForm):
    recaptcha_public_key = None
    recaptcha_private_key = None
    recaptcha_theme = None
