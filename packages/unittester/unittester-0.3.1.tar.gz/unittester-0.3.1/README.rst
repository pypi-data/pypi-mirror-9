# unittester
Run python unit-tests as command-line applications (class and method based)

###install
```bash
pip install unittester
```

###options:

```bash
Usage: sample.py [options]

Options:
  -h, --help            show this help message and exit
  -c CLASSNAME, --class=CLASSNAME
                        UnitTest classname
  -m METHOD, --method=METHOD
                        UnitTest methodname (optional)
  -f, --failfast        Fail fast
  -a, --all             Run all test without stop on fail
  -s, --showclasses     Show all classes
  -r, --resetconsole    Reset console (clear screen)
  -p, --profile         Profile the method
  -q, --quiet           Silence output except when there is an error
```

###quiet
Quiet mode only outputs text in case of an error.

####normal
```bash
$ python tests.py -c SampleTestCase2
0.00 | unittester.py:70 | unittester | SampleTestCase2
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

####quiet
```bash
$ python sample.py -q -c SampleTestCase2
$
```