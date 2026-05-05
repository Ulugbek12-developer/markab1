from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[('customer', 'Oluvchi/Ko\'ruvchi'), ('seller_user', 'Sotuvchi')],
        widget=forms.RadioSelect,
        initial='customer',
        label="Siz kimsiz?"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role',)
