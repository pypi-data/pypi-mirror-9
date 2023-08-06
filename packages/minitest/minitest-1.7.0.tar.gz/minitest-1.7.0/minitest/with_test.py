'''
    see the atexit.register about how to check if the code is end
''' 

import sys
import inspect
import traceback
from datetime import datetime
import pprint

import inject_methods
from variables import *
import types

__all__ = ['test', 'test_case', 'get_test_self', 'inject', 'inject_customized_must_method']

global_test_function_names = None

class TestSelf(object):
    pass

def get_test_self():
    return TestSelf()

class TestFailure(object):
    def __init__(self, actual, expected, frame, failure_msg):
        self.actual = actual
        self.expected = expected
        self.frame = frame
        self.failure_msg = failure_msg

    def __str__(self):
        result = inject_methods.gen_line_info(self.frame) + "\n"
        if self.failure_msg:
            result += " MESSAGE: %s\n" % pprint.pformat(self.failure_msg)
        result += "EXPECTED: %s\n" % pprint.pformat(self.expected)
        result += "  ACTUAL: %s\n"  % pprint.pformat(self.actual)
        return result

    def __repr__(self):
        return self.__str__()


class TestCase(object):
    def __init__(self, msg=None):
        self.msg = msg
        self.test_methods = []
        self.assertion_count = 0
        self.failures = []
        self.error_count = 0

    def __enter__(self):
        self.start_time = datetime.now()
        print "Running tests:\n"
        set_current_test_case(self)
        return self

    def __exit__(self, e_type=None, value=None, tb=None):
        self.end_time = datetime.now()
        if e_type != None:
            # print e_type
            # print value
            # print tb
            print traceback.format_exc()
            self.add_error_count()
        set_current_test_case(None)
        self.print_report()
        return self

    @classmethod
    def create(clz):
        new_test_case = TestCase("test case")
        new_test_case.__enter__()
        import atexit
        atexit.register(new_test_case.__exit__)
        return new_test_case


    def add_test_method(self, test_method):
        self.test_methods.append(test_method)
        return self

    def add_error_count(self):
        self.error_count += 1;

    def add_assertion(self):
        self.assertion_count += 1

    def add_failure(self, actual, expected, frame, failure_msg):
        self.failures.append(TestFailure(
            actual, expected, frame,failure_msg))

    def print_report(self):
        pass_seconds = (self.end_time - self.start_time).total_seconds()
        print "\n"
        print "Finished tests in %fs.\n" % pass_seconds
        [self.print_failure(index, failure) for index, failure in enumerate(self.failures)]
        # map(self.print_failure, enumerate(self.failures))
        print "%d tests, %d assertions, %d failures, %d errors." %\
          (len(self.test_methods), self.assertion_count, len(self.failures), self.error_count)
        return True
        
    def print_failure(self, index, failure):
        print "%d) Failure:" % (index+1)
        print failure
        print
        return True


# Run options: --seed 38103

# # Running tests:

# F.

# Finished tests in 0.044339s, 45.1070 tests/s, 45.1070 assertions/s.

#   1) Failure:
# test_0001_can work!(OrderDecisionTableBuilder) [/Users/Colin/work/ruby/dsl/advanced_decision_table/order_decision_table_builder.rb:79]:
# --- expected
# +++ actual
# @@ -1 +1 @@
# -[#<struct Consequence description="Fee">, #<struct Consequence description="Alert Re p">]
# +[#<struct Consequence description="Fee">, #<struct Consequence description="Alert Rep">]

# 2 tests, 2 assertions, 1 failures, 0 errors, 0 skips
# [Finished in 0.3s with exit code 1]

# # Running tests:

# ..

# Finished tests in 0.002570s, 778.2101 tests/s, 3501.9455 assertions/s.

# 2 tests, 9 assertions, 0 failures, 0 errors, 0 skips
# [Finished in 0.3s]

class SkipException(Exception):
    def __init__(self, message):
        self.message = message

