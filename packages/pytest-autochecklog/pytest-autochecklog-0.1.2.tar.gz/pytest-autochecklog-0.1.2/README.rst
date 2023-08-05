pytest plugin for test_steps auto check and log functions
===============================================================

.. image:: https://pypip.in/v/pytest_autochecklog/badge.png
    :target: https://crate.io/packages/pytest_autochecklog/

.. image:: https://pypip.in/d/pytest_autochecklog/badge.png
    :target: https://crate.io/packages/pytest_autochecklog/

This pytest plugin is very simple, which is for users who use test_steps in py.test framework.
Use this plugin, the function detection mechanism is using pytest runtest_setup to do it, instead of
using the original mechanism, which requires users know more about the auto-function-detection while
writing scripts originally.
Now, it will be all set, while taken care of by this plugin.


Install pytest-autochecklog
---------------------------

::

    pip install pytest-autochecklog


Using
------
Given the following tests (suppose it is in file /test_steps_example/test1.py)

.. code-block:: python

    from test_steps import *
    import random
    def test_example():
        ok("just pass the check and log it")
        #fail("Just fail the check and log it")
        ok(3+2 == 5, "pass if expr else fail")
        #eq("Shanghai", "Beijing", "Shanghai not equal to Beijing")
        eq(4+5, 9)
        ne("Shanghai", "Beijing", "Pass, Shanghai not equal to Beijing")
        #'Shanghai City' contains 'Country', the second parameter could be regex
        check(" 'Shanghai City' =~ 'Country' ", warning=True)
        unmatch("Shanghai City", "Country", "Pass, not contains, regex can be used too")
        check('random.uniform(1,20) > 15', repeat=5)


After installed the plugin for pytest, when you run pytest with the above test case,
then, you will get the following log in logfile /tmp/test_yyyymmdd_hhmm.log by default like::

    Steven-Mac:tmp Steven$ cat test_20150124_1545.log
    2015-01-24 15:45:11,184 - INFO - ------------------------------------------------------
    2015-01-24 15:45:11,197 - INFO - Func test_example in file: /test_steps_example/test1.py
    2015-01-24 15:45:11,198 - INFO - Check-1: just pass the check and log it -PASS-
    2015-01-24 15:45:11,198 - INFO - Check-2: pass if expr else fail -PASS-
    2015-01-24 15:45:11,198 - INFO - Check-3: 9 == 9 -PASS- 9 == 9?
    2015-01-24 15:45:11,199 - INFO - Check-4: Pass, Shanghai not equal to Beijing -PASS- 'Shanghai' != 'Beijing'?
    2015-01-24 15:45:11,202 - INFO - Check-5: 'Shanghai City' =~ 'Country' -PASS- 'Shanghai City' =~ 'Country'
    2015-01-24 15:45:11,202 - WARNING -   ^^^  condition not met (pass due to -w option set)  ^^^
    2015-01-24 15:45:11,203 - INFO - Check-6: Pass, not contains, regex can be used too -PASS- 'Shanghai City' !~ 'Country'?
    2015-01-24 15:45:13,204 - DEBUG -    vvv  Results(-r 5 set) { 1:<11.960281812565919 > 15>  2:<12.284208523480407 > 15>  3:<15.89909604817515 > 15>  }  vvv
    2015-01-24 15:45:13,204 - INFO - Check-7: random.uniform(1,20) > 15 -PASS- 15.89909604817515 > 15 - tried 3 times in 5 seconds


Btw, you can change the log file and format by using test_steps functions.



See more information about test_steps module
--------------------------------------------

https://pypi.python.org/pypi?:action=display&name=test_steps



