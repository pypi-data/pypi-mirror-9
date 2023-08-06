from django.forms import ModelForm, ValidationError
from django.contrib.admin.widgets import AdminTextInputWidget
from django.core.urlresolvers import reverse_lazy
from django.utils.crypto import get_random_string

try:
    from pureftpd_admin.localdir.widgets import LocalDirAdminWidget as PathWidget
except ImportError:
    from django.forms import Textarea as PathWidget

from pureftpd_admin.models import FtpUsers
import pureftpd_admin.settings as ftpusets_settings

__author__ = 'ivan'


class FtpUsersAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('instance'):
            kwargs['initial'] = {'password': get_random_string(6)}
        super(FtpUsersAdminForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "autocomplete": "off"
        })
        self.fields["password"].widget.attrs.update({
            "autocomplete": "off"
        })

    def clean_password(self):
        data = self.cleaned_data['password']
        if len(data) < 6:
            raise ValidationError("Password is very simple, minimal must be 6 characters!")
        return data

    class Meta:
        model = FtpUsers
        widgets = {
            'path': PathWidget(attrs={'popup_url': reverse_lazy('localdir-ftpusers-url', kwargs={'path': ''}),
                                      'document_root': ftpusets_settings.ROOT_PATH}),
            'password': AdminTextInputWidget(attrs={'autocomplete': 'off'}),
            'username': AdminTextInputWidget(attrs={'autocomplete': 'off'}),
        }