import unittest

from pypermissions.permission import Permission


class BasicPermissionTests(unittest.TestCase):

    def setUp(self):
        self.p1 = Permission("test.1.hello")
        self.p2 = Permission("test.2.hello")
        self.p3 = Permission("test")
        self.p4 = Permission("test.1.hello")
        self.ps1 = {self.p1, self.p2}
        self.ps2 = {self.p1, self.p4}
        self.ps3 = {self.p1}

        self.wp1 = Permission("test.1.*")
        self.wp2 = Permission("test.2.hello")
        self.wp3 = Permission("test")
        self.wp4 = Permission("test.1.*")
        self.wp5 = Permission("test.1.goodbye")
        self.wp6 = Permission("test.1")
        self.wp7 = Permission("*")
        self.wp8 = Permission("test.*.hello")

    def test_equal(self):
        self.assertEqual(self.p1, self.p4)
        self.assertNotEqual(self.p1, self.p2)
        self.assertNotEqual(self.p1, self.p3)
        self.assertEqual(self.ps2, self.ps3)

    def test_grants_permission(self):
        self.assertTrue(self.p1.grants_permission(self.p1))
        self.assertTrue(self.p1.grants_permission(self.p4))
        self.assertFalse(self.p1.grants_permission(self.p2))
        self.assertFalse(self.p1.grants_permission(self.p3))
        self.assertFalse(self.p3.grants_permission(self.p1))

        self.assertTrue(self.wp1.grants_permission(self.wp1))
        self.assertTrue(self.wp1.grants_permission(self.wp4))
        self.assertFalse(self.wp1.grants_permission(self.wp2))
        self.assertFalse(self.wp1.grants_permission(self.wp3))
        self.assertFalse(self.wp3.grants_permission(self.wp1))
        self.assertTrue(self.wp1.grants_permission(self.wp5))
        self.assertFalse(self.wp1.grants_permission(self.wp6))
        self.assertTrue(self.wp7.grants_permission(self.wp1))
        self.assertTrue(self.wp7.grants_permission(self.wp2))
        self.assertTrue(self.wp7.grants_permission(self.wp3))
        self.assertTrue(self.wp7.grants_permission(self.wp4))
        self.assertTrue(self.wp7.grants_permission(self.wp5))
        self.assertTrue(self.wp7.grants_permission(self.wp6))
        self.assertTrue(self.wp8.grants_permission(self.wp2))
        self.assertFalse(self.wp8.grants_permission(self.wp1))

    def test_grants_any_permission(self):
        self.assertTrue(self.p1.grants_any_permission(self.ps1))
        self.assertTrue(self.p2.grants_any_permission(self.ps1))
        self.assertFalse(self.p3.grants_any_permission(self.ps1))
        self.assertTrue(self.p4.grants_any_permission(self.ps1))

    def test_segments(self):
        self.assertEqual(self.p1.segments, ["test", "1", "hello"])
        self.assertEqual(self.p2.segments, ["test", "2", "hello"])
        self.assertEqual(self.p3.segments, ["test"])
        self.assertEqual(self.p1.segments, self.p4.segments)

    def test_is_end_wildcard(self):
        self.assertTrue(self.wp1.is_end_wildcard)
        self.assertTrue(self.wp4.is_end_wildcard)
        self.assertTrue(self.wp7.is_end_wildcard)
        self.assertFalse(self.wp8.is_end_wildcard)
        self.assertFalse(self.p1.is_end_wildcard)
        self.assertFalse(self.p2.is_end_wildcard)
        self.assertFalse(self.p3.is_end_wildcard)
        self.assertFalse(self.p4.is_end_wildcard)

    def test_is_wildcard(self):
        self.assertTrue(self.wp1.is_wildcard)
        self.assertTrue(self.wp4.is_wildcard)
        self.assertTrue(self.wp7.is_wildcard)
        self.assertTrue(self.wp8.is_wildcard)
        self.assertFalse(self.p1.is_wildcard)
        self.assertFalse(self.p2.is_wildcard)
        self.assertFalse(self.p3.is_wildcard)
        self.assertFalse(self.p4.is_wildcard)

if __name__ == "__main__":
    unittest.main()




