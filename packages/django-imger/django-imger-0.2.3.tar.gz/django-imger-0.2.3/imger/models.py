"""
from django.db import models
from imger.fields import ImgerField


class Images(models.Model):
    image_path = ImgerField(upload_to='testing', imger_settings={'width': 500, 'height': 300, 'note': 'Explain what the image is for'})

    def __unicode__(self):
        return self.image_path
"""
