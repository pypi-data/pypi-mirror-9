from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class NullDateFieldFilter(admin.SimpleListFilter):
    title = None
    parameter_name = None

    def lookups(self, request, model_admin):
        return (
            ('True', _('Yes')),
            ('False', _('No')),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(**{self.parameter_name+'__isnull': self.value()!='True'})