from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from .models import AUPhoneNumberField


class ExtraFieldsAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, request=None, **kwargs):
        if isinstance(db_field, AUPhoneNumberField):
            return db_field.formfield(**kwargs)

        return super(ExtraFieldsAdmin, self).formfield_for_dbfield(
            db_field, request=request, **kwargs)
