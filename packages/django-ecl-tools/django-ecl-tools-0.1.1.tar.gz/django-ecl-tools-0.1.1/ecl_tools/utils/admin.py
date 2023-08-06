from django.contrib import admin
from django.contrib.admin.widgets import ManyToManyRawIdWidget, ForeignKeyRawIdWidget
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.encoding import smart_unicode
from django.contrib.admin.sites import site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ecl_tools.utils import widgets


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


class VerboseForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    def __init__(self, rel, admin_site, attrs=None, using=None, extra_url_parameters=None):
        self.extra_url_parameters = extra_url_parameters
        super(VerboseForeignKeyRawIdWidget, self).__init__(rel, admin_site, attrs, using)

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to._default_manager.using(self.db).get(**{key: value})
            change_url = reverse(
                "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.object_name.lower()),
                args=(obj.pk,)
            )
            return '&nbsp;<strong><a href="%s" target="_blank">%s</a></strong>' % (change_url, escape(obj))
        except (ValueError, self.rel.to.DoesNotExist):
            return '???'

    def url_parameters(self):
        """
        Allow extending of url_parameters; used to force certain filters for raw_id_fields.
        """
        params = super(VerboseForeignKeyRawIdWidget, self).url_parameters()
        if self.extra_url_parameters:
            params.update(self.extra_url_parameters)
        return params


class VerboseManyToManyRawIdWidget(ManyToManyRawIdWidget):
    def label_for_value(self, value):
        values = value.split(',')
        str_values = []
        key = self.rel.get_related_field().name
        for v in values:
            try:
                obj = self.rel.to._default_manager.using(self.db).get(**{key: v})
                x = smart_unicode(obj)
                change_url = reverse(
                    "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.module_name.lower()),
                    args=(obj.pk,)
                )
                str_values += ['<strong><a href="%s" target="_blank">%s</a></strong>' % (change_url, escape(x))]
            except self.rel.to.DoesNotExist:
                str_values += [u'???']
        return u', '.join(str_values)


class ImproveRawIdFieldsFormMixin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs.pop("request", None)
            type = db_field.rel.__class__.__name__
            extra = getattr(self, 'raw_id_fields_extra_url_parameters', None)
            if extra:
                try:
                    extra = extra[db_field.name]
                except KeyError:
                    extra = None
            if type == "ManyToOneRel":
                kwargs['widget'] = VerboseForeignKeyRawIdWidget(db_field.rel, site, extra_url_parameters=extra)
            elif type == "ManyToManyRel":
                kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel, site)
            return db_field.formfield(**kwargs)
        return super(ImproveRawIdFieldsFormMixin, self).formfield_for_dbfield(db_field, **kwargs)


class SaveAsNewAutoClearMixin(admin.ModelAdmin):
    save_as_clear_fields = False
    save_as_clear_fields_defaults = {'scheduled': None, 'publish': None, 'is_published': False, 'when_to_publish': None}

    def save_model(self, request, obj, form, change):
        if self.save_as_clear_fields:
            if '_saveasnew' in request.POST:
                # Allow the resetting of certain fields when the save_as button is used;
                #Useful for clearing publish fields and preventing accidental bulkmail sends
                for field, value in self.save_as_clear_fields_defaults.items():
                    try:
                        current = getattr(obj, field)
                        if current:
                            setattr(obj, field, value)
                    except AttributeError:
                        pass  #ignore if fields don't exist

        return super(SaveAsNewAutoClearMixin, self).save_model(request, obj, form, change)


class VerboseForeignKeyRawIdTabAdmin(admin.TabularInline):

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs.pop("request", None)
            type = db_field.rel.__class__.__name__
            if type == "ManyToOneRel":
                kwargs['widget'] = VerboseForeignKeyRawIdWidget(db_field.rel, site)
            elif type == "ManyToManyRel":
                kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel, site)
            return db_field.formfield(**kwargs)
        return super(VerboseForeignKeyRawIdTabAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class CommonTabAdmin(VerboseForeignKeyRawIdTabAdmin):

    formfield_overrides = {models.TextField: {'widget': widgets.WYSIWYGFullEditor()},}


class CommonAdmin(ImproveRawIdFieldsFormMixin):

    formfield_overrides = {models.TextField: {'widget': widgets.WYSIWYGFullEditor()},}
