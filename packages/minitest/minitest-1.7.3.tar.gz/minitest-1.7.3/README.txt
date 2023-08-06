Mini Test
=========

This project is inspired by Ruby minispec, but now it just implement
some methods including:

::

    must_equal, must_true, must_false, must_raise, only_test.

And some other useful functions:

::

    p, pp, pl, ppl, length, size, inject, flag_test,
    p_format, pp_format, pl_format, ppl_format.

github: https://github.com/jichen3000/minitest

pypi: https://pypi.python.org/pypi/minitest

--------------

Author
~~~~~~

Colin Ji jichen3000@gmail.com

How to install
~~~~~~~~~~~~~~

::

    pip install minitest

How to use
~~~~~~~~~~

For a simple example, you just write a function called x, and I would
like to write the unittest in same file as: code:

::

    if __name__ == '__main__':
        # import the minitest
        from minitest import *

        import operator

        # declare a variable for test
        tself = get_test_self()
        # you could put all your test variables on tself
        # just like declare your variables on setup.
        tself.jc = "jc"

        # declare a test
        with test(object.must_equal):
            tself.jc.must_equal('jc')
            None.must_equal(None)


        with test(object.must_true):
            True.must_true()
            False.must_true()

        with test(object.must_false):
            True.must_false()
            False.must_false()

        # using a funcation to test equal.
        with test("object.must_equal_with_func"):
            (1).must_equal(1, key=operator.eq)
            (1).must_equal(2, key=operator.eq)

        def div_zero():
            1/0
            
        # test exception
        with test("test must_raise"):
            (lambda : div_zero()).must_raise(ZeroDivisionError)
            (lambda : div_zero()).must_raise(ZeroDivisionError, "integer division or modulo by zero")
            (lambda : div_zero()).must_raise(ZeroDivisionError, "in")

        # when assertion fails, it will show the failure_msg
        with test("with failure_msg"):
            the_number = 10
            (the_number % 2).must_equal(1, 
                failure_msg="{0} is the number".format(the_number))
            # it wont show the failure_msg
            (the_number % 2).must_equal(0, 
                failure_msg="{0} is the number".format(the_number))

            (True).must_false(
                failure_msg="{0} is the number".format(the_number))

            (lambda : div_zero()).must_raise(ZeroDivisionError, "in",
                failure_msg="{0} is the number".format(the_number))

result:

::

    Running tests:

    .FFFF.

    Finished tests in 0.013165s.

    1) Failure:
    File "/Users/Colin/work/minitest/test.py", line 29, in <module>:
    EXPECTED: True
      ACTUAL: False


    2) Failure:
    File "/Users/Colin/work/minitest/test.py", line 32, in <module>:
    EXPECTED: False
      ACTUAL: True


    3) Failure:
    File "/Users/Colin/work/minitest/test.py", line 38, in <module>:
    EXPECTED: 2
      ACTUAL: 1


    4) Failure:
    File "/Users/Colin/work/minitest/test.py", line 47, in <module>:
    EXPECTED: 'in'
      ACTUAL: 'integer division or modulo by zero'


    5) Failure:
    File "/Users/colin/work/minitest/test.py", line 86, in <module>:
     MESSAGE: '10 is the number'
    EXPECTED: 1
      ACTUAL: 0


    6) Failure:
    File "/Users/colin/work/minitest/test.py", line 92, in <module>:
     MESSAGE: '10 is the number'
    EXPECTED: False
      ACTUAL: True


    7) Failure:
    File "/Users/colin/work/minitest/test.py", line 95, in <module>:
     MESSAGE: '10 is the number'
    EXPECTED: 'in'
      ACTUAL: 'integer division or modulo by zero'


    10 tests, 18 assertions, 7 failures, 0 errors.
    [Finished in 0.1s]

only\_test function
~~~~~~~~~~~~~~~~~~~

If you just want to run some test functions, you can use only\_test
funtion to specify them. Notice, you must put it on the top of test
functions, just like the below example. code:

::

    def foo():
        return "foo"

    def bar():
        return "bar"

    if __name__ == '__main__':
        from minitest import *


        only_test("for only run", foo)

        with test("for only run"):
            (1).must_equal(1)
            (2).must_equal(2)
            pass

        with test("other"):
            (1).must_equal(1)
            (2).must_equal(2)
            pass    

        with test(foo):
            foo().must_equal("foo")

        with test(bar):
            bar().must_equal("bar")

