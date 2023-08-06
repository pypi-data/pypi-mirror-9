from django import forms

from mailtest.validators import MailTestValidator

class EmailMailTestField(forms.EmailField):
    default_validators = forms.EmailField.default_validators + \
        [MailTestValidator]
