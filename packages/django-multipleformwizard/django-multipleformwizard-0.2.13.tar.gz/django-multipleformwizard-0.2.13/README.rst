=============================
django-multipleformwizard
=============================

.. image:: https://badge.fury.io/py/django-multipleformwizard.svg
    :target: https://badge.fury.io/py/django-multipleformwizard

.. image:: https://travis-ci.org/vikingco/django-multipleformwizard.svg?branch=master
    :target: https://travis-ci.org/vikingco/django-multipleformwizard

.. image:: https://coveralls.io/repos/vikingco/django-multipleformwizard/badge.svg?branch=master
    :target: https://coveralls.io/r/vikingco/django-multipleformwizard?branch=master

.. image:: https://readthedocs.org/projects/django-multipleformwizard/badge/
    :target: https://django-multipleformwizard.readthedocs.org

An extension to the official Django form wizard supporting multiple forms on a wizard step.

Documentation
-------------

The full documentation is at https://django-multipleformwizard.readthedocs.org.

Quickstart
----------

Install django-multipleformwizard::

    pip install django-multipleformwizard

Then use it in a project::

    # Every *WizardView that can be imported is an equivalent of a builtin *WizardView in Django
    from multipleformwizard import (SessionMultipleFormWizardView, CookieMultipleFormWizardView,
                                    NamedUrlSessionMultipleFormWizardView, NamedUrlCookieMultipleFormWizardView,
                                    MultipleFormWizardView, NamedUrlMultipleFormWizardView)

Example use
-----------

.. code-block:: python

    from __future__ import unicode_literals

    from django import forms
    from django.shortcuts import render_to_response

    from multipleformwizard import SessionMultipleFormWizardView

    from .forms import Form1, Form2, Form3

    class Wizard(SessionMultipleFormWizardView):
        form_list = [
            ("start", Form1),
            ("user_info", (
                ('account', Form2),
                ('address', Form3)
            )
        ]

        templates = {
            "start": 'demo/wizard-start.html',
            "user_info": 'demo/wizard-user_info.html'
        }

        def get_template_names(self):
            return [self.templates[self.steps.current]]

        def done(self, form_dict, **kwargs):
            result = {}

            for key in form_dict:
                form_collection = form_dict[key]
                if isinstance(form_collection, forms.Form):
                    result[key] = form_collection.cleaned_data
                elif isinstance(form_collection, dict):
                    result[key] = {}
                    for subkey in form_collection:
                        result[key][subkey] = form_collection[subkey].cleaned_data

            return render_to_response('demo/wizard-end.html', {
                'form_data': result,
            })
