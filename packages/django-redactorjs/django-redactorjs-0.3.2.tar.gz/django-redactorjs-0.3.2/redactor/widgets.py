import json
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.conf import settings


GLOBAL_OPTIONS = getattr(settings, 'REDACTOR_OPTIONS', {})
REDACTOR_CSS = getattr(settings, 'REDACTOR_CSS', {})
REDACTOR_JS = getattr(settings, 'REDACTOR_JS', [])

INIT_JS = """<script type="text/javascript">
    (function($){
        $("#%s").redactor(%s);
    })(jQuery || django.jQuery);
    </script>
    """


class RedactorEditor(widgets.Textarea):

    class Media:
        js = REDACTOR_JS
        css = REDACTOR_CSS

    def __init__(self, *args, **kwargs):
        self.upload_to = kwargs.pop('upload_to', '')
        self.custom_options = kwargs.pop('redactor_options', {})
        self.Media.css['all'] = self.Media.css['all'] + ('redactor/css/django_admin.css',)
        super(RedactorEditor, self).__init__(*args, **kwargs)

    def get_options(self):
        options = GLOBAL_OPTIONS.copy()
        options.update(self.custom_options)
        options.update({
            'imageUpload': reverse('redactor_upload_image', kwargs={'upload_to': self.upload_to}),
            'fileUpload': reverse('redactor_upload_file', kwargs={'upload_to': self.upload_to})
        })
        return json.dumps(options)

    def render(self, name, value, attrs=None):
        html = super(RedactorEditor, self).render(name, value, attrs)
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id')
        html += INIT_JS % (id_, self.get_options())
        return mark_safe(html)
