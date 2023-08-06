import os, sys, inspect

# add parent path aka minitest to sys.path, so I can import the files
# realpath() will make your script run, even if you symlink it :)
current_file_path = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
parent_file_path = os.path.realpath(os.path.abspath(os.path.join(current_file_path, '..')))
if parent_file_path not in sys.path:
    sys.path.insert(0, parent_file_path)

def foo():
    return "foo"

def bar():
    return "bar"

def div_zero():
    1/0

if __name__ == '__main__':
    from minitest import *


    only_test("for only run", foo, "must_raise1")
    # only_test("for only run")

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

    with test("must_raise1"):
        (lambda : div_zero()).must_raise(ZeroDivisionError)

    with test("must_raise2"):
        (lambda : div_zero()).must_raise(ZeroDivisionError)
