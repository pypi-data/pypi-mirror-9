from django import forms

from mailtest.validators import MailTestValidator

class EmailField(forms.EmailField):
    default_validators = forms.EmailField.default_validators + \
        [MailTestValidator]
