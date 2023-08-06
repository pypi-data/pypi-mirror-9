# coding=utf-8
"""
run_unit_test
Active8 (05-03-15)
license: GNU-GPL2
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import input

import os
import sys
import unittest
from optparse import OptionParser
from pyprofiler import start_profile, end_profile
from consoleprinter import console, console_warning, clear_screen


def run_unit_test(class_name=None, methodname=None, caller_globals=None, failfast=True, profile=False, quiet=True):
    """
    @type class_name: str, unicode, None
    @type methodname: str, unicode, None
    @type caller_globals: str, unicode, None
    @type failfast: bool
    @type profile: bool
    @type quiet: bool
    @return: None
    """

    # clear_screen()
    suite = unittest.TestSuite()

    if failfast is None:
        failfast = True

    if methodname and not class_name:
        for i in caller_globals:
            if isinstance(caller_globals[i], type):
                if issubclass(caller_globals[i], unittest.TestCase):
                    for m in dir(caller_globals[i]):
                        if methodname == m:
                            if class_name:
                                console("found another", m, "in", i, color="red")
                                a = eval(input("would you like to use this one? (y/n=default): "))

                                if a.strip().lower() == "y":
                                    class_name = i
                            else:
                                if quiet is False:
                                    console("found", m, "in", i, color="cyan")

                                class_name = i

        if not class_name:
            raise ValueError("run_unit_test:cannot find class for method")

    cl = [os.path.basename(os.getcwd())]

    if methodname and class_name:
        cl.append(class_name + ":" + methodname)
    elif class_name:
        cl.append(class_name)
    elif methodname:
        cl.append(methodname)

    if failfast is True:
        if quiet is False:
            cl.append("failing fast")

    if class_name != "_*_":
        if len(cl) > 0:
            if quiet is False:
                console(*cl, color="cyan")

    if methodname and class_name:
        cls = caller_globals[class_name]
        suite.addTest(cls(methodname))
    else:
        if class_name is not None:
            suite = unittest.TestLoader().loadTestsFromTestCase(caller_globals[class_name])
        else:
            if "TESTDIR" in os.environ:
                suite = unittest.TestLoader().discover(os.environ["TESTDIR"])
            else:
                suite = unittest.TestLoader().discover(".")

    try:

        # noinspection PyProtectedMember
        if len(suite._tests) == 0:
            console_warning("Can't find tests, looked in test*.py")
    except BaseException as e:
        console_warning(e)

    profiletrace = None

    if profile is True:
        profiletrace = start_profile()

    if quiet is True:
        sbuffer = ""
        result = unittest.TextTestRunner(failfast=failfast, stream=open("/dev/null", "w"), buffer=sbuffer).run(suite)
    else:
        result = unittest.TextTestRunner(failfast=failfast).run(suite)

    if profiletrace is not None:
        end_profile(profiletrace, items=50)

    return result


def print_error_coll(coll):
    """
    @type coll: list
    @return: None
    """
    for f in coll:
        for es in f:
            es = str(es)

            if "\n" in es:
                for i in es.split("\n"):
                    print(i)
            else:
                console(es)


def unit_test_main(caller_globals=None):
    """
    @type caller_globals: dict
    """
    parser = OptionParser()
    parser.add_option("-c", "--class", dest="classname", default=None, help="UnitTest classname")
    parser.add_option("-m", "--method", dest="method", default=None, help="UnitTest methodname (optional)")
    parser.add_option("-f", "--failfast", dest="failfast", action="store_true", help="Fail fast")
    parser.add_option("-a", "--all", dest="all", action="store_true", help="Run all test without stop on fail")
    parser.add_option("-s", "--showclasses", dest="showclasses", action="store_true", help="Show all classes")
    parser.add_option("-r", "--resetconsole", dest="resetconsole", action="store_true", help="Reset console (clear screen)")
    parser.add_option("-p", "--profile", dest="profile", action="store_true", help="Profile the method", default=False)
    parser.add_option("-q", "--quiet", dest="quiet", action="store_true", help="Silence output except when there is an error", default=False)
    (options, args) = parser.parse_args()

    if options.resetconsole:
        clear_screen()

    if options.all is None:
        options.all = True

    if options.quiet is None:
        options.quiet = True

    if options.all is True and options.failfast is None:
        options.failfast = False

    stderr = sys.stderr
    stdout = sys.stdout

    if options.quiet is True:
        sys.stdout = open("/dev/null", "w")
        sys.stderr = open("/dev/null", "w")

    if options.showclasses:
        options.classname = "_*_"
    try:
        methods = []

        if options.method is not None:
            options.method = options.method.replace(" ", "")

            if "," in options.method:
                methods = options.method.split(",")

        results = []

        if len(methods) > 0:
            for m in methods:
                result = run_unit_test(options.classname, m, caller_globals, options.failfast, options.profile, quiet=options.quiet)
                results.append(result)
        else:
            result = run_unit_test(options.classname, options.method, caller_globals, options.failfast, options.profile, quiet=options.quiet)
            results.append(result)

        sys.stdout = stdout
        sys.stderr = stderr

        if options.quiet is True:
            for r in results:
                if len(r.errors) > 0:
                    coll = r.errors
                    print_error_coll(coll)

                if len(r.failures) > 0:
                    coll = r.failures
                    print_error_coll(coll)

    except (KeyError, ValueError) as e:
        testclasses = []
        mcnt = 1

        for i in caller_globals:
            if isinstance(caller_globals[i], type):
                if issubclass(caller_globals[i], unittest.TestCase):
                    testclasses.append(i)
                    for m in dir(caller_globals[i]):
                        if "test_" in m:
                            console(mcnt, i + ":" + m, color="green")
                            mcnt += 1

        for i in testclasses:
            console(i, color="blue")

        if isinstance(e, KeyError):
            if options.classname != "_*_":
                console_warning("Class not found", options.classname)

        elif isinstance(e, ValueError):
            if options.classname:
                console_warning("Method not found", options.classname, options.method)
            else:
                console_warning("Method not found", options.method)
