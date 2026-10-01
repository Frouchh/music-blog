from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import AuthorProfile, Role, User


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [(Role.BUYER, 'Покупатель'), (Role.AUTHOR, 'Автор')]

    email = forms.EmailField(label='E-mail')
    role = forms.ChoiceField(label='Я регистрируюсь как', choices=ROLE_CHOICES)
    stage_name = forms.CharField(label='Псевдоним автора', max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким e-mail уже существует')
        return email

    def clean(self):
        data = super().clean()
        if data.get('role') == Role.AUTHOR and not data.get('stage_name'):
            self.add_error('stage_name', 'Укажите псевдоним автора')
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Role.objects.get(name=self.cleaned_data['role'])
        if commit:
            user.save()
            if user.role.name == Role.AUTHOR:
                AuthorProfile.objects.create(user=user, stage_name=self.cleaned_data['stage_name'])
        return user


class LoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_blocked:
            raise forms.ValidationError('Учётная запись заблокирована администратором',
                                        code='blocked')


class AuthorProfileForm(forms.ModelForm):
    class Meta:
        model = AuthorProfile
        fields = ['stage_name', 'payout_details']
