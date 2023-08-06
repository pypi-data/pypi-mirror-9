"""
from django.db import models
from imger.fields import ImgerField


class Images(models.Model):
    image_path = ImgerField(upload_to='testing', width=400, height=200, mime='image/jpg', quality=80)

    def __unicode__(self):
        return self.image_path
"""
