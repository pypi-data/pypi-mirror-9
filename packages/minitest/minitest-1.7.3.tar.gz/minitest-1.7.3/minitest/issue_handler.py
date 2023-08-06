from types import ClassType


import new
import inject_methods
pre_classobj = new.classobj
def wraped_classobj(name, baseclasses, the_dict):
    new_class = pre_classobj(name, baseclasses, the_dict)
    # inject_methods.set_method_to_builtin(new_class, classmethod(inject_methods.p), 'p')
    new_class.pp = inject_methods.pp
    return new_class
new.classobj = wraped_classobj


class OldStyle:
    pass
    def pmm():
        print "mm"

class NormalObject(object):
    def __new__(cls):
        print "in the __new__"
    def pmm():
        print "mm"

print ClassType("MM", (OldStyle,), {})


if __name__ == '__main__':
    # from minitest import *
    print pre_classobj
    print (dir(pre_classobj))
    # pre_classobj.pp()

    old_one = OldStyle()
    # old_one.pp()
    # config.pp()
    print dir(old_one)
    print type(OldStyle)
    # print super(OldStyle)
    # print old_one.super()
    print OldStyle.__module__

    normal_one = NormalObject()
    print dir(normal_one)
    print super(NormalObject)

    MM = new.classobj("MM", (OldStyle,), {})
    print dir(MM)
    print type(MM)
    mm = MM()
    mm.pp()
    # new.classobj()


    # with test("for loop"):
    #     for i in range(3):
    #         i.p()
    #         i.must_equal(i)
    #         'true'.must_equal('true')

    # with test("for some object no pp"):
    #     # import ConfigParser
    #     # config = ConfigParser.ConfigParser()
    #     old_one = OldStyle()
    #     # config.pp()
    #     print dir(old_one)
    #     # print super(OldStyle)
    #     # print old_one.super()

    #     normal_one = NormalObject()
    #     print dir(normal_one)
    #     print super(NormalObject)
