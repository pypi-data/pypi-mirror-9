from __future__ import print_function
from django.test import TestCase
from importlib import import_module
# from doctest import DocTestCase


# Django 1.7 recommends following python 2.4 unittest+doctest recommendations
#  https://docs.djangoproject.com/en/dev/releases/1.6/#new-test-runner
#  https://docs.python.org/2/library/doctest.html#unittest-api
# import unittest
import doctest

import os
PACKAGE = os.path.basename(os.path.dirname(__file__))

# DONT DO THIS: This will wipe the existing buildings!
# from django.core import management 
# management.call_command('loaddata', 'Building.json', verbosity=0)

import inspect

class DocTestCase(TestCase):
    results = {}
    test_count = 0
    failure_count = 0

    def run_doctests(self, module=None, verbose=False):
        if isinstance(module, basestring):
            module = '.'.join(module.split('__'))
            try:
                module = import_module(module)
            except:
                module = import_module(PACKAGE + '.' + module)
        if not module:
            return
        failure_count, test_count = doctest.testmod(module, raise_on_error=False, verbose=verbose)
        self.results[module.__name__] = {}
        self.results[module.__name__]['failure_count'] = failure_count
        self.results[module.__name__]['test_count'] = test_count
        self.test_count += test_count
        self.failure_count += failure_count
        if failure_count:
            msg = "Ran {} doctests for {}.\n    {} passed and {} failed".format(test_count, module.__name__, test_count-failure_count, failure_count)
            msg += "\n        Total results so far:\n         {} passed and {} failed\n".format(self.test_count-self.failure_count, self.failure_count)
            if verbose:
                print(msg)
            else:
                print('Rerunning tests with verbose set because there were failures.')
                print('Because the test database may have been altered by the previous tests, this rerun may fail differently.')
                self.run_doctests(module=module, verbose=True)
            self.fail(msg)


class AllDocTests(DocTestCase):
    # fixtures = ['django-formatted-records.json']

    # def test_models(self):
    #     self.run_doctests(inspect.currentframe().f_code.co_name[5:])

    # def test_views(self):
    #     self.run_doctests(inspect.currentframe().f_code.co_name[5:])

    def test_urls(self):
        self.run_doctests(inspect.currentframe().f_code.co_name[5:])


def run():
    from django.core.management import execute_from_command_line

    # FIXME:
    # /usr/src/projects/predict/predict/webapp/dashboard/models.py:77: RemovedInDjango19Warning: Model class models.Building doesn't declare an explicit app_label and either isn't in an application in INSTALLED_APPS or else was imported before its application was loaded. This will no longer be supported in Django 1.9. class Building(models.Model):
    execute_from_command_line(['manage.py', 'test'])

    # from django.core import management
    #
    # # FIXME: 
    # #   File "/usr/local/share/.virtualenvs/predict/lib/python2.7/site-packages/django/utils/translation/trans_real.py", line 163, in _add_installed_apps_translations
    # #     "The translation infrastructure cannot be initialized before the "
    # #     django.core.exceptions.AppRegistryNotReady: The translation infrastructure cannot be initialized before the apps registry is ready. Check that you don't make non-lazy gettext calls at import time.
    # management.call_command('test', verbosity=1)


if __name__ == '__main__':
    import os
    import sys
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    if BASE_DIR not in sys.path:
        sys.path.insert(1, BASE_DIR)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")
    run()

# def load_tests(loader, tests, ignore):
#     """
#     Creating test database for alias 'default'...
#     ......EE
#     ======================================================================
#     Traceback (most recent call last):
#       File "./manage.py", line 10, in <module>
#         execute_from_command_line(sys.argv)
#       File "/usr/local/share/.virtualenvs/predict/lib/python2.7/site-packages/django/core/management/__init__.py", line 338, in execute_from_command_line
#         utility.execute()
#       File "/usr/local/share/.virtualenvs/predict/lib/python2.7/site-packages/django/core/management/__init__.py", line 330, in execute
#         self.fetch_command(subcommand).run_from_argv(self.argv)
#       File "/usr/local/share/.virtualenvs/predict/lib/python2.7/site-packages/django/core/management/commands/test.py", line 30, in run_from_argv
#         super(Command, self).run_from_argv(argv)
#       File "/usr/local/share/.virtualenvs/predict/lib/python2.7/site-packages/django/core/management/base.py", line 390, in run_from_argv
#         self.execute(*args, **cmd_options)
#       File "/usr/local/share/.virtualenvs/predict/lib/python2.7/site-packages/django/core/management/commands/test.py", line 74, in execute
#         super(Command, self).execute(*args, **options)
#       File "/usr/local/share/.virtualenvs/predict/lib/python2.7/site-packages/django/core/management/base.py", line 441, in execute
#         output = self.handle(*args, **options)
#       File "/usr/local/share/.virtualenvs/predict/lib/python2.7/site-packages/django/core/management/commands/test.py", line 90, in handle
#         failures = test_runner.run_tests(test_labels)
#       File "/usr/local/share/.virtualenvs/predict/lib/python2.7/site-packages/django/test/runner.py", line 211, in run_tests
#         result = self.run_suite(suite)
#       File "/usr/local/share/.virtualenvs/predict/lib/python2.7/site-packages/django/test/runner.py", line 178, in run_suite
#         ).run(suite)

#       !!!!!!!!!!!!! 
#       !!! DONT UNDERSTAND WHY system python2.7 is used for unittest but not for django test runner. 
#       !!! Import doctest, doctest.__file__ also points to system level install: 

#       File "/usr/lib64/python2.7/unittest/runner.py", line 158, in run
#         result.printErrors()
#       File "/usr/lib64/python2.7/unittest/runner.py", line 108, in printErrors
#         self.printErrorList('ERROR', self.errors)
#       File "/usr/lib64/python2.7/unittest/runner.py", line 114, in printErrorList
#         self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
#       File "/usr/lib64/python2.7/unittest/runner.py", line 44, in getDescription
#         doc_first_line = test.shortDescription()
#       File "/usr/lib64/python2.7/doctest.py", line 2314, in shortDescription
#         return "Doctest: " + self._dt_test.name
#     """
#     print('Ignoring doctest runner because it borks...')
#     return tests

#     import models
#     test_suite = doctest.DocTestSuite(models)
#     for test in test_suite:
#         cls = test.__class__
#         test.__class__ = cls.__class__(cls.__name__ + "WithDajngoTestCaseBase", (cls, DocTestCase), {})
#         tests.addTests(test_suite)
#     return tests



