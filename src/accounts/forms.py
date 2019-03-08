from django import forms
from django.contrib.auth import authenticate, get_user_model, login, logout


User = get_user_model()

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if username and password:
            if not user:
                raise forms.ValidationError('This user does not exist')
            if not user.check_password(password):
                raise forms.ValidationError('Password incorrect')
            if not user.is_active:
                raise forms.ValidationError('User disabled')

        return super(UserLoginForm, self).clean(*args, **kwargs)

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email')
    email2 = forms.EmailField(label='Confirm email')
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'email2', 'password']

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        if email != email2:
            raise forms.ValidationError('Emails must match')
        emails_qs = User.objects.filter(email=email)
        if emails_qs.exists():
            raise forms.ValidationError('Email already exists, please use other')
        return super(UserRegisterForm, self).clean(*args, **kwargs)

    # def clean_email2(self):
    #     email = self.cleaned_data.get('email')
    #     email2 = self.cleaned_data.get('email2')
    #     if email != email2:
    #         raise forms.ValidationError('Emails must match')
    #     emails_qs = User.objects.filter(email=email)
    #     if emails_qs.exists():
    #         raise forms.ValidationError('Email already exists, please use other')
    #     return email