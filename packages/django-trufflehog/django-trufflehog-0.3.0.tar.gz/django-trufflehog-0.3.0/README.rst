==========
trufflehog
==========

Keep track of creation, update and hiding of models

.. image:: https://travis-ci.org/jleeothon/trufflehog.svg?branch=master
    :target: https://travis-ci.org/jleeothon/trufflehog

------------
Installation
------------

This was developed using:

- Django 1.7
- Python 3.4

I cannot guarantee it will work for anything older than that, but it probably works for later versions.

Install the latest official release using pip_::

    pip install django-trufflehog

.. _pip: https://pypi.python.org/pypi/pip

You can install the latest development version using pip::

    pip install git+git://github.com/jleeothon/trufflehog/


-----
Usage
-----

    **Warning.** Until release of version 1.0, API is bound to change.

~~~~~~
Models
~~~~~~

There are two ``Model`` subclasses that you can mix into your models: ``DateTraceable`` and ``Hideable``. The former adds two datetime fields to the model: ``created`` and ``updated``.

To include either or both in a model, mix-in these classes like this::

    # models.py
    
    from django.db import models
    from django.db.models import Model
    from trufflehog, import DateTracreable, Hideable
    
    class HappyHog(DateTraceable, Hideable, Model):
        name = models.CharField(max_length=100)
        happiness = models.IntegerField()

Given there exists ``happy_hog = HappyHog(name="Moccus")``, check the datetime of creation and edition with ``happy_hog.created`` and ``happy_hog.updated``.

When checking whether or not a model is hidden, ``happy_hog.hidden`` will return the datetime of deletion and can be used as a boolean test. If a boolean variable is strictly necessary, you could use ``happy_hog.is_hidden``.

~~~~~~~~
Managers
~~~~~~~~

Add a manager to peek into only hidden or only visible model instances::

    # models.py
    
    import trufflehog
    
    class HappyHog(DateTraceable, Hideable, Model):
        # some fields here
        
        hidden_objects = trufflehog.VisibilityManager(visible=False)
        visible_objects = trufflehog.VisibilityManager(visible=True)

But if you want to override the default ``objects`` manager::

    objects = trufflehog.VisibilityManager(visible=True)

You can also create your own custom managers by mixing-in ``VisibilityManagerMixin``::

    # mymanagers.py
    
    from django.db import models
    import trufflehog.managers
    
    class SuperHappyHogManager(trufflehog.managers.VisibilityManagerMixin, models.Manager):
        def get_queryset(self):
            """
            Only queries on hogs whose happiness is over 9000.
            """
            q = super(HappyHogManager, self).get_queryset()
            q = q.filter(happiness__gt=9000)
            return q

------
Thanks
------

Well, thanks. At least for reading this. Also, if you file an issue or contribute to this repository, have my thanks beforehand. Any good or bad ideas or comments are appreciated.
