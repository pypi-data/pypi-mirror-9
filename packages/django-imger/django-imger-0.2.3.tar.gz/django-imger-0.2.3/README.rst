============
django-imger
============

django-imger is an implementation of Imger into Django. Imger is a client side
image resizing and placement tool.

https://github.com/4shaw/imger
https://github.com/4shaw/django-imger

Quick start
-----------

1. Install django-imger::
	
	pip install django-imger

2. Add MEDIA_ROOT and MEDIA_URL to settings.py. something like::

	MEDIA_URL = '/media/'
	MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

3. Add "imger" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'imger',
    )

4. Import ImgerField into your models.yp and create an ImgerField on a model::

    from imger.fields import ImgerField

	...
	image_path = ImgerField(upload_to='testing', imger_settings={'width'=400, 'height'=300, 'quality'=80})


5. Make sure imger static files are in your static directory::

	/static/imger

5. Start the development server and visit http://127.0.0.1:8000/admin/
   Navigate to your model with the imger field and upolad an image
   (you'll need the Admin app enabled).

Other
-----

For lack of documentation at this point here is some more info:

'imger_settings' can include::

	width :: default 300
	height :: default 200
	quality :: default 100
	mime :: default 'image/jpeg'
	autobrowse :: default true
	note :: default ''
	form :: default 'imger.imagename'

If you don't want to prompt for Image name use::

	...
	form: None

	Imger will generate a unique name using the current time.

If you need you generate your own name you need to add an extra parameter to ImgerField called 'generate_name'
which should be a reference to a function that will handle generating a name. This function must accept 1 argument
which will be the supplied 'name'. Empty if you use {... form: None} in the imger_settings or the users input.

The value returned should not contain an extention as the appropriate extention will be automatically added.

Example::

	...
	def makeName(name):
		n = <do something to generate a name>
		return n

	...
		image_path = ImgerField(upload_to='testing', generate_name=makeName, imger_settings={... form: None})
