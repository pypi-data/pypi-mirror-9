from django import forms
from django.utils.safestring import mark_safe


class ImgerWidget(forms.Widget):

    def __init__(self, attrs=None, *args, **kwargs):
        self.width = attrs['width']
        self.height = attrs['height']
        self.mime = attrs['mime']
        self.quality = attrs['quality']
        super(ImgerWidget, self).__init__(*args, **kwargs)

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
        w = self.width
        h = self.height
        t = self.mime
        q = self.quality

        print '%sX%s' % (w, h)

        return mark_safe("%s<br/><button data-width=\"%s\" data-height=\"%s\" data-mime=\"%s\" data-quality=\"%s\" type=\"button\" id=\"ImgerBrowseBTN\">Browse</button> <span id=\"ImgerBrowseLabel\">No image selected...</span><input id=\"ImgerDataURL\" name=\"%s\" type=\"hidden\" />" % (value, w, h, t, q, name))
