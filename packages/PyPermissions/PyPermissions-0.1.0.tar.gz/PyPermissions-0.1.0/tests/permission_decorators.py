import unittest

from pypermissions.permission import Permission, PermissionSet
from pypermissions.decorators import set_grants_permission, set_has_any_permission


def ret_false(*args, **kw):
    return False


def test_grants_permission(perm):

    def get_perm_set(function):

        def decorator(*args, **kwargs):

            s = set_grants_permission(perm=perm, on_failure=ret_false, perm_set=kwargs.pop('perm_set'))

            return s(function)(*args, **kwargs)

        return decorator

    return get_perm_set


def test_has_any_permission(perm):

    def get_perm_set(function):

        def decorator(*args, **kwargs):

            s = set_has_any_permission(perm=perm, on_failure=ret_false, perm_set=kwargs.pop('perm_set'))

            return s(function)(*args, **kwargs)

        return decorator

    return get_perm_set

class PermissionSetTests(unittest.TestCase):

    def setUp(self):
        self.p1 = Permission("test.1.hello")
        self.p2 = Permission("test.2.hello")
        self.p3 = Permission("test")
        self.p4 = Permission("test.1.hello")
        self.p5 = Permission("test.*")
        self.ps1 = PermissionSet({self.p1, self.p2})
        self.ps2 = PermissionSet({self.p1, self.p4})
        self.ps3 = PermissionSet({self.p3})
        self.ps4 = PermissionSet({self.p5})

    @test_grants_permission("test.1.hello")
    def example_simple_function(self):
        return True

    @test_grants_permission("test.3.hello")
    def example_simple_function_dne(self):
        return True

    @test_has_any_permission("test.*.hello")
    def example_simple_function_2(self):
        return True

    def test_grants_permission(self):
        self.assertTrue(self.example_simple_function(perm_set=self.ps1))
        self.assertFalse(self.example_simple_function_dne(perm_set=self.ps1))
        self.assertTrue(self.example_simple_function(perm_set=self.ps2))
        self.assertFalse(self.example_simple_function_dne(perm_set=self.ps2))
        self.assertFalse(self.example_simple_function(perm_set=self.ps3))
        self.assertFalse(self.example_simple_function_dne(perm_set=self.ps3))
        self.assertTrue(self.example_simple_function(perm_set=self.ps4))
        self.assertTrue(self.example_simple_function_dne(perm_set=self.ps4))
        self.assertTrue(self.example_simple_function_2(perm_set=self.ps1))
        self.assertTrue(self.example_simple_function_2(perm_set=self.ps2))
        self.assertFalse(self.example_simple_function_2(perm_set=self.ps3))
        self.assertFalse(self.example_simple_function_2(perm_set=self.ps4))

if __name__ == "__main__":
    unittest.main()

