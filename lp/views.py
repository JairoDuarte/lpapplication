from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .forms import SettingsForm
from .util import lp_settings

def index(request):
    return render(request, 'lp/index.html', {})

def login(request):
    return render(request, 'lp/login.html', {})

def apply(request):
    return render(request, 'lp/apply.html', {})

def admin_settings(request):
    user = request.user
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
            return HttpResponseRedirect(reverse('admin_settings'))
    else:
        settings = lp_settings()
        form = SettingsForm(instance=settings)
    return render(request, 'admin/settings.html', {
        'has_permission': user.is_admin,
        'user': user,
        'form': form
    })
