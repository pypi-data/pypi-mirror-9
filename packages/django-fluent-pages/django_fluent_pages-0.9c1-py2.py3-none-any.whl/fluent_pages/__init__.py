# following PEP 386
__version__ = "0.9c1"

# Do some sane version checking
import django
import mptt

if django.VERSION < (1,4,0):
    raise ImportError("At least Django 1.4.0 is required to run this application")

if mptt.VERSION < (0,5,4):
    raise ImportError("At least django-mptt 0.5.4 is required to run this application")
