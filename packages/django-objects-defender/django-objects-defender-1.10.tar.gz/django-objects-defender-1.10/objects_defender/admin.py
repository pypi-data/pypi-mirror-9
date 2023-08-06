from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.actions import delete_selected
from .utils import get_registered_models, is_deletable

registered_models = get_registered_models()


def defended_delete_selected(modeladmin, request, queryset):
    model = queryset.model
    if model in registered_models:
        queryset = queryset.exclude(**registered_models[model])
        if not queryset.exists():
            messages.add_message(request,
                                 messages.DEFAULT_LEVELS['WARNING'],
                                 "This object couldn't be deleted")
            return None
    return delete_selected(modeladmin, request, queryset)
defended_delete_selected.short_description = delete_selected.short_description
admin.site._actions['delete_selected'] = defended_delete_selected

for model in admin.site._registry:
    if model in registered_models:
        ModelAdmin = admin.site._registry[model].__class__

        class DefendedAdmin(ModelAdmin):
            def has_delete_permission(self, request, obj=None):
                if obj:
                    return is_deletable(obj)
                return super(DefendedAdmin, self).has_delete_permission(request, obj)

        admin.site.unregister(model)
        admin.site.register(model, DefendedAdmin)
