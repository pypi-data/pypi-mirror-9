=====
Imger
=====

Imger is a client side resizing and placement tool for images.
Images are stored in the settings.MEDIA_ROOT so settings.py needs to include:
MEDIA_ROOT and MEDIA_URL

Quick start
-----------

1. Add MEDIA_ROOT and MEDIA_URL to settings.py. something like::

	MEDIA_URL = '/media/'
	MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

2. Make sure imger static files are in your static directory::

	/static/imger

3. Add "imger" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'imger',
    )

4. Import ImgerField into your models.yp and create an ImgerField on a model::

    from imger.fields import ImgerField

	...
	image_path = ImgerField(upload_to='testing', imger_settings={'width'=400, 'height'=300, 'quality'=80})

	No documentation yet but for a quick reference imger_settings can include:

	width :: default 300
	height :: default 200
	quality :: default 100
	mime :: default 'image/jpeg'
	autoborwse :: default true
	note :: default ''

5. Start the development server and visit http://127.0.0.1:8000/admin/
   Navigate to your model with the imger field and upolad an image
   (you'll need the Admin app enabled).
