from django.conf import settings
from .models import ConfVar
import os
import importlib
DEFAULT = 'global_vars'


class SingletonVar(object):

    ATTRIBUTES = {}

    def __new__(cls, *a, **k):
        if not hasattr(cls, '_inst'):
            cls._inst = super(SingletonVar, cls).__new__(cls, *a, **k)
        return cls._inst

    def __getattr__(self, key):
        if not bool(len(self.ATTRIBUTES)):
            self.load_attributes()
        return self.ATTRIBUTES.get(key, None)

    def getAll(self):
        if not bool(len(self.ATTRIBUTES)):
            self.load_attributes()
        return eval(str(self.ATTRIBUTES))

    def set(self, name, default=0):
        var, created = ConfVar.objects.get_or_create(name=name)
        if created:
            var.value = str(default)
            var.save(reload=False)
        self.ATTRIBUTES[var.name] = var.value

    def reload(self, name, value):
        self.ATTRIBUTES[name] = value

    def load_attributes(self):
        try:
            vars_path = settings.GLOBAL_VARS_PATH
        except Exception:
            print "*******************************************************************"
            print "*******************************************************************"
            print "No GLOBAL_VARS_PATH defined in your settings, using default module '{}'. \n".format(DEFAULT)
            print "*******************************************************************"
            print "*******************************************************************\n"
            vars_path = DEFAULT

        try:
            __import__(vars_path)
        except ImportError:
            print "*******************************************************************"
            print "*******************************************************************"
            print "No module named '{}'. \n\nPlease, read the documentation https://github.com/MaoAiz/django-admin-conf-vars#installation\n".format(vars_path)
            print "*******************************************************************"
            print "*******************************************************************"



config = SingletonVar()
