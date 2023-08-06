from django import forms


class SignupForm(forms.Form):
    email = forms.EmailField()
    tracking = forms.CharField(initial='signup-module', widget=forms.HiddenInput, required=False)
