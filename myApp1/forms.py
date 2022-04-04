from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User
from django.forms import ModelForm

from myApp1.models import Customer


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        common_field_css = {'class': 'p-2 my-3 text-lg font-medium mb-3 text-black'}
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(common_field_css)
        self.fields['phone'].widget.attrs.update(common_field_css)
        self.fields['email'].widget.attrs.update(common_field_css)
        self.fields['profile_pic'].widget.attrs.update(common_field_css)
