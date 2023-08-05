=====================
django_localflavor_au
=====================

Country-specific Django helpers for Australia.

What's in the Australia localflavor?
====================================

* forms.AUPostCodeField: A form field that validates input as an Australian
  postcode.

* forms.AUPhoneNumberField: A form field that validates input as an Australian
  phone number. Valid numbers have ten digits.

* forms.AUStateSelect: A ``Select`` widget that uses a list of Australian
  states/territories as its choices.

* models.AUPhoneNumberField: A model field that checks that the value is a
  valid Australian phone number (ten digits).

* models.AUStateField: A model field that forms represent as a
  ``forms.AUStateField`` field and stores the three-letter Australian state
  abbreviation in the database.

* models.AUPostCodeField: A model field that forms represent as a
  ``forms.AUPostCodeField`` field and stores the four-digit Australian postcode
  in the database.

See the source code for full details.

About localflavors
==================

Django's "localflavor" packages offer additional functionality for particular
countries or cultures.

For example, these might include form fields for your country's postal codes,
phone number formats or government ID numbers.

This code used to live in Django proper -- in django.contrib.localflavor -- but
was separated into standalone packages in Django 1.5 to keep the framework's
core clean.

For a full list of available localflavors, see https://github.com/django/
