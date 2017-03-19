from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.forms.models import model_to_dict
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
            # Succès, on enregistre le candidat dans la session
            request.session['candidat'] = request.POST
            # Et on redirige vers la page de confirmation
            return HttpResponseRedirect(reverse('lp:confirm'))
    else:
        # Si jamais on vient de la page de confirmation
        # Il faudra récupérer les données envoyés
        if 'candidat' in request.session:
            form = CandidatForm(request.session['candidat'])
            del request.session['candidat']
        else:
            form = CandidatForm()
    # Préparer le contexte
    session_expired_error = None
    if 'session_expired_error' in request.session:
        session_expired_error = 'Votre session a expirée'
        del request.session['session_expired_error']
    context = form.context_data()
    context.update({
        'form': form,
        'session_expired_error': session_expired_error
    })
    # Afficher
    return render(request, 'lp/apply.html', context)

def confirm(request):
    # On essaye de récupérer le candidat de la session
    if 'candidat' not in request.session:
        request.session['session_expired_error'] = True
        return HttpResponseRedirect(reverse('lp:apply'))
    candidat = request.session['candidat']
    candidat_form = CandidatForm(candidat)
    candidat_instance = candidat_form.save(commit=False)
    if request.method == 'POST':
        # On supprime le candidat de la session
        del request.session['candidat']
        # On recupère le candidat de la session et l'on enregistre dans la BDD
        candidat_instance.save()
        # On genere les données de confirmation email et on en envoit un
        # TODO: confirmation d'email
        # Puis on redirige vers la page de confirmation d'email
        return HttpResponseRedirect(reverse('lp:confirm_email'))
    # On affiche la page
    return render(request, 'lp/confirm.html', {
        'candidat': candidat_instance
    })

def confirm_email(request):
    return render(request, 'lp/confirm_email.html', {})

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
