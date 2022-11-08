from django import forms

class MessageForm(forms.Form):
    name = forms.CharField(max_length=50, required=False)
    message = forms.CharField(max_length=140, required=True)

class LoginForm(forms.Form):
    username = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)