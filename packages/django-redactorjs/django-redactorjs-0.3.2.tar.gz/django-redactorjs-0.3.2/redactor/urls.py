try:
    from django.conf.urls import url, patterns
except ImportError:
    from django.conf.urls.defaults import url, patterns

from redactor.views import redactor_upload
from redactor.forms import FileForm, ImageForm


urlpatterns = patterns('',
    url('^upload/image/(?P<upload_to>.*)', redactor_upload, {
        'form_class': ImageForm,
        'response': lambda name, url: '{"filelink": "%s"}' % url,
    }, name='redactor_upload_image'),

    url('^upload/file/(?P<upload_to>.*)', redactor_upload, {
        'form_class': FileForm,
        'response': lambda name, url: '{"filelink": "%s"}' % url,
    }, name='redactor_upload_file'),
)
