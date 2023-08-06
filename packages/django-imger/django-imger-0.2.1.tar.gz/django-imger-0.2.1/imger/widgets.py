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

        if not static_url.endswith('/'):
            static_url = r'%s/' % (static_url)

        return mark_safe("%s<br/><button data-static_url=\"%s\" data-imger='%s' id=\"ImgerBrowseBTN\" type=\"button\">Browse</button> <span id=\"ImgerBrowseLabel\">No image selected...</span><input id=\"ImgerDataURL\" name=\"%s\" type=\"hidden\" />" % (value, static_url, imger_json, name))
