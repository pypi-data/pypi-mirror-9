from django.db import models
from django.core import exceptions
from imger.widgets import ImgerWidget
from django.conf import settings
import json
import re


class ImgerField(models.Field):
    description = "Handles imger images via dataurl"

    metaclass__ = models.SubfieldBase

    def __init__(
        self,
        upload_to='',
        width=300,
        height=200,
        mime='image/jpg',
        quality=100,
        *args,
        **kwargs
    ):
        self.upload_to = upload_to
        self.width = width
        self.height = height
        self.mime = mime
        self.quality = quality

        super(ImgerField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "Input"

    def db_type(self, connection):
        return 'char(200)'

    def to_python(self, value):
        if value is None:
            return None
        elif value == "":
            return ''
        elif isinstance(value, basestring):
            if(value.startswith('imgerDjango:')):
                arr = value.split(':imgerDjango:', 1)

                json_string = r'%s' % (arr[0][12:])
                dataurl = r'%s' % arr[1]

                formdata = json.loads(json_string)
                imgstr = re.search(r'base64,(.*)', dataurl).group(1)

                media_path = settings.MEDIA_ROOT
                path = r'%s/%s/%s' % (
                    media_path,
                    self.upload_to,
                    formdata['imagename']
                )

                output = open(path, 'wb')
                output.write(imgstr.decode('base64'))
                output.close()

                return r'%s/%s' % (self.upload_to, formdata['imagename'])
            else:
                return value
        else:
            raise exceptions.ValidationError(self.error_messages['invalid'])

    def get_prep_value(self, value):
        if not value:
            return ""
        elif isinstance(value, basestring):
            return value
        else:
            return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    """def clean(self, value, model_instance):
        value = super(DictionaryField, self).clean(value, model_instance)
        return self.get_prep_value(value)"""

    def formfield(self, **kwargs):
        w = self.width
        h = self.height
        t = self.mime
        q = self.quality

        defaults = {
            'widget': ImgerWidget(
                attrs={
                    'width': w,
                    'height': h,
                    'mime': t,
                    'quality': q
                }
            )
        }
        defaults.update(kwargs)

        return super(ImgerField, self).formfield(**defaults)
