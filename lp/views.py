from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .forms import SettingsForm, CandidatForm
from .utils import lp_settings
from . import models

def index(request):
    return render(request, 'lp/index.html', {})

def login(request):
    return render(request, 'lp/login.html', {})

def apply(request):
    # Traiter le formulaire
    if request.method == 'POST':
        form = CandidatForm(request.POST)
        if form.is_valid():
            # Success, we save candidate
            form.save()
            # Then redirect to confirmation notice
            # TODO: Make an actual confirmation notice
            return HttpResponseRedirect(reverse('lp:index'))
        form_type_diplome = request.POST['type_diplome']
        form_filiere_diplome = request.POST['filiere_diplome']
        form_option_diplome = request.POST['option_diplome']
    else:
        form = CandidatForm()
    # Préparer la liste des types de diplome, filière, option
    # TODO: names need quote escaping
    types_diplome = []
    for type_diplome in models.TypeDiplome.objects.all():
        filieres_diplome = []
        for filiere_diplome in type_diplome.filierediplome_set.all():
            options_diplome = []
            for option_diplome in filiere_diplome.optiondiplome_set.all():
                options_diplome.append('"%i":"%s"' % (option_diplome.pk, option_diplome.libelle))
            filieres_diplome.append('"%i": {"label": "%s", "options": {%s}}' % (filiere_diplome.pk, filiere_diplome.libelle, ','.join(options_diplome)))
        types_diplome.append('"%i": {"label": "%s", "filieres": {%s}}' % (type_diplome.pk, type_diplome.libelle, ','.join(filieres_diplome)))
    filieres_json = '{%s}' % ','.join(types_diplome)
    # Afficher
    return render(request, 'lp/apply.html', {
        'form': form,
        'filieres_json': filieres_json,
        'type_diplome': type_diplome,
        'filiere_diplome': filiere_diplome,
        'option_diplome': option_diplome
    })

def admin_settings(request):
    user = request.user
    # Check if staff user is logged
    if not user.is_staff:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(
            request.get_full_path(),
            reverse('admin:login', current_app='lp')
        )
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            # Success, we save
            settings = form.save(commit=False)
            settings.id = 1
            settings.save()
            form.save_m2m()
            # Show a success message
            messages.success(request, 'Paramètres enregistrés avec succès.')
            # Then redirect to same page...
            return HttpResponseRedirect(reverse('lp:admin_settings'))
    else:
        settings = lp_settings()
        form = SettingsForm(instance=settings)
    return render(request, 'admin/settings.html', {
        'has_permission': user.is_admin,
        'user': user,
        'form': form
    })
