from django.db import models
from django.core import exceptions
from imger.widgets import ImgerWidget
from django.conf import settings
import time
import json
import re
import os


class ImgerField(models.Field):
    description = "Handles imger images via dataurl"

    metaclass__ = models.SubfieldBase

    def __init__(
        self,
        upload_to='',
        generate_name=None,
        imger_settings=None,
        **kwargs
    ):
        self.upload_to = upload_to
        self.generate_name = generate_name
        self.imger_settings = imger_settings

        super(ImgerField, self).__init__(**kwargs)

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

                imagename = formdata.get('imagename', '')
                extention = formdata['meta']['save_ext']

                if self.generate_name is not None:
                    if imagename.endswith(extention):
                        imagename = os.path.splitext(imagename)[0]

                    imagename = r'%s%s' % (
                        self.generate_name(imagename),
                        extention
                    )

                if imagename == '':
                    imagename = r'%s%s' % (
                        time.strftime("%Y%m%d%H%M%S"),
                        extention
                    )

                imgstr = re.search(r'base64,(.*)', dataurl).group(1)

                media_path = settings.MEDIA_ROOT
                path = r'%s/%s' % (
                    media_path,
                    self.upload_to
                )

                if not path.endswith('/'):
                    path = r'%s/' % (path)

                if not os.path.exists(path):
                    os.makedirs(path)

                path = r'%s%s' % (path, imagename)

                output = open(path, 'wb')
                output.write(imgstr.decode('base64'))
                output.close()

                return r'%s/%s' % (self.upload_to, imagename)
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
        imger_settings = self.imger_settings

        defaults = {
            'widget': ImgerWidget(
                attrs={
                    'imger_settings': imger_settings,
                }
            )
        }
        defaults.update(kwargs)

        return super(ImgerField, self).formfield(**defaults)
