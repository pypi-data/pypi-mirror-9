from django.core.exceptions import ImproperlyConfigured

__version__ = '0.2.13'

try:
    # This is in a try-except block to prevent import errors at install time
    from .views import (SessionMultipleFormWizardView, CookieMultipleFormWizardView,
                        NamedUrlSessionMultipleFormWizardView, NamedUrlCookieMultipleFormWizardView,
                        MultipleFormWizardView, NamedUrlMultipleFormWizardView)
except (ImportError, ImproperlyConfigured):
    pass
