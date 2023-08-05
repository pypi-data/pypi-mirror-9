=====
Tethys Compute
=====

Tethys Compute is a Django app that is intended to add admin controls for computing resources.
Computing resources are managed through the Python module TethysCluster

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "tethys_compute" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'tethys_compute',
    )

2. Include the tethys_compute URLconf in your project urls.py like this::

    url(r'^compute-admin/', include('tethys_compute.urls')),

3. Run `python manage.py migrate` to create the tethys_compute models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
