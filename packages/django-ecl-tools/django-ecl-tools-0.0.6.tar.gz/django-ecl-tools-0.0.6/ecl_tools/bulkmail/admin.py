from django import http
from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from .models import List, Subscription, Optin, TrackingEvent


class SubscribedFilter(SimpleListFilter):
    title = 'Subscribed'
    parameter_name = 'subscribed'

    def lookups(self, request, model_admin):
        return (
            ('subs', 'Subscribed'),
            ('unsubs', 'Unsubscribed'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'subs':
            return queryset.filter(unsubscribed__isnull=True)

        elif self.value() == 'unsubs':
            return queryset.filter(unsubscribed__isnull=False)


class OptinAdmin(admin.ModelAdmin):
    list_display = ('email', 'signup_location', 'created')
    list_filter = ('signup_location',)
    date_hierarchy = 'created'
    search_fields = ('email',)


class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'reply_to', 'short_description', 'frequency', 'sorder', 'Subscribed')
    list_editable = ('sorder',)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser:
            return super(ListAdmin, self).change_view(request, object_id, form_url=form_url,
                                                      extra_context=extra_context)

        return http.HttpResponseForbidden('Access Denied', content_type="text/plain")


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
    'email', 'bulk_list', 'signup_location', 'is_clean', 'unsubscribed', 'reason', 'created') #, 'email_status'
    list_filter = (
    SubscribedFilter, 'bulk_list', 'is_clean', 'unsubscribed', 'reason', 'signup_location', 'created') #, 'email_status'
    date_hierarchy = 'created'
    search_fields = ('email',)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser:
            return super(SubscriptionAdmin, self).change_view(request, object_id, form_url=form_url,
                                                              extra_context=extra_context)

        return http.HttpResponseForbidden('Access Denied', content_type="text/plain")


class TrackingEventAdmin(admin.ModelAdmin):
    list_display = (
        'subscription',
        'campaign',
        'event',
        'client_os',
        'client_name',
        'client_type',
        'device_type',
        'user_agent',
        'city',
        'region',
        'country',
        'ip',
        'time',
    )
    list_filter = ('event', 'client_os', 'client_name', 'client_type', 'city', 'region', 'country')
    search_fields = ('subscription__email','campaign','user_agent','ip')

admin.site.register(List, ListAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Optin, OptinAdmin)
admin.site.register(TrackingEvent, TrackingEventAdmin)