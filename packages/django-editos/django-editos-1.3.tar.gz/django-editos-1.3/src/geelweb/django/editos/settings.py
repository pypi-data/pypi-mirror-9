from django.conf import settings

EDITOS_THEMES = getattr(settings, 'EDITOS_THEMES', (
    ('light', 'Light'),
    ('dark', 'Dark'),
))

EDITOS_DEFAULT_THEME = getattr(settings, 'EDITOS_DEFAULT_THEME', 'light')

EDITOS_HELP_TEXTS = getattr(settings, 'EDITOS_HELP_TEXTS', {})
