from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .forms import SettingsForm, CandidatForm
from .utils import lp_settings

def index(request):
    return render(request, 'lp/index.html', {})

def login(request):
    return render(request, 'lp/login.html', {})

def apply(request):
    if request.method == 'POST':
        form = CandidatForm(request.POST)
        if form.is_valid():
            # Success, we save candidate
            candidate = form.save()
            # Then redirect to confirmation notice
            # TODO: Make an actual confirmation notice
            return HttpResponseRedirect(reverse('lp:index'))
    else:
        form = CandidatForm()
    return render(request, 'lp/apply.html', {
        'form': form
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
