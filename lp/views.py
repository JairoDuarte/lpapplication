import random
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.core.mail import send_mail
from django.template import loader

from .forms import SettingsForm, CandidatForm, CandidatChangeForm, PasswordForm
from .utils import lp_settings, filter_login
from . import models

def send_confirmation_email(email, token, request):
    email_confirm_url = request.build_absolute_uri(reverse('lp:confirm_email') + '?token=' + token)
    corps_email = loader.get_template('lp/email_confirm_body.html').render({
        'confirm_url': email_confirm_url
    }, request)
    sujet_email = loader.get_template('lp/email_confirm_subject.html').render({}, request)
    send_mail(sujet_email, corps_email, 'test@gmail.com', [email])

def index(request):
    # On redirige l'utilsateur si déjà connecté
    response = filter_login(request)
    if response:
        return response
    return render(request, 'lp/index.html', {})

def apply(request):
    # On redirige l'utilsateur si déjà connecté
    response = filter_login(request)
    if response:
        return response
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
    context = form.context_data()
    context.update({
        'form': form
    })
    # Afficher
    return render(request, 'lp/apply.html', context)

def confirm(request):
    # On redirige l'utilsateur si déjà connecté
    response = filter_login(request)
    if response:
        return response
    # On essaye de récupérer le candidat de la session
    if 'candidat' not in request.session:
        messages.error(request, 'Votre session a expirée.')
        return HttpResponseRedirect(reverse('lp:apply'))
    candidat = request.session['candidat']
    candidat_form = CandidatForm(candidat)
    candidat_instance = candidat_form.save(commit=False)
    if request.method == 'POST':
        # On supprime le candidat de la session
        del request.session['candidat']
        # On genere les données de confirmation email et on en envoit un
        allowed_chars = '23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
        token_length = 32
        # Continuer à générer un nouveau jeton jusqu'à ce qu'on en trouve un unique
        confirmation_token = ''.join(random.choice(allowed_chars) for _ in range(token_length))
        while len(models.Candidat.objects.filter(jeton_validation=confirmation_token)):
            confirmation_token = ''.join(random.choice(allowed_chars) for _ in range(token_length))
        candidat_instance.jeton_validation = confirmation_token
        # On enregistre le candidat dans la bdd
        candidat_instance.save()
        # On envoie l'email
        send_confirmation_email(candidat_instance.email, confirmation_token, request)
        # On affiche un message comme quoi on doit vérifier son email
        messages.info(request, "Veuillez vérifier votre boîte email pour confirmer votre adresse email.")
        # Puis on redirige vers la page de confirmation d'email
        return HttpResponseRedirect(reverse('lp:login'))
    # On affiche la page
    return render(request, 'lp/confirm.html', {
        'candidat': candidat_instance
    })
def confirm_email(request):
    # On redirige l'utilsateur si déjà connecté
    response = filter_login(request)
    if response:
        return response
    # On vérifie le jeton de validation donné comme paramètre
    if 'token' in request.GET:
        token = request.GET['token']
        candidat_set = models.Candidat.objects.filter(jeton_validation=token)
        if len(candidat_set) > 0:
            # On envoit vers la page de création d'utilisateur
            candidat = candidat_set[0]
            request.session['email_confirme_candidat'] = candidat.pk
            messages.info(request, 'Email confirmé avec succès')
            return HttpResponseRedirect(reverse('lp:set_password'))
    else:
        messages.error(request, 'Lien de validation invalide.')
        return HttpResponseRedirect(reverse('lp:index'))

def set_password(request):
    # On redirige l'utilsateur si déjà connecté
    response = filter_login(request)
    if response:
        return response
    # On redirige l'utilisateur si pas en mode de creation d'utilisateur
    if 'email_confirme_candidat' not in request.session:
        return HttpResponseRedirect(reverse('lp:index'))
    candidat_set = models.Candidat.objects.filter(pk=request.session['email_confirme_candidat'])
    if len(candidat_set) == 0:
        messages.error(request, 'Une erreur est survenue')
        return HttpResponseRedirect(reverse('lp:index'))
    candidat = candidat_set[0]
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            # On crée l'utilisateur et on l'ajoute au candidat
            user = models.User(email=candidat.email)
            user.set_password(form.cleaned_data['password_confirm'])
            user.save()
            candidat.user = user
            candidat.jeton_validation = None
            candidat.save()
            # On supprime les données de session
            del request.session['email_confirme_candidat']
            # On redirige vers la page de connexion
            messages.info(request, 'Mot de passe enregistré avec succès')
            return HttpResponseRedirect(reverse('lp:login'))
    else:
        form = PasswordForm(initial={'email': candidat.email})
    # On affiche
    return render(request, 'lp/set_password.html', {'form': form})

def panel(request):
    user = request.user
    # On redirige l'utilsateur si pas un candidat
    if user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    elif user.is_anonymous:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(
            request.get_full_path(),
            reverse('lp:login', current_app='lp')
        )
    # On récupère l'objet candidat
    candidat = user.candidat
    # On crée le formulaire
    if request.method == 'POST':
        form = CandidatChangeForm(request.POST, instance=candidat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Données enregistrées avec succès')
    else:
        form = CandidatChangeForm(instance=candidat)
    context = form.context_data()
    context.update(form=form)
    # On affiche
    return render(request, 'lp/panel.html', context)

def logout(request):
    auth_views.logout(request)
    messages.info(request, 'Déconnecté avec succès')
    return HttpResponseRedirect(reverse('lp:index'))

def password_change_done(request):
    auth_views.password_change_done(request)
    messages.info(request, 'Mot de passe modifié avec succès')
    return HttpResponseRedirect(reverse('lp:panel'))

def password_reset_confirm(request, uidb64, token):
    return auth_views.password_reset_confirm(request, token=token, uidb64=uidb64, template_name='lp/password_reset_confirm.html')

def password_reset_done(request):
    auth_views.password_reset_done(request)
    return render(request, 'lp/password_reset_done.html', {})

def password_reset_complete(request):
    auth_views.password_reset_complete(request)
    messages.info(request, 'Mot de passe modifié avec succès')
    return HttpResponseRedirect(reverse('lp:login'))

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
