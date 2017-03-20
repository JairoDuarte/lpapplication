from django import forms
from django.utils import timezone
from django.forms import widgets
from decimal import Decimal

from . import models
from .utils import Countries, lp_settings
from .widgets import DateSelectorWidget, SchoolYearWidget, CustomModelSelect

class SettingsForm(forms.ModelForm):
    class Meta:
        model = models.Settings
        fields = '__all__'
    def clean_age_max(self):
        age = self.cleaned_data.get('age_max')
        if age < 17:
            raise forms.ValidationError('Âge maximal doit être supérieur ou égale à 17')
        return age
    def clean_age_bac_max(self):
        age = self.cleaned_data.get('age_bac_max')
        if age < 2:
            raise forms.ValidationError('Âge maximal du Bac doit être supérieur ou égale à 2')
        return age

class EmailForm(forms.Form):
    email = forms.EmailField()
    def clean_email(self):
        email = self.cleaned_data.get('email')
        candidat = models.Candidat.objects.filter(email=email)
        if len(candidat) == 0:
            raise forms.ValidationError("Aucun candidat n'existe avec l'adresse email fournie")
        return email

class PasswordForm(forms.Form):
    password = forms.CharField(min_length=6, widget=forms.PasswordInput)
    password_confirm = forms.CharField(min_length=6, widget=forms.PasswordInput)
    def clean_password_confirm(self):
        # Vérifier si les deux mots de passes sont identiques
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_confirm')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Mots de passe non-identiques')
        return password2

class CandidatForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Init parent
        if 'initial' not in kwargs:
            kwargs['initial'] = {
                'nationalite': 'maroc',
                'pays_naissance': 'maroc',
                'pays_residence': 'maroc',
            }
        super(CandidatForm, self).__init__(*args, **kwargs)
        # prepare data
        settings = lp_settings()
        current_year = timezone.now().year
        birthdate_widget = DateSelectorWidget(current_year - settings.age_max, current_year - 10)
        min_annee_diplome = current_year - settings.age_bac_max + 2
        min_annee_bac = current_year - settings.age_bac_max
        # Make default inputs
        countries_input = widgets.Select(choices=Countries.LIST)
        mark_input = widgets.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '20'})
        empty_select = widgets.Select()
        # Set default inputs
        self.fields['nationalite'].widget = countries_input
        self.fields['date_naissance'].widget = birthdate_widget
        self.fields['pays_naissance'].widget = countries_input
        self.fields['email'].widget = widgets.EmailInput()
        self.fields['adresse_residence'].widget = widgets.Textarea(attrs={'rows': 3})
        self.fields['pays_residence'].widget = countries_input
        self.fields['note_s1'].widget = mark_input
        self.fields['note_s2'].widget = mark_input
        self.fields['note_s3'].widget = mark_input
        self.fields['note_s4'].widget = mark_input
        self.fields['note_a1'].widget = mark_input
        self.fields['note_a2'].widget = mark_input
        self.fields['annee_s1'].widget = SchoolYearWidget(min_annee_diplome, current_year)
        self.fields['annee_s2'].widget = SchoolYearWidget(min_annee_diplome, current_year)
        self.fields['annee_s3'].widget = SchoolYearWidget(min_annee_diplome + 1, current_year)
        self.fields['annee_s4'].widget = SchoolYearWidget(min_annee_diplome + 1, current_year)
        self.fields['annee_bac'].widget = SchoolYearWidget(min_annee_bac, current_year - 2)
        self.fields['type_diplome'].widget = CustomModelSelect(models.TypeDiplome, True)
        self.fields['filiere_diplome'].widget = empty_select
        self.fields['option_diplome'].widget = empty_select
        self.fields['type_bac'].widget = CustomModelSelect(models.TypeBac, True)
        self.fields['mention_bac'].widget = CustomModelSelect(models.MentionBac, False)
        self.fields['filiere_choisie'].widget = empty_select
    def context_data(self):
        form_type_diplome = self['type_diplome'].value()
        form_filiere_diplome = self['filiere_diplome'].value()
        form_option_diplome = self['option_diplome'].value()
        form_filiere_choisie = self['filiere_choisie'].value()
        # Préparer la liste des types, filières et options de diplômes
        types_diplome = []
        for type_diplome in models.TypeDiplome.objects.all():
            filieres_diplome = []
            for filiere_diplome in type_diplome.filierediplome_set.all():
                options_diplome = []
                for option_diplome in filiere_diplome.optiondiplome_set.all():
                    options_diplome.append('"%i":"%s"' % (option_diplome.pk, option_diplome.libelle.replace('"', '\\\"')))
                filieres_diplome.append('"%i": {"label": "%s", "options": {%s}}' % (filiere_diplome.pk, filiere_diplome.libelle.replace('"', '\\\"'), ','.join(options_diplome)))
            types_diplome.append('"%i": {"label": "%s", "filieres": {%s}}' % (type_diplome.pk, type_diplome.libelle.replace('"', '\\\"'), ','.join(filieres_diplome)))
        arbre_diplome_json = '{%s}' % ','.join(types_diplome)
        # Préparer la liste des filières et leurs diplômes corréspondants
        filieres = []
        for filiere in models.Filiere.objects.all():
            types_diplome = [
                ('"%i"' % type_diplome.pk)
                for type_diplome in filiere.types_diplome.all()
            ]
            filieres_diplome = [
                ('"%i"' % filiere_diplome.pk)
                for filiere_diplome in filiere.filieres_diplome.all()
            ]
            options_diplome = [
                ('"%i"' % option_diplome.pk)
                for option_diplome in filiere.options_diplome.all()
            ]
            filieres.append('"%i": {"label": "%s", "diplomes": [%s], "filieres": [%s], "options": [%s]}' % (filiere.pk, filiere.libelle, ','.join(types_diplome), ','.join(filieres_diplome), ','.join(options_diplome)))
        filieres_json = '{%s}' % ','.join(filieres)
        return {
            'arbre_diplome_json': arbre_diplome_json,
            'filieres_json': filieres_json,
            'type_diplome': form_type_diplome,
            'filiere_diplome': form_filiere_diplome,
            'option_diplome': form_option_diplome,
            'filiere_choisie': form_filiere_choisie,
        }
    def __str__(self):
        html = ''
        for title, fields in CandidatForm.fieldsets:
            html += '<h2>' + title + '</h2>'
            for fieldname in fields:
                field = self[fieldname]
                html += '<div class="field-%s"><label for="%s">%s :</label><div class="widget">%s</div>' % (fieldname, field.id_for_label, field.label, field.as_widget())
                errors = field.errors
                if len(errors) > 0:
                    html += '<ul class="errors">'
                    for error in errors:
                        html += '<li>%s</li>' % error
                    html += '</ul>'
                html += '</div>'
        return html
    def save(self, commit=True):
        candidat = super(CandidatForm, self).save(commit=False)
        # Calculer la note de préselection
        candidat.note_preselection = \
            Decimal('0.25') * candidat.note_a1 + \
            Decimal('0.25') * candidat.note_a2 + \
            Decimal('0.15') * candidat.mention_bac.note_preselection + \
            Decimal('0.15') * Decimal('20') + \
            Decimal('0.20') * Decimal('20')
        if commit:
            candidat.save()
        return candidat
    class Meta:
        model = models.Candidat
        exclude = ['user', 'jeton_validation', 'note_preselection']
    fieldsets = (
        ('Informations personnelles', ('cin', 'cne', 'nom', 'prenom', 'nationalite', 'ville_naissance', 'pays_naissance', 'date_naissance', 'email', 'telephone_gsm', 'telephone_fixe', 'adresse_residence', 'ville_residence', 'pays_residence',)),
        ('Informations sur le diplôme', ('note_s1', 'annee_s1', 'note_s2', 'annee_s2', 'note_a1', 'note_s3', 'annee_s3', 'note_s4', 'annee_s4', 'note_a2', 'type_diplome', 'type_diplome_autre', 'filiere_diplome', 'option_diplome',)),
        ('Informations sur le Bac', ('type_bac', 'type_bac_autre', 'annee_bac', 'mention_bac',)),
        ('Informations sur la filière', ('filiere_choisie',)),
    )

class CandidatChangeForm(CandidatForm):
    def __init__(self, *args, **kwargs):
        super(CandidatChangeForm, self).__init__(*args, **kwargs)
        self.fields['email'].disabled = True
