from operator import or_
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.actions import delete_selected
from .utils import defended_models, get_filters, add_methods


def defended_delete_selected(modeladmin, request, queryset):
    model = queryset.model
    if model in defended_models:
        queryset = queryset.exclude(reduce(or_, get_filters(model)))
        if not queryset.exists():
            messages.add_message(request, messages.DEFAULT_LEVELS['WARNING'], "This object couldn't be deleted")
            return None
    return delete_selected(modeladmin, request, queryset)
defended_delete_selected.short_description = delete_selected.short_description
admin.site._actions['delete_selected'] = defended_delete_selected

for model in admin.site._registry:
    if model in defended_models:
        ModelAdmin = admin.site._registry[model].__class__
        DefendedAdmin = type(str(model.__class__) + 'DefendedAdmin', (ModelAdmin,), {})
        add_methods(DefendedAdmin)

        admin.site.unregister(model)
        admin.site.register(model, DefendedAdmin)
