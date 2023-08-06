from django.forms import forms
from django.conf import settings
from django.utils.safestring import mark_safe


class WYSIWYGFullEditor(forms.Textarea):
    class Media:
        js = (
            '//cdn.ckeditor.com/4.4.7/full/ckeditor.js',
        )
        #<script src="//cdn.ckeditor.com/4.4.7/standard/ckeditor.js"></script>
    def render(self, name, value, attrs=None):
        rendered = super(self.__class__, self).render(name, value, attrs)
        return mark_safe('<div style="clear: both; margin-bottom: 2px;"/></div>') + rendered + \
               mark_safe("""<script type="text/javascript">(function($) { CKEDITOR.replace('id_""" + name + """'); })(django.jQuery);</script>""")


class WYSIWYGStandardEditor(forms.Textarea):
    class Media:
        js = (
            '//cdn.ckeditor.com/4.4.7/standard/ckeditor.js',
        )
        #<script src="//cdn.ckeditor.com/4.4.7/standard/ckeditor.js"></script>
    def render(self, name, value, attrs=None):
        rendered = super(self.__class__, self).render(name, value, attrs)
        return mark_safe('<div style="clear: both; margin-bottom: 2px;"/></div>') + rendered + \
               mark_safe("""<script type="text/javascript">(function($) { CKEDITOR.replace('id_""" + name + """'); })(django.jQuery);</script>""")

