#-*- coding: utf-8 -*-
from django.conf import settings
from django.core import exceptions
from django.db.models import get_model
from models.userprofile import UserProfile


def get_userprofile_model():

    model = UserProfile

    if settings.DJINN_USERPROFILE_MODEL:

        try:
            parts = settings.DJINN_USERPROFILE_MODEL.split('.')
            model = get_model(parts[0], parts[-1])
        except:

            raise exceptions.ImproperlyConfigured(
                'Erroneous userprofile model'
            )

        return model
