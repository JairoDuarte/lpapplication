from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.forms import widgets

from . import models
from .forms import CandidatForm
from .utils import Countries

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

class VilleAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VilleAdminForm, self).__init__(*args, **kwargs)
        self.fields['pays'].widget = widgets.Select(choices=Countries.CHOICES)
        self.fields['pays'].initial = self.fields['pays'].initial or 'maroc'
    class Meta:
        model = models.Ville
        fields = '__all__'

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
    list_display = ('nb_redoublements', 'note_preselection',)

class CandidatAdmin(admin.ModelAdmin):
    """
    Panneau d'administration de candidats
    """
    form = CandidatForm
    list_display = ('short_cin', 'short_cne', 'nom', 'prenom', 'note_preselection', 'short_filiere', 'email_valide',)
    change_form_template = 'admin/change_form_candidat.html'
    list_filter = ('filiere_choisie',)
    search_fields = ('cne', 'cin', 'nom', 'prenom',)
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update(context['adminform'].form.context_data())
        return super(CandidatAdmin, self).render_change_form(request, context, add, change, form_url, obj)

class OptionDiplomeInline(admin.TabularInline):
    """
    Formulaire de modification d'options de diplômes imbriqué
    """
    model = models.OptionDiplome
    extra = 1

class FiliereDiplomeAdmin(admin.ModelAdmin):
    """
    Panneau d'administration de filières de diplômes
    """
    list_display = ('libelle', 'type_diplome_libelle',)
    inlines = [OptionDiplomeInline]

class FiliereDiplomeInline(admin.TabularInline):
    """
    Formulaire de modification de filières de diplômes imbriqué
    """
    model = models.FiliereDiplome
    show_change_link = True
    extra = 1

class TypeDiplomeAdmin(admin.ModelAdmin):
    """
    Panneau d'administration de types de diplômes
    """
    inlines = [FiliereDiplomeInline]

class MentionBacAdmin(admin.ModelAdmin):
    """
    Panneau d'administration de mentions de bac
    """
    list_display = ('libelle', 'note_preselection',)

class VilleAdmin(admin.ModelAdmin):
    form = VilleAdminForm

admin.site.register(models.User, UserAdmin)
admin.site.register(models.BaremeAge, BaremeAgeAdmin)
admin.site.register(models.BaremeAnneesDiplome, BaremeAnneesDiplomeAdmin)
admin.site.register(models.Candidat, CandidatAdmin)
admin.site.register(models.Filiere)
admin.site.register(models.TypeDiplome, TypeDiplomeAdmin)
admin.site.register(models.FiliereDiplome, FiliereDiplomeAdmin)
admin.site.register(models.TypeBac)
admin.site.register(models.MentionBac, MentionBacAdmin)
admin.site.register(models.Ville, VilleAdmin)

admin.site.unregister(Group)
