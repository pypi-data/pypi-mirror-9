import unittest

from pypermissions.permission import Permission
from pypermissions.templates import PermissionTemplate


class PermissionTemplateTests(unittest.TestCase):

    def setUp(self):
        self.p1 = Permission("test.1.*", description="Test permission for 1")
        self.p2 = Permission("test.2.hello", description="Test hello permission for 2")
        self.p3 = Permission("test")
        self.p4 = Permission("test.1.hello", description="Test hello permission for 1")
        self.p5 = Permission("test.1")
        self.p6 = Permission("test.2.*", description="Test permission for 2")
        self.p7 = Permission("test.*.hello", description="Test hello permission for *")
        self.t1 = PermissionTemplate(form="test.!.*", description="Test permission for {0}")
        self.t2 = PermissionTemplate(form="test.!.hello", description="Test hello permission for {0}")
        self.t3 = PermissionTemplate(form="test.!.!", description="Test {1} permission for {0}")

    def test_matches_format(self):
        # Test the permission matching
        self.assertTrue(self.t1.matches_format(self.p1)[0])
        self.assertTrue(self.t1.matches_format(self.p6)[0])
        self.assertFalse(self.t1.matches_format(self.p4)[0])
        self.assertFalse(self.t1.matches_format(self.p5)[0])
        self.assertTrue(self.t2.matches_format(self.p2)[0])
        self.assertTrue(self.t2.matches_format(self.p4)[0])
        self.assertTrue(self.t2.matches_format(self.p7)[0])
        self.assertFalse(self.t2.matches_format(self.p6)[0])
        self.assertTrue(self.t3.matches_format(self.p1)[0])
        self.assertTrue(self.t3.matches_format(self.p2)[0])
        self.assertFalse(self.t3.matches_format(self.p3)[0])
        self.assertTrue(self.t3.matches_format(self.p4)[0])
        self.assertFalse(self.t3.matches_format(self.p5)[0])
        self.assertTrue(self.t3.matches_format(self.p6)[0])
        self.assertTrue(self.t3.matches_format(self.p7)[0])

        # Test the segment matches
        self.assertEqual(self.t1.matches_format(self.p1)[1], ["1"])
        self.assertEqual(self.t1.matches_format(self.p6)[1], ["2"])
        self.assertEqual(self.t1.matches_format(self.p4)[1], list())
        self.assertEqual(self.t1.matches_format(self.p5)[1], list())
        self.assertEqual(self.t2.matches_format(self.p2)[1], ["2"])
        self.assertEqual(self.t2.matches_format(self.p4)[1], ["1"])
        self.assertEqual(self.t2.matches_format(self.p7)[1], ["*"])
        self.assertEqual(self.t2.matches_format(self.p6)[1], list())
        self.assertEqual(self.t3.matches_format(self.p1)[1], ["1", "*"])
        self.assertEqual(self.t3.matches_format(self.p2)[1], ["2", "hello"])
        self.assertEqual(self.t3.matches_format(self.p3)[1], list())
        self.assertEqual(self.t3.matches_format(self.p4)[1], ["1", "hello"])
        self.assertEqual(self.t3.matches_format(self.p5)[1], list())
        self.assertEqual(self.t3.matches_format(self.p6)[1], ["2", "*"])
        self.assertEqual(self.t3.matches_format(self.p7)[1], ["*", "hello"])

    def test_create_permission(self):
        self.assertEqual(self.t1.create_permission("test.1.*"), self.p1)
        self.assertFalse(self.t1.create_permission("test.2.hello"))
        self.assertEqual(self.t1.create_permission("test.2.*"), self.p6)
        self.assertFalse(self.t1.create_permission("test.1.hello"))
        self.assertEqual(self.t2.create_permission("test.2.hello"), self.p2)
        self.assertEqual(self.t2.create_permission("test.1.hello"), self.p4)
        self.assertFalse(self.t2.create_permission("test"))
        self.assertFalse(self.t2.create_permission("test.1.*"))
        self.assertNotEqual(self.t3.create_permission("test.1.*"), self.p1)
        self.assertEqual(self.t3.create_permission("test.2.hello"), self.p2)
        self.assertNotEqual(self.t3.create_permission("test.2.*"), self.p6)
        self.assertEqual(self.t3.create_permission("test.1.hello"), self.p4)


if __name__ == "__main__":
    unittest.main()



