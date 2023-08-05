#-*- encoding: utf-8 -*-
"""
leap/email/imap/tests/__init__.py
----------------------------------
Module intialization file for leap.mx.tests, a module containing unittesting
code, using twisted.trial, for testing leap_mx.

@authors: Kali Kaneko, <kali@leap.se>
@license: GPLv3, see included LICENSE file
@copyright: © 2013 Kali Kaneko, see COPYLEFT file
"""

__all__ = ['test_imap']


def run():
    """xxx fill me in"""
    pass

import os
import u1db

from leap.common.testing.basetest import BaseLeapTest

from leap.soledad.client import Soledad
from leap.soledad.common.document import SoledadDocument


#-----------------------------------------------------------------------------
# Some tests inherit from BaseSoledadTest in order to have a working Soledad
# instance in each test.
#-----------------------------------------------------------------------------

class BaseSoledadIMAPTest(BaseLeapTest):
    """
    Instantiates GPG and Soledad for usage in LeapIMAPServer tests.
    Copied from BaseSoledadTest, but moving setup to classmethod
    """

    def setUp(self):
        # open test dbs
        self.db1_file = os.path.join(
            self.tempdir, "db1.u1db")
        self.db2_file = os.path.join(
            self.tempdir, "db2.u1db")

        self._db1 = u1db.open(self.db1_file, create=True,
                              document_factory=SoledadDocument)
        self._db2 = u1db.open(self.db2_file, create=True,
                              document_factory=SoledadDocument)

        # soledad config info
        self.email = 'leap@leap.se'
        secrets_path = os.path.join(
            self.tempdir, Soledad.STORAGE_SECRETS_FILE_NAME)
        local_db_path = os.path.join(
            self.tempdir, Soledad.LOCAL_DATABASE_FILE_NAME)
        server_url = ''
        cert_file = None

        self._soledad = self._soledad_instance(
            self.email, '123',
            secrets_path=secrets_path,
            local_db_path=local_db_path,
            server_url=server_url,
            cert_file=cert_file)

    def _soledad_instance(self, uuid, passphrase, secrets_path, local_db_path,
                          server_url, cert_file):
        """
        Return a Soledad instance for tests.
        """
        # mock key fetching and storing so Soledad doesn't fail when trying to
        # reach the server.
        Soledad._fetch_keys_from_shared_db = Mock(return_value=None)
        Soledad._assert_keys_in_shared_db = Mock(return_value=None)

        # instantiate soledad
        def _put_doc_side_effect(doc):
            self._doc_put = doc

        class MockSharedDB(object):

            get_doc = Mock(return_value=None)
            put_doc = Mock(side_effect=_put_doc_side_effect)

            def __call__(self):
                return self

        Soledad._shared_db = MockSharedDB()

        return Soledad(
            uuid,
            passphrase,
            secrets_path=secrets_path,
            local_db_path=local_db_path,
            server_url=server_url,
            cert_file=cert_file,
        )

    def tearDown(self):
        self._db1.close()
        self._db2.close()
        self._soledad.close()


# Key material for testing
KEY_FINGERPRINT = "E36E738D69173C13D709E44F2F455E2824D18DDF"
PUBLIC_KEY = """
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.10 (GNU/Linux)

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
=MuOY
-----END PGP PUBLIC KEY BLOCK-----
"""
PRIVATE_KEY = """
-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: GnuPG v1.4.10 (GNU/Linux)

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
=JTFu
-----END PGP PRIVATE KEY BLOCK-----
"""
