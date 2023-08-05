django-db-obfuscate-id
============

A reusable Django app that psuedo encrypts your id at database level.

What is this
------------

This is a small app that helps help you change your Autofield ids of your models into a "psuedo-encrypted" id sequence
The encryption is done on database layer so you won't have to worry about complicating your queries or sketching your model managers

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install db-obcuscate-id

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/thisiscam/django-db-obfuscate-id.git#egg=db_obfuscate

Add ``db_obfuscate`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'db_obfuscate',
    )

Add full paths to your models to your ``settings.py``

.. code-block:: python

    ENCRYPT_ID_FOR_MODELS = (
        'django.contrib.auth.models.User',
        ...
    )

Alternatively, you can set a class attribute flag as follow

.. code-block:: python

    class MyEncrypedIdModel(models.Model):
        pseudo_encrypt_id = True


Note: Currently, the app only supports postgres, and takes advantage of psuedo-encrypt scripts given here https://wiki.postgresql.org/wiki/Pseudo_encrypt

More support to be added in the future, and feel free to PR since I'm not using other databases other than postgres now, and will only be updating this repo on a per-use basis

Usage
-----

After setting up, you can conveniently call the management command

.. code-block:: bash

    python manage.py db --encrypt-all #this will encrypt all your models specified in settings.py and those flagged true for pseudo_encrypt_id

    python manage.py db --encrypt-model myapp.models.SomeModelA myapp.models.SomeModelB #this will encrypt all the models specified in this command, use this if you want a one time setting


After one of the two commands, your according models will be using a encryped sequence instead of the normal increasing sequence, note that items in the database won't be migrated to the new sequence, so you do have risk that the newly generated ids will collide onto the old existing ids! I'm still thinking of a good solution to this but feel free to PR if you have one. For now, the seemingly safest way is to use an entirely new database with this app and maybe migrate your data to the new database

Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 db-obcuscate-id
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch

In order to run the tests, simply execute ``tox``. This will install two new
environments (for Django 1.6 and Django 1.7) and run the tests against both
environments.
