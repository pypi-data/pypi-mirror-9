import unittest
import sys
import os
import shutil
import subprocess
import inspect
import gc


class CaPBase(object):
    """ CaP base class """

    def __init__(self):
        pass

    def remove_dir(self, dir_name):
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

    def create_dir(self, dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def delete_file(self, file_name):
        if os.path.exists(file_name):
            os.remove(file_name)

    def copy_file(self, source, destination):
        shutil.copy2(source, destination)

    def info(self, info_msg):
        print >> sys.stderr, info_msg

    def throw(self, err_msg):
        raise Exception(err_msg)

    @property
    def current_func_name(self):
        frame = inspect.currentframe(1)
        code  = frame.f_code
        globs = frame.f_globals
        functype = type(lambda: 0)
        funcs = []
        for func in gc.get_referrers(code):
            if type(func) is functype:
                if getattr(func, "func_code", None) is code:
                    if getattr(func, "func_globals", None) is globs:
                        funcs.append(func)
                        if len(funcs) > 1:
                            return None
        return funcs[0].__name__ if funcs else None


class Tester(unittest.TestCase, CaPBase):
    """ general CaP template for testing """

    individual_debug = False

    def __init__(self, test_name):
        unittest.TestCase.__init__(self, test_name)
        CaPBase.__init__(self)

    def remove_dir(self, dir_name):
        self.assertTrue(dir_name, '"None" is not a valid directory')
        CaPBase.remove_dir(self, dir_name)

    def create_dir(self, dir_name):
        self.assertTrue(dir_name, '"None" is not a valid directory')
        CaPBase.create_dir(self, dir_name)

    def empty_working_dir(self):
        if not self.individual_debug:
            self.remove_dir(self.working_dir)
        self.create_dir(self.working_dir)

    def remove_working_dir(self):
        if not self.individual_debug:
            self.remove_dir(self.working_dir)

    def set_dir(self):
        self.working_dir = os.path.join(os.path.join(os.path.join(os.path.dirname(__file__),
                                                                  'tmp'),
                                                     self.test_class),
                                        self.test_function)
        self.data_dir= os.path.join(os.path.join(os.path.dirname(__file__), 
                                                 'data'),
                                    self.test_class)

    def init_test(self, test_function):
        self.test_function = test_function
        self.set_dir()
        self.empty_working_dir()

    def tearDown(self):
        self.remove_working_dir()


class SafeTester(Tester):
    """

    General template for testing
    that can be run in both dev and production environment
    The purpose of this template is to test general functionality

    """

    def __init__(self, test_name):
        Tester.__init__(self, test_name)


class RiskyTester(Tester):
    """

    General template for testing
    that can be run only in devevelopment environment

    The purpose of this template is to test
    if the modules can function properly in real environment

    """

    def __init__(self, test_name):
        Tester.__init__(self, test_name)

    def remove_user_dir(self):
        if not self.individual_debug:
            self.remove_dir(cbv_const.USER_DATA_ROOT)
