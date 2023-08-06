from django.conf import settings
from django.db.models.loading import get_model
from operator import or_
from django.db.models import Q


def get_registered_models():
    registered_models = {}
    for model, params in settings.DEFENDED_OBJECTS:
        registered_models[get_model(model)] = params
    return registered_models


def is_deletable(instance):
    sender = instance.__class__
    register = get_registered_models()
    return instance not in sender.objects.filter(
        reduce(or_, [Q(**params) for params in register[sender]])
    )