class TestMethod(object):
    def __init__(self, msg=None):
        self.msg = msg
        self.failed_flag = False

    def __enter__(self):
        # print "test enter"
        # skip some test functions which are not in global_test_function_names
        if global_test_function_names and self.msg not in global_test_function_names:
            sys.settrace(lambda *args, **keys: None)
            frame = inspect.currentframe(1)

            frame.f_trace = self.trace
            return self            
        if not is_current_test_case():
            TestCase.create()
        set_current_test_method(self)
        get_current_test_case().add_test_method(self)
        return self

    def trace(self, frame, event, arg):
        raise SkipException("!!! for only_test!!!")

    def __exit__(self, e_type=None, value=None, tb=None):
        if e_type != None and not isinstance(value, SkipException):
            # print e_type
            # print value
            # print tb
            # print traceback.format_exc()
            get_current_test_case().add_error_count()
        # print "method exit"
        if self.failed_flag:
            sys.stdout.write('F')
        else:
            sys.stdout.write('.')
        sys.stdout.flush()
        set_current_test_method(None)
        return self

    def set_failed(self):
        self.failed_flag = True
        return self.failed_flag

def test_case(msg):
    return TestCase(msg)

def test(msg):
    return TestMethod(msg)

def inject_customized_must_method(key_method, method_name=None, must_method=object.must_equal):
    '''
        Inject the customized method to object and NoneType.
        and the customized must method's default name would be 'must_' plus the key_method's name.
    '''
    def method_func(self, other):
        must_method(self, other, key=key_method)
    method_name = method_name or 'must_'+key_method.func_code.co_name
    inject_methods.set_method_to_object(method_func, method_name)
    inject_methods.set_method_to_builtin(types.NoneType, method_func, method_name)
    return method_func

inject = inject_customized_must_method

def only_test(*args):
    global global_test_function_names
    global_test_function_names = args
    function_names = [func if isinstance(func, str) else func.func_name 
            for func in args]
    print "Notice: only test these functions: {function_names}\n".format(
            function_names=function_names)
    return global_test_function_names
    # if not (isinstance(function_names, list) or isinstance(function_names, tuple)):
    #     function_names = (function_names,)
    # if function_names[0] == 'all':
    #     function_names = None
    #     global_test_function_names = function_names
    #     return function_names
    # global_test_function_names = function_names
    # return function_names



if __name__ == '__main__':

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
        1/0

    def div_zero():
        1/0
        
    # test excecption
    with test("test must_raise"):
        (lambda : div_zero()).must_raise(ZeroDivisionError)
        (lambda : div_zero()).must_raise(ZeroDivisionError, "integer division or modulo by zero")
        (lambda : div_zero()).must_raise(ZeroDivisionError, "in")

    # customize your must method 
    with test("inject"):
        def close_one(int1, int2):
            return int1 == int2+1 or int2 == int1+1
        (1).must_equal(2, close_one)
        inject(close_one)
        (1).must_close_one(2)
        inject(close_one, 'must_close')
        (1).must_close(2)

    with test("check file name in false status"):
        (1).must_equal(10)
        (1).must_equal(10, close_one)
        (1).must_close(10)

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

    with test("format functions"):
        foo=dict(name="foo", value="bar")
        foo.p_format().must_equal("foo : {'name': 'foo', 'value': 'bar'}")
        foo.pp_format().must_equal("foo :\n{'name': 'foo', 'value': 'bar'}")
        # foo.pl_format().must_equal(
        #     'line info: File "/Users/colin/work/minitest/minitest/with_test.py", line 254, in <module>:\n'+
        #     'foo :\n{\'name\': \'foo\', \'value\': \'bar\'}')
        # foo.ppl_format().must_equal(
        #     'line info: File "/Users/colin/work/minitest/minitest/with_test.py", line 257, in <module>:\n'+
        #     'foo :\n{\'name\': \'foo\', \'value\': \'bar\'}')


    class Person(object):
        def __init__(self, name):
            self.name = name

    print "\nstart to show print results:"
    import logging
    logging.basicConfig(level=logging.DEBUG)
    foo=dict(name="foo", value="bar")
    logging.info(foo.p_format())
    logging.info(foo.pp_format())
    logging.info(foo.pl_format())
    logging.info(foo.ppl_format())
    None.p()
    None.pp()
    tself.jc.p()
    tself.jc.p(auto_get_title=False)
    tself.jc.p("jc would be:")
    tself.jc.pp()
    tself.jc.pp(auto_get_title=False)
    tself.jc.pp("jc would be:")
    tself.jc.pl()
    tself.jc.ppl()
    [1, 2].length().pp()
    (1, 2).size().pp()
    flag_test()

    class OldStyle:
        pass

    with test("OldStyle"):
        print (dir(OldStyle()))
        print (dir(Person("nn")))

