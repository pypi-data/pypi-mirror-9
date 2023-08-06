django-ma-settings
==================

Master Settings is a simple Django app to have simple typed settings in django app with type validation.


Installation & Setup
--------------------

1. Install using pip

.. code-block:: bash

    $> pip install django-ma-settings


2. add 'ma-settings' into INSTALLED_APPS

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'ma_settings',
        # ...
    )

3. define MASTER_SETTINGS dict with your settings definition

template:

.. code-block:: python

    MASTER_SETTINGS = {
        '(setting_name)':{
            'type' : '(setting_type)',
            'display_name': '(displayed name)', #optional
            'default': (default value), # optional
            'options': (choice options), # optional
            'model': (foreign model), # optional, use only when foreign type is chosen
        }
    }

example:

.. code-block:: python

    MASTER_SETTINGS = {
        'max_email_size_kb': {
            'type': 'integer',
            'display_name': 'Max email size(kb)',
            'default': 400,
        },
        'text_color': {
            'type': 'choices',
            'display_name': 'Text color',
            'options': ['White', 'Black', 'Red', 'Blue'],
            'default': 'White',
        },
        'our_rate': {
            'type': 'float',
            'display_name': 'Our rate',
            'default': 1.0,
        },
        'email_from': {
            'type': 'string'
            'display_name': 'Email from',
        },
        'Default client': {
            'type': 'foreign',
            'model': 'my_app.Client'
        }
    }

4. define BASE_SETTINGS_TEMPLATE_NAME

.. code-block:: python

    BASE_SETTINGS_TEMPLATE_NAME = "template_name.html"

    #  Template file must contain empty {% block settings %}

5. in urls.py add include('ma_settings.urls')

.. code-block:: python

    url(r'^settings/', include('ma_settings.urls')),

    #  Use url name 'master_settings_home' to access settings page

    {% url 'master_settings_home' %}

6. Run commands to initialize settings

.. code-block:: bash

    $> python manage.py syncdb
    $> python manage.py init_settings



Using
-----

To get setting use

.. code-block:: python

    from ma_settings import master_settings
    master_settings.get('setting_name', default='default')

To set new value:

.. code-block:: python

    master_settings.set('setting_name', [value|model_instance])

To check if setting exists:

.. code-block:: python

    master_settings.exists('setting_name')


Updating settings definition
----------------------------

After updating settings definition in settings.py run this command to update settings

.. code-block:: bash

     python manage.py init_settings
