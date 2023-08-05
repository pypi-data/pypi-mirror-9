import unittest

from pypermissions.permission import Permission
from pypermissions.factory import PermissionFactory
from pypermissions.templates import PermissionTemplate


class PermissionFactoryTests(unittest.TestCase):

    def setUp(self):
        self.rpf = PermissionFactory()
        self.tpf = PermissionFactory(prefix="test")
        self.t2pf = self.rpf.create_child("test")
        self.ttpf = self.t2pf.create_child("2")
        self.thpf = self.tpf.create_child("hello")
        self.twpf = self.tpf.create_child("*")
        self.p1 = Permission("test.1.hello")
        self.p2 = Permission("test.2.hello")
        self.p3 = Permission("test")
        self.p4 = Permission("test.1.hello")
        self.p5 = Permission("test.*")

        self.tp1 = Permission("test.1.*", description="Test permission for 1")
        self.tp2 = Permission("test.2.hello", description="Test hello permission for 2")
        self.tp3 = Permission("test")
        self.tp4 = Permission("test.1.hello", description="Test hello permission for 1")
        self.tp5 = Permission("test.1")
        self.tp6 = Permission("test.2.*", description="Test permission for 2")
        self.tp7 = Permission("test.*.hello", description="Test hello permission for *")
        self.t1 = PermissionTemplate(form="test.!.*", description="Test permission for {0}")
        self.t2 = PermissionTemplate(form="test.!.hello", description="Test hello permission for {0}")
        self.t3 = PermissionTemplate(form="test.!.!", description="Test {1} permission for {0}")

        self.trpf = PermissionFactory()
        self.tqtpf = PermissionFactory(prefix="test")

        self.trpf.register_template(self.t1)
        self.trpf.register_template(self.t2)
        self.trpf.register_template(self.t3)
        self.tqtpf.register_template(self.t1)
        self.tqtpf.register_template(self.t2)
        self.tqtpf.register_template(self.t3)

        self.tt2pf = self.trpf.create_child("test")
        self.tttpf = self.tt2pf.create_child("2")
        self.tthpf = self.tqtpf.create_child("hello")
        self.ttwpf = self.tqtpf.create_child("*")

    def test_equal(self):
        self.assertEqual(self.p1, self.rpf.create_permission("test.1.hello"))
        self.assertNotEqual(self.p1, self.rpf.create_permission("test.2.hello"))
        self.assertEqual(self.p2, self.ttpf.create_permission("hello"))
        self.assertEqual(self.p2, self.tpf.create_permission("2.hello"))
        self.assertNotEqual(self.p5, self.twpf.create_permission(""))
        self.assertEqual(self.tpf, self.t2pf)
        self.assertNotEqual(self.tpf, self.ttpf)

        self.assertEqual(self.tp4, self.trpf.create_permission("test.1.hello"))
        self.assertNotEqual(self.tp4, self.trpf.create_permission("test.2.hello"))
        self.assertEqual(self.tp2, self.tttpf.create_permission("hello"))
        self.assertEqual(self.tp2, self.tqtpf.create_permission("2.hello"))
        self.assertEqual(self.tqtpf, self.tt2pf)
        self.assertNotEqual(self.tqtpf, self.tttpf)
        self.assertEqual(self.tp1, self.tqtpf.create_permission("1.*"))
        self.assertNotEqual(self.tp2, self.rpf.create_permission("test.2.hello"))
        self.assertEqual(self.tp4, self.tt2pf.create_permission("1.hello"))
        self.assertEqual(self.tp4, self.trpf.create_permission("test.1.hello"))
        self.assertEqual(self.tp6, self.tqtpf.create_permission("2.*"))
        self.assertEqual(self.tp6, self.tttpf.create_permission("*"))
        self.assertEqual(self.tp7, self.tqtpf.create_permission("*.hello"))
        self.assertEqual(self.tp7, self.ttwpf.create_permission("hello"))

if __name__ == "__main__":
    unittest.main()



