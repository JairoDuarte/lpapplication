from django import forms
from django.utils import timezone
from django.forms import widgets
from django.db.models import Q
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
    type_diplome = forms.CharField(required=False, widget=CustomModelSelect(models.TypeDiplome, True))
    filiere_diplome = forms.CharField(required=False, widget=widgets.Select())
    option_diplome = forms.CharField(required=False, widget=widgets.Select())
    type_bac = forms.CharField(required=False, widget=CustomModelSelect(models.TypeBac, True))
    filiere_choisie = forms.CharField(required=False, widget=widgets.Select())
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
        self.fields['mention_bac'].widget = CustomModelSelect(models.MentionBac, False)
        if self.instance:
            instance = self.instance
            if instance.type_diplome:
                self.fields['type_diplome'].initial = instance.type_diplome.pk
                if instance.filiere_diplome:
                    self.fields['filiere_diplome'].initial = instance.filiere_diplome.pk
                    if instance.option_diplome:
                        self.fields['option_diplome'].initial = instance.option_diplome.pk
            else:
                self.fields['type_diplome'].initial = '-1'
            if instance.type_bac:
                self.fields['type_bac'].initial = instance.type_bac.pk
            else:
                self.fields['type_diplome'].initial = '-1'
            if instance.filiere_choisie:
                self.fields['filiere_choisie'].initial = instance.filiere_choisie.pk
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
            'type_diplome': form_type_diplome or '',
            'filiere_diplome': form_filiere_diplome or '',
            'option_diplome': form_option_diplome or '',
            'filiere_choisie': form_filiere_choisie or '',
        }
    def __verifier_pays(self, pays):
        liste_pays = [pays_id for pays_id, pays_nom in Countries.LIST]
        if pays and (pays not in liste_pays):
            raise forms.ValidationError('Valeur invalide')
        return pays
    def __verifier_note(self, note):
        if note and note > Decimal('20.00'):
            raise forms.ValidationError('La note doit être inférieure à 20.00')
        if note and note < Decimal('0.00'):
            raise forms.ValidationError('La note doit être supérieure à 0.00')
        return note
    def __verifier_annee_a1(self, annee):
        settings = lp_settings()
        current_year = timezone.now().year
        try:
            annee = int(annee)
            if annee > current_year:
                raise True
            elif annee < current_year - settings.age_bac_max + 3:
                raise True
        except:
            raise forms.ValidationError('Valeur invalide')
        return annee
    def __verifier_annee_a2(self, annee):
        settings = lp_settings()
        current_year = timezone.now().year
        try:
            annee = int(annee)
            if annee > current_year:
                raise True
            elif annee < current_year - settings.age_bac_max + 4:
                raise True
        except:
            raise forms.ValidationError('Valeur invalide')
        return annee
    def clean_nationalite(self):
        return self.__verifier_pays(self.cleaned_data.get('nationalite'))
    def clean_pays_naissance(self):
        return self.__verifier_pays(self.cleaned_data.get('pays_naissance'))
    def clean_pays_residence(self):
        return self.__verifier_pays(self.cleaned_data.get('pays_residence'))
    def clean_note_s1(self):
        return self.__verifier_note(self.cleaned_data.get('note_s1'))
    def clean_note_s2(self):
        return self.__verifier_note(self.cleaned_data.get('note_s2'))
    def clean_note_s3(self):
        return self.__verifier_note(self.cleaned_data.get('note_s3'))
    def clean_note_s4(self):
        return self.__verifier_note(self.cleaned_data.get('note_s4'))
    def clean_note_a1(self):
        return self.__verifier_note(self.cleaned_data.get('note_a1'))
    def clean_note_a2(self):
        return self.__verifier_note(self.cleaned_data.get('note_a2'))
    def clean_annee_s1(self):
        return self.__verifier_annee_a1(self.cleaned_data.get('annee_s1'))
    def clean_annee_s2(self):
        return self.__verifier_annee_a1(self.cleaned_data.get('annee_s2'))
    def clean_annee_s3(self):
        return self.__verifier_annee_a2(self.cleaned_data.get('annee_s3'))
    def clean_annee_s4(self):
        return self.__verifier_annee_a2(self.cleaned_data.get('annee_s4'))
    def clean_type_diplome(self):
        id_type_diplome = self.cleaned_data.get('type_diplome')
        try:
            if id_type_diplome != '-1':
                models.TypeDiplome.objects.get(pk=id_type_diplome)
        except models.TypeDiplome.DoesNotExist:
            raise forms.ValidationError('Valeur invalide')
        return id_type_diplome
    def clean_type_bac(self):
        id_type_bac = self.cleaned_data.get('type_bac')
        try:
            if id_type_bac != '-1':
                models.TypeBac.objects.get(pk=id_type_bac)
        except:
            raise forms.ValidationError('Valeur invalide')
        return id_type_bac
    def clean_annee_bac(self):
        annee_bac = self.cleaned_data.get('annee_bac')
        settings = lp_settings()
        current_year = timezone.now().year
        try:
            annee = int(annee_bac)
            if annee > current_year - 2:
                raise True
            elif annee < current_year - settings.age_bac_max + 2:
                raise True
        except:
            raise forms.ValidationError('Valeur invalide')
        return annee_bac
    def clean(self):
        cleaned_data = super(CandidatForm, self).clean()
        # Type diplome autre
        id_type_diplome = cleaned_data.get('type_diplome')
        type_diplome_autre = cleaned_data.get('type_diplome_autre')
        if id_type_diplome == '-1':
            if type_diplome_autre == '':
                self.add_error('type_diplome_autre', 'Champ obligatoire')
        else:
            cleaned_data['type_diplome_autre'] = ''
        # Filière diplôme
        id_filiere_diplome = self.cleaned_data.get('filiere_diplome')
        if id_type_diplome == '-1':
            cleaned_data['filiere_diplome'] = ''
        elif id_filiere_diplome != '':  # and id_filiere_diplome != '-1':
            try:
                models.FiliereDiplome.objects.get(type_diplome__pk=id_type_diplome, pk=id_filiere_diplome)
            except:
                self.add_error('filiere_diplome', 'Valeur invalide')
        # Option diplôme
        id_option_diplome = self.cleaned_data.get('option_diplome')
        if id_type_diplome == '-1':
            cleaned_data['option_diplome'] = ''
        # elif id_filiere_diplome == '-1':
        #     cleaned_data['option_diplome'] = ''
        elif id_option_diplome != '':
            try:
                models.OptionDiplome.objects.get(filiere_diplome__pk=id_filiere_diplome, pk=id_option_diplome)
            except:
                self.add_error('option_diplome', 'Valeur invalide')
        # Type bac autre
        id_type_bac = cleaned_data.get('type_bac')
        type_bac_autre = cleaned_data.get('type_bac_autre')
        if id_type_bac == '-1':
            if type_bac_autre == '':
                self.add_error('type_bac_autre', 'Champ obligatoire')
        else:
            cleaned_data['type_bac_autre'] = ''
        # Filière choisie
        id_filiere_choisie = self.cleaned_data.get('filiere_choisie')
        try:
            if id_type_diplome != '-1':
                q = Q(types_diplome__pk=id_type_diplome)
                if id_filiere_diplome != '':
                    q = q | Q(filieres_diplome__pk=id_filiere_diplome)
                    if id_option_diplome != '':
                        q = q | Q(options_diplome__pk=id_option_diplome)
                print('TYPE' + str(Q(pk=id_filiere_choisie) & q))
                models.Filiere.objects.filter(pk=id_filiere_choisie).get(q)
            else:
                models.Filiere.objects.get(pk=id_filiere_choisie)
        except models.Filiere.DoesNotExist:
            self.add_error('filiere_choisie', 'Valeur invalide')
        # On retourne les données de nouveau
        return cleaned_data
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
        # Ajout de type de diplome
        id_type_diplome = self.cleaned_data.get('type_diplome')
        candidat.type_diplome = None if id_type_diplome in ['', '-1'] else models.TypeDiplome.objects.get(pk=id_type_diplome)
        # Ajout de filière de diplome
        id_filiere_diplome = self.cleaned_data.get('filiere_diplome')
        candidat.filiere_diplome = None if id_filiere_diplome == '' else models.FiliereDiplome.objects.get(pk=id_filiere_diplome)
        # Ajout d'option de diplome
        id_option_diplome = self.cleaned_data.get('option_diplome')
        candidat.option_diplome = None if id_option_diplome == '' else models.OptionDiplome.objects.get(pk=id_option_diplome)
        # Ajout de type de bac
        id_type_bac = self.cleaned_data.get('type_bac')
        candidat.type_bac = None if id_type_bac in ['', '-1'] else models.TypeBac.objects.get(pk=id_type_bac)
        # Calculer la note de préselection
        candidat.note_preselection = \
            Decimal('0.25') * candidat.note_a1 + \
            Decimal('0.25') * candidat.note_a2 + \
            Decimal('0.15') * candidat.mention_bac.note_preselection + \
            Decimal('0.15') * candidat.note_age() + \
            Decimal('0.20') * candidat.note_validation()
        if commit:
            candidat.save()
        return candidat
    class Meta:
        model = models.Candidat
        exclude = ['user', 'jeton_validation', 'note_preselection', 'type_diplome', 'type_bac', 'filiere_diplome', 'option_diplome', 'filiere_choisie']
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
