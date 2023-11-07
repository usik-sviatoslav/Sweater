from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


def invalid_form(self, form):
    field = dict(self.fields.items()).get(form)
    field.widget.attrs['class'] += ' is-invalid'


def valid_form(self, form):
    field = dict(self.fields.items()).get(form)
    field.widget.attrs['class'] += ' is-valid'


class LoginPage(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
        labels = {'password': 'Пароль'}
        widgets = {'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'xxxxxxxx'})}

    email = forms.EmailField(label='Електронна пошта', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'example@gmail.com'}))

    def clean(self):
        email = self.cleaned_data.get('email').lower()
        password = self.cleaned_data.get('password')

        user = User.objects.filter(email=email).first()
        if user is None:
            invalid_form(self, 'email')
            self.add_error('email', 'Немає такого користувача!')
        elif not user.check_password(password):
            valid_form(self, 'email')
            invalid_form(self, 'password')
            self.add_error('password', 'Не правильний пароль!')


class RegistrationPage(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1']

    first_name = forms.CharField(
        label='Ім\'я *',
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    last_name = forms.CharField(
        label='Прізвище *',
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(
        label='Електронна пошта *',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@gmail.com'}))

    password1 = forms.CharField(
        label='Пароль *', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'xxxxxxxx'}))

    password2 = forms.CharField(
        label='Підтвердження паролю *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'xxxxxxxx'}))

    def clean_password2(self):

        def validate_form(field, field_name):
            field_length = len(field)
            sequence_length = 5

            for i in range(field_length - sequence_length + 1):
                sequence_to_check = field[i:i + sequence_length]
                if sequence_to_check.lower() in password1.lower():
                    return f"Пароль не повинен містити частину вашого {field_name}."
            return None

        password_errors = []
        email = self.cleaned_data.get('email')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        password_errors.append(validate_form(email, "email"))
        password_errors.append(validate_form(first_name, "ім'я"))
        password_errors.append(validate_form(last_name, "прізвища"))

        min_len_password = 8
        if len(password1) <= min_len_password:
            password_errors += forms.ValidationError(f"Пароль не повинен бути менше {min_len_password} символів.")

        password_errors = [error for error in password_errors if error is not None]

        user = User.objects.filter(email=email).first()
        if user is None:
            valid_form(self, 'email')
        else:
            invalid_form(self, 'email')
            self.add_error('email', 'Користувач з таким email вже існує.')

        if first_name.isalpha():
            valid_form(self, 'first_name')
        else:
            invalid_form(self, 'first_name')
            self.add_error('last_name', "Ім'я не може містити в собі числа.")

        if last_name.isalpha():
            valid_form(self, 'last_name')
        else:
            invalid_form(self, 'last_name')
            self.add_error('last_name', 'Прізвище не може містити в собі числа.')

        if password_errors:
            invalid_form(self, 'password1')
            self.add_error('password1', password_errors)
        else:
            if password1 != password2:
                invalid_form(self, 'password2')
                raise forms.ValidationError('Паролі не співпадають!')


class EditUserProfilePage(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'bio', 'birth_date']

    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    first_name = forms.CharField(
        label='Ім\'я',
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    last_name = forms.CharField(
        label='Прізвище',
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    email = forms.EmailField(
        label='Електронна пошта',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@gmail.com'}), required=False)

    bio = forms.CharField(
        label='Про себе',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}),
        required=False)

    birth_date = forms.DateField(
        label='День народження',
        widget=forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False)

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
