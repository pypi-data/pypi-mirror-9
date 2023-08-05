=================
django-initialcon
=================

django-initialcon is a small django application for generating small colourful
icons for users profile pictures. Project is hosted on Github https://github.com/bettsmatt/django-initialcon

.. image:: https://raw.github.com/bettsmatt/django-initialcon/master/docs/_static/images/p1.png
.. image:: https://raw.github.com/bettsmatt/django-initialcon/master/docs/_static/images/p2.png
.. image:: https://raw.github.com/bettsmatt/django-initialcon/master/docs/_static/images/p3.png
.. image:: https://raw.github.com/bettsmatt/django-initialcon/master/docs/_static/images/p4.png
.. image:: https://raw.github.com/bettsmatt/django-initialcon/master/docs/_static/images/p5.png
.. image:: https://raw.github.com/bettsmatt/django-initialcon/master/docs/_static/images/p6.png
.. image:: https://raw.github.com/bettsmatt/django-initialcon/master/docs/_static/images/p7.png

Quick start
-----------

1. Install using PIP::

    pip install django-initialcon

2. Add 'initialcon' to INSTALLED_APPS::

    INSTALLED_APPS = {
        ...
        'initialcon',
    }

3. Include the initialcon URLconf in __init__.py::

    url(r'^initialcon/', include('initialcon')),

4. Add font config to your settings.py::

    INITIALCON_FONTS = {
        'default': <pathtofont>),
        'alt': <pathtofont>)
    }

5. Run the development server and test everything works by accessing http://127.0.0.1:8000/initialcon/test%20name

Configuration
-------------

Along with the fonts used the default size, maximum size and colors can be set by adding the following to your settings.py.::

    INITIALCON_SIZE = 100
    INITIALCON_SIZE_MAX = 200)
    INITIALCON_COLORS = [
        (153,180,51), (0,163,0), (30,113,69), (255,0,151), (45,137,239),
        (159,0,167), (0,171,169), (185,29,71),(227,162,26), (255,196,13),
        (126,56,120), (96,60,186), (43,87,151), (218,83,44), (238,17,17)
    ]
    INITIALCON_FONTS = {
        'default': <pathtofont>),
        'alt': <pathtofont>)
    }

Example URLs
-------------

1. Basic::

    localhost:8000/initialcon/test%20name

2. Custom size::

    localhost:8000/initialcon/test%20name?size=200
3. Custom font::

    localhost:8000/initialcon/test%20name?font=alt

4. Custom size and font::

    localhost:8000/initialcon/test%20name?size=200&font=alt

Example code
------------

Template::

    <img src="{{img.getImage}}" />


Code::

    class MyModel(model.Models):

        image = ...
        name = ...

        def getImage(self):
            if self.image:
                ...
            else:
                 return reverse('initialcon:generate', args=[self.name])