It will only run test("for only run") and test(foo) for you.

Other useful function
~~~~~~~~~~~~~~~~~~~~~

p, pp, pl, ppl, length, size, p\_format, pp\_format, pl\_format,
ppl\_format these ten functions could been used by any object.

p, print with title. This function will print variable name as the
title. code:

::

    value = "Minitest"
    value.p()
                                    
    value.p("It is a value:")   
                                    
    value.p(auto_get_title=False)    

print result:

::

    value : 'Minitest'

    It is a value: 'Minitest'

    'Minitest'

pp, pretty print with title. This function will print variable name as
the title in the first line, then pretty print the content of variable
below the title. code:

::

    value = "Minitest"
    value.pp()
                                    
    value.pp("It is a value:")   
                                    
    value.pp(auto_get_title=False)    

print result:

::

    value :
    'Minitest'

     It is a value:
    'Minitest'

    'Minitest'

pl, print with title and code loction. This function just like pt, but
will print the code location at the first line. And some editors support
to go to the line of that file, such as Sublime2. code:

::

    value = "Minitest"
    value.pl()
                                    
    value.pl("It is a value:")   
                                    
    value.pl(auto_get_title=False)    

print result:

::

        File "/Users/Colin/work/minitest/test.py", line 76
    value : 'Minitest'


        File "/Users/Colin/work/minitest/test.py", line 77
     It is a value: 'Minitest'


        File "/Users/Colin/work/minitest/test.py", line 78
    'Minitest'

ppl, pretty print with title and code loction. This function just like
ppt, but will print the code location at the first line. Notice: it will
print a null line firstly. code:

::

    value = "Minitest"
    value.ppl()
                                    
    value.ppl("It is a value:")   
                                    
    value.ppl(auto_get_title=False)    

print result:

::

        File "/Users/Colin/work/minitest/test.py", line 76
    value :
    'Minitest'


        File "/Users/Colin/work/minitest/test.py", line 77
     It is a value:
    'Minitest'


        File "/Users/Colin/work/minitest/test.py", line 78
    'Minitest'

p\_format, get the string just like p function prints. I use it in
debugging with log, like: logging.debug(value.p\_format()) code:

::

    value = "Minitest"
    value.p_format()

return result:

::

    value : 'Minitest'

pp\_format, get the string just like pp function prints. I use it in
debugging with log, like: logging.debug(value.pp\_format()) code:

::

    value = "Minitest"
    value.pp_format()

return result:

::

    value :\n'Minitest'

pl\_format, get the string just like pl function prints. I use it in
debugging with log, like: logging.debug(value.pl\_format()) code:

::

    value = "Minitest"
    value.pl_format()

return result:

::

    line info: File "/Users/Colin/work/minitest/test.py", line 76, in <module>\nvalue : 'Minitest'

ppl\_format, get the string just like ppl function prints. I use it in
debugging with log, like: logging.debug(value.ppl\_format()) code:

::

    value = "Minitest"
    value.ppl_format()

return result:

::

    line info: File "/Users/Colin/work/minitest/test.py", line 76, in <module>\nvalue :\n'Minitest'

length and size will invoke len function for the caller's object. code:

::

    [1,2].length()                  # 2, just like len([1,2])
    (1,2).size()                    # 2, just like len((1,2))

inject\_customized\_must\_method or inject function will inject the
function which you customize. Why do I make this function? Since in many
case I will use numpy array. When it comes to comparing two numpy array,
I have to use:

::

    import numpy
    numpy.array([1]).must_equal(numpy.array([1.0]), numpy.allclose)

For being convient, I use inject\_customized\_must\_method or inject
function like:

::

    import numpy
    inject(numpy.allclose, 'must_close')
    numpy.array([1]).must_close(numpy.array([1.0]))

flag\_test will print a message 'There are codes for test in this
place!' with the code loction. code:

::

    flag_test()

    # add a title
    flag_test("for test")

print result:

::

        File "/Users/colin/work/minitest/test.py", line 97, in <module>:
    There are test codes in this place!    

        File "/Users/colin/work/minitest/test.py", line 101, in <module>:
    for test : There are test codes in this place!    

