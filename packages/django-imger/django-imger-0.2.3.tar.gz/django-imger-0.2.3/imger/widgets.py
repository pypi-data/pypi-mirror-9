from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
import json


class ImgerWidget(forms.Widget):

    def __init__(self, attrs=None, **kwargs):
        self.imger_settings = attrs['imger_settings']
        super(ImgerWidget, self).__init__(**kwargs)

    class Media:
        js = (
            'imger/js/jquery-1.11.1.min.js',
            'imger/js/jquery.nouislider.js',
            'imger/js/form2js.js',
            'imger/js/canvas-to-blob.min.js',
            'imger/js/imger-compress.js',
            'imger/js/imger-ui.js',
            'imger/js/imger-init.js'
        )
        css = {
            'all': (
                'imger/css/bootstrap.css',
                'imger/css/bootstrap-theme.css',
                'imger/css/imger.css',
                'imger/css/jquery.nouislider.css'
            )
        }

    def render(self, name, value, attrs=None):
        imger_settings = self.imger_settings
        imger_json = json.dumps(imger_settings)

        static_url = settings.STATIC_URL

        if value is None:
            currently = r''
            current_link = r'Nothing yet'
        else:
            currently = r'%s' % (value)
            current_link = r'<a href="%s%s">%s</a>' % (
                settings.MEDIA_URL,
                value,
                value
            )

        if not static_url.endswith('/'):
            static_url = r'%s/' % (static_url)

        return mark_safe("<p>Currently: %s<br/>Change: <span><button data-static_url=\"%s\" data-imger='%s' class=\"ImgerBrowseBTN\" type=\"button\">Browse</button> <span class=\"ImgerBrowseLabel\">No image selected...</span><input value=\"%s\" class=\"ImgerDataURL\" name=\"%s\" type=\"hidden\" /></span></p>" % (current_link, static_url, imger_json, currently, name))
