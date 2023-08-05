import unittest

from pypermissions.permission import Permission, DynamicPermission
from pypermissions.templates import PermissionTemplate
from pypermissions.factory import PermissionFactory


class TestLessThanPermission(DynamicPermission):
    templates = [PermissionTemplate(form="test.hello.!")]

    def __init__(self, *args, **kw):
        super(TestLessThanPermission, self).__init__(*args, **kw)

        self.x = self.segments[3]

    def _grants_permission(self, components, template):
        if components[0] < self.x:
            return True
        return False


class BasicPermissionTests(unittest.TestCase):

    def setUp(self):
        self.p1 = Permission("test.hello.1")
        self.p2 = Permission("test.hello.2")
        self.p3 = Permission("test.hello.3")
        self.dp1 = TestLessThanPermission("test.hello.less.3")
        self.dp2 = TestLessThanPermission("test.hello.less.4")
        self.t = PermissionTemplate(form="test.hello.less.!", cls=TestLessThanPermission)
        self.dp3 = self.t.create_permission("test.hello.less.3")
        self.dp4 = self.t.create_permission("test.hello.less.4")
        self.pf = PermissionFactory(prefix="test.hello", templates=[self.t])
        self.dp5 = self.pf.create_permission("less.3")
        self.dp6 = self.pf.create_permission("less.4")

    def test_grants_permission(self):
        self.assertTrue(self.dp1.grants_permission(self.p1))
        self.assertTrue(self.dp1.grants_permission(self.p2))
        self.assertFalse(self.dp1.grants_permission(self.p3))
        self.assertTrue(self.dp2.grants_permission(self.p1))
        self.assertTrue(self.dp2.grants_permission(self.p2))
        self.assertTrue(self.dp2.grants_permission(self.p3))

    def test_equals(self):
        self.assertEqual(self.dp1, self.dp3)
        self.assertEqual(self.dp1, self.dp5)
        self.assertEqual(self.dp2, self.dp4)
        self.assertEqual(self.dp2, self.dp6)

if __name__ == "__main__":
    unittest.main()




