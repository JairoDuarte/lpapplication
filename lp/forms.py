from django import forms
from .models import Settings, Candidat

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
    class Meta:
        model = Candidat
        exclude = ['user', 'jeton_validation']