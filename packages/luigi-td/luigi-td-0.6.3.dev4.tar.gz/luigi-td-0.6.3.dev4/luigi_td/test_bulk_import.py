from bulk_import import BulkImportUploadContext
from bulk_import import BulkImportTarget
from bulk_import import BulkImportSession
from bulk_import import BulkImportUpload
from bulk_import import BulkImportPerform
from bulk_import import BulkImport
from test_helper import MockJob
from test_helper import TestConfig

from unittest import TestCase
from nose.tools import eq_, raises

import os
import shutil
import tempfile

test_config = TestConfig(
    bulk_imports = [
        {
            'session': 'session-1',
            'status': 'Uploading',
        },
        {
            'session': 'session-2',
            'status': 'Uploading',
            'frozen': True,
        },
        {
            'session': 'session-3',
            'status': 'Performing',
            'frozen': True,
        },
        {
            'session': 'session-4',
            'status': 'Ready',
            'frozen': True,
        },
        {
            'session': 'session-5',
            'status': 'Committing',
            'frozen': True,
        },
        {
            'session': 'session-6',
            'status': 'Committed',
            'frozen': True,
        },
    ]
)

class BulkImportUploadContextTestCase(TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_creates_temporary_environ(self):
        env = {'TEST_ENV': 'ok'}
        eq_(os.environ.get('TEST_ENV'), None)
        with BulkImportUploadContext(env):
            eq_(os.environ.get('TEST_ENV'), 'ok')
        eq_(os.environ.get('TEST_ENV'), None)

    def test_creates_directories(self):
        cur_dir = os.getcwd()
        log_dir = os.path.realpath(os.path.join(self.test_dir, 'log'))
        tmp_dir = os.path.realpath(os.path.join(self.test_dir, 'tmp'))
        with BulkImportUploadContext(log_dir=log_dir, tmp_dir=tmp_dir):
            eq_(os.getcwd(), log_dir)
            eq_(os.path.exists(log_dir), True)
            eq_(os.path.exists(tmp_dir), True)
        eq_(os.getcwd(), cur_dir)
        eq_(os.path.exists(log_dir), True)
        eq_(os.path.exists(tmp_dir), False)

class TestBulkImportTarget(BulkImportTarget):
    config = test_config

class BulkImportTargetTestCase(TestCase):
    def test_not_exists(self):
        target = TestBulkImportTarget('none')
        eq_(target.exists(), False)

    def test_exists(self):
        target = TestBulkImportTarget('session-1')
        eq_(target.exists(), True)

class BulkImportSessionTestCase(TestCase):
    pass

class BulkImportUploadTestCase(TestCase):
    pass

class BulkImportPerformTestCase(TestCase):
    pass

class BulkImportTestCase(TestCase):
    pass
