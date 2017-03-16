from .models import Settings

def lp_settings():
    settingsSet = Settings.objects.filter(id=1)
    if len(settingsSet) == 0:
        settings = Settings(id=1)
        settings.save()
        return settings
    else:
        return settingsSet[0]
