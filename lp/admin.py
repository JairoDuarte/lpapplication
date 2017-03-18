from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from . import models
from .forms import CandidatForm

class UserCreationForm(forms.ModelForm):
    """
    Un formulaire pour la création de nouveaux utilisateurs
    """
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmation de mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = models.User
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
        model = models.User
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

class BaremeAgeAdmin(admin.ModelAdmin):
    """
    Panneau d'administration de barèmes d'âge
    """
    list_display = ('age_max', 'note_preselection',)

class BaremeAnneesDiplomeAdmin(admin.ModelAdmin):
    """
    Panneau d'administration de barèmes d'années du diplôme
    """
    list_display = ('annees_max', 'note_preselection',)

class CandidatAdmin(admin.ModelAdmin):
    """
    Panneau d'administration de candidats
    """
    form = CandidatForm
    list_display = ('cin', 'cne', 'nom', 'prenom', 'note_preselection',)
    change_form_template = 'admin/change_form_candidat.html'

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update(self.form.context_data(request))
        return super(CandidatAdmin, self).render_change_form(request, context, add, change, form_url, obj)

class FiliereDiplomeAdmin(admin.ModelAdmin):
    """
    Panneau d'administration de filières de diplômes
    """
    list_display = ('libelle', 'type_diplome_libelle',)

class OptionDiplomeAdmin(admin.ModelAdmin):
    """
    Panneau d'administration de filières de diplômes
    """
    list_display = ('libelle', 'filiere_diplome_libelle', 'type_diplome_libelle',)

class MentionBacAdmin(admin.ModelAdmin):
    """
    Panneau d'administration de mentions de bac
    """
    list_display = ('libelle', 'note_preselection',)

admin.site.register(models.User, UserAdmin)
admin.site.register(models.BaremeAge, BaremeAgeAdmin)
admin.site.register(models.BaremeAnneesDiplome, BaremeAnneesDiplomeAdmin)
admin.site.register(models.Candidat, CandidatAdmin)
admin.site.register(models.Filiere)
admin.site.register(models.TypeDiplome)
admin.site.register(models.FiliereDiplome, FiliereDiplomeAdmin)
admin.site.register(models.OptionDiplome, OptionDiplomeAdmin)
admin.site.register(models.TypeBac)
admin.site.register(models.MentionBac, MentionBacAdmin)

admin.site.unregister(Group)
