# Copyright 2013-2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""An extended `unittest.TestCase` to be run using `setup.py` in the
root of a project which may contain several Django projects.

We cannot import :mod:`lino.utils.djangotest` here because
that's designed for unit tests *within a particular* Django project
(run using `djange-admin test`).

"""
import os
import sys
import doctest
import warnings

from atelier.test import TestCase


class TestCase(TestCase):

    """
    """

    demo_settings_module = None
    """
    The `DJANGO_SETTINGS_MODULE` to set for each subprocess
    launched by this test case.
    """

    def build_environment(self):
        env = super(TestCase, self).build_environment()
        if self.demo_settings_module:
            env.update(DJANGO_SETTINGS_MODULE=self.demo_settings_module)
        return env

    def setUp(self):

        if self.demo_settings_module:
            from lino.core.signals import testcase_setup
            testcase_setup.send(self)
        super(TestCase, self).setUp()

    def run_docs_django_tests(self, n, **kw):
        warnings.warn("run_docs_django_tests is deprecated")
        args = ["django-admin.py"]
        args += ["test"]
        args += ["--settings=%s" % n]
        args += ["--failfast"]
        args += ["--traceback"]
        args += ["--verbosity=0"]
        args += ["--pythonpath=%s" % self.project_root.child('docs')]
        self.run_subprocess(args, **kw)

    def run_django_manage_test(self, cwd=None, **kw):
        args = ["python", "manage.py"]
        args += ["test"]
        args += ["--noinput"]
        args += ["--failfast"]
        if cwd is not None:
            kw.update(cwd=cwd)
        self.run_subprocess(args, **kw)

    def run_django_admin_test_cd(self, cwd, **kw):
        kw.update(cwd=cwd)
        args = ["django-admin.py"]
        args += ["test"]
        args += ["--settings=settings"]
        args += ["--pythonpath=."]
        args += ["--verbosity=0"]
        args += ["--noinput"]
        args += ["--failfast"]
        args += ["--traceback"]
        self.run_subprocess(args, **kw)

    def run_django_admin_test(self, settings_module, *args, **kw):
        warnings.warn("run_django_admin_test is deprecated")
        parts = settings_module.split('.')
        assert parts[-1] == "settings"
        cwd = '/'.join(parts[:-1])
        return self.run_django_admin_test_cd(cwd, *args, **kw)

    def run_django_admin_command(self, settings_module, *cmdargs, **kw):
        args = ["django-admin.py"]
        args += cmdargs
        args += ["--settings=%s" % settings_module]
        self.run_subprocess(args, **kw)

    def run_django_admin_command_cd(self, cwd, *cmdargs, **kw):
        kw.update(cwd=cwd)
        args = ["python", "manage.py"]
        args += cmdargs
        # args += ["--settings=settings"]
        # args += ["--pythonpath=."]
        self.run_subprocess(args, **kw)

    def run_docs_doctests(self, filename):
        """
        Run a simple doctest for specified file after importing the
        docs `conf.py` (which causes the demo database to be activated).
        
        This is used e.g. for testing pages like those below
        :doc:`/tested/index`.
        
        
        http://docs.python.org/2/library/doctest.html#doctest.REPORT_ONLY_FIRST_FAILURE
        
        These tests may fail for the simple reason that the demo database
        has not been initialized (in that case, run `fab initdb`).
        """
        filename = 'docs/' + filename
        sys.path.insert(0,  os.path.abspath('docs'))
        import conf  # trigger Django startup

        res = doctest.testfile(filename, module_relative=False,
                               encoding='utf-8',
                               optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)

        del sys.path[0]
        #~ os.chdir(oldcwd)

        if res.failed:
            self.fail("doctest.testfile() failed. See earlier messages.")
