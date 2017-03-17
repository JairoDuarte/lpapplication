from django import forms
from django.utils import timezone
from .models import Settings, Candidat
from .utils import Countries, lp_settings
from .widgets import DateSelectorWidget, SchoolYearWidget

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
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

class CandidatForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Init parent
        super(CandidatForm, self).__init__(*args, **kwargs)
        # prepare data
        settings = lp_settings()
        current_year = timezone.now().year
        birthdate_widget = DateSelectorWidget(current_year - settings.age_max, current_year - 10)
        min_annee_diplome = current_year - settings.age_bac_max + 2
        min_annee_bac = current_year - settings.age_bac_max
        # Make default inputs
        countries_input = forms.Select(choices=Countries.LIST)
        mark_input = forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '20'})
        # Set default inputs
        self.fields['nationalite'].widget = countries_input
        self.fields['date_naissance'].widget = birthdate_widget
        self.fields['pays_naissance'].widget = countries_input
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
    class Meta:
        model = Candidat
        exclude = ['user', 'jeton_validation']
