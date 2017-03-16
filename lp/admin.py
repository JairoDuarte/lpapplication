from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User

class UserCreationForm(forms.ModelForm):
    """
    Un formulaire pour la création de nouveaux utilisateurs
    """
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmation de mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Vérifier si les deux mots de passes sont identiques
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Mots de passes non-identiques')
        return password2

    def save(self, commit=True):
        # Enregistrer le mot de passe dans un format hashé
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_admin = True
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """
    Un formulaire pour la modification d'un utilisateur existant.
    On y utilise un champ permettant de ne pas modifier le mot de passe.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password')

    def clean_password(self):
        return self.initial['password']

class UserAdmin(BaseUserAdmin):
    """
    Panneau d'administration d'utilisateurs (administrateurs)
    """
    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
    )

    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
    )

    list_display = ('email',)
    list_filter = ('is_admin',)
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
