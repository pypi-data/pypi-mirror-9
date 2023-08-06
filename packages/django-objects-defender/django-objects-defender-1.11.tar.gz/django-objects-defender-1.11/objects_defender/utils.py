from django.conf import settings
from django.contrib import messages
from django.db.models.loading import get_model
from operator import or_
from django.db.models import Q


defended_models = {}
for model, params in settings.DEFENDED_OBJECTS.iteritems():
    defended_models[get_model(model)] = params


def get_filters(klass):
    return [Q(**{fld: val}) for optns in defended_models[klass] for fld, values in optns.iteritems() for val in values]


def get_defended_fields(klass, exclude=('id',)):
    defended_fields = []
    for field in (field for optns in defended_models[klass] for field, values in optns.iteritems()):
        if field not in exclude:
            defended_fields.append(field.split('__')[0] if '__' in field else field)
    return tuple(set(defended_fields))


def is_deletable(instance):
    sender = instance.__class__
    return instance not in sender.objects.filter(reduce(or_, get_filters(sender)))


def add_methods(klass):
    def has_delete_permission(self, request, obj=None):
        if obj:
            return is_deletable(obj)
        return super(klass, self).has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(klass, self).get_readonly_fields(request, obj)
        if obj and not is_deletable(obj):
            return readonly_fields + get_defended_fields(obj.__class__)
        return readonly_fields

    def get_prepopulated_fields(self, request, obj=None):
        prepopulated_fields = super(klass, self).get_prepopulated_fields(request, obj)
        if obj and not is_deletable(obj):
            prepopulated_fields = prepopulated_fields.copy()
            for field in get_defended_fields(obj.__class__):
                if field in prepopulated_fields:
                    del prepopulated_fields[field]
        return prepopulated_fields

    def save_form(self, request, form, change):
        obj_new = super(klass, self).save_form(request, form, change)
        obj_old = form.cleaned_data.get('id')
        if obj_old and obj_old.__class__ in defended_models and not is_deletable(obj_old):
            for field in get_defended_fields(obj_old.__class__):
                setattr(obj_new, field, getattr(obj_old, field))
                messages.add_message(request, messages.DEFAULT_LEVELS['WARNING'],
                                     "Field '{field}' couldn't be edit".format(field=field))
        return obj_new

    klass.has_delete_permission = has_delete_permission
    klass.get_readonly_fields = get_readonly_fields
    klass.get_prepopulated_fields = get_prepopulated_fields
    klass.save_form = save_form