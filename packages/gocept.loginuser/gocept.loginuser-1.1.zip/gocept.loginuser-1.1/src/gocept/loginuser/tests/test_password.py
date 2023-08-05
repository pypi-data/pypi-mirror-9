import bcrypt
import hashlib
import unittest


class PasswordHashingTest(unittest.TestCase):

    def setUp(self):
        import gocept.loginuser.password
        import gocept.testing.patch
        self.patch = gocept.testing.patch.Patches()
        self.patch.set(gocept.loginuser.password, 'WORK_FACTOR', 4)

    def tearDown(self):
        self.patch.reset()

    def test_verifying_passwords(self):
        import gocept.loginuser.password
        hashed = gocept.loginuser.password.hash('mypassword')
        self.assertTrue(gocept.loginuser.password.check(
            'mypassword', hashed))
        self.assertFalse(gocept.loginuser.password.check(
            'invalid', hashed))

    def test_hash_accepts_and_returns_unicode(self):
        import gocept.loginuser.password
        hashed = gocept.loginuser.password.hash(u'mypassword')
        self.assertIsInstance(hashed, unicode)

    def test_sha256_password_is_recognised(self):
        import gocept.loginuser.password
        hashed = hashlib.sha256('asdf').hexdigest()
        self.assertTrue(gocept.loginuser.password.check(
            'asdf', 'sha256:' + hashed))

    def test_password_check_defaults_to_bcrypt(self):
        import gocept.loginuser.password
        hashed = bcrypt.hashpw('asdf', bcrypt.gensalt(12)).encode('utf8')
        self.assertTrue(gocept.loginuser.password.check(
            'asdf', hashed))
