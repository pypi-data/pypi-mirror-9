from config import get_config

import collections
import json
import os
import subprocess
import shutil
import tempfile
import time
import urlparse
import luigi
import luigi.s3
import tdclient

import logging
logger = logging.getLogger('luigi-interface')

class BulkImportUploadContext(object):
    def __init__(self, env, log_dir='log', tmp_dir='tmp'):
        self.env = env
        self.cur_dir = os.getcwd()
        self.cur_env = os.environ.copy()
        self.log_dir = log_dir
        self.tmp_dir = tmp_dir

    def __enter__(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        os.chdir(self.log_dir)
        os.environ.update(self.env)
        return self

    def __exit__(self, type, value, tb):
        os.environ.clear()
        os.environ.update(self.cur_env)
        os.chdir(self.cur_dir)
        shutil.rmtree(self.tmp_dir)

class BulkImportTarget(luigi.Target):
    config = get_config()

    def __init__(self, session_id):
        self._session_id = session_id
        self._session = None

    def session(self):
        if not self._session:
            try:
                client = self.config.get_client()
                self._session = client.bulk_import(self._session_id)
            except tdclient.api.NotFoundError:
                self._session = None
        return self._session

    def exists(self):
        return self.session() != None

class BulkImportSession(luigi.Task):
    config = get_config()
    session = luigi.Parameter()
    options = luigi.Parameter(significant=False)

    def output(self):
        return BulkImportTarget(self.session)

    def run(self):
        options = json.loads(self.options)
        client = self.config.get_client()
        client.create_bulk_import(self.session, options['database'], options['table'])

class BulkImportUpload(luigi.Task):
    config = get_config()
    session = luigi.Parameter()
    options = luigi.Parameter(significant=False)

    def requires(self):
        return BulkImportSession(self.session, options=self.options)

    def complete(self):
        client = self.config.get_client()
        try:
            session = client.bulk_import(self.session)
        except tdclient.api.NotFoundError:
            return False
        else:
            return session.upload_frozen

    @property
    def log_dir(self):
        luigi_config = luigi.configuration.get_config()
        return os.path.abspath(os.path.join(luigi_config.get('td', 'log-dir', 'log'), self.session))

    @property
    def tmp_dir(self):
        luigi_config = luigi.configuration.get_config()
        return os.path.abspath(os.path.join(luigi_config.get('td', 'tmp-dir', 'tmp'), self.session))

    def full_path(self):
        options = json.loads(self.options)
        return [options['path']]

    def run_upload(self):
        options = json.loads(self.options)
        args = [
            'td',
            '-e', self.config.endpoint,
            '-k', self.config.apikey,
            'import:upload',
            self.session,
            '--format', 'csv',
            '--output', os.path.join(self.tmp_dir, 'parts'),
            '--error-records-output', os.path.join(self.log_dir, 'error-records'),
            '--time-column', options['time_column'],
            '--time-format', options['time_format'],
            '--encoding', 'utf-8',
            '--prepare-parallel', '8',
            '--parallel', '8',
            '--columns', ','.join([c.split(':')[0] for c in options['columns']]),
            '--column-types', ','.join([c.split(':')[1] for c in options['columns']]),
            # '--error-records-handling', 'abort',
            '--empty-as-null-if-numeric',
        ]
        if options['column_header']:
            args += ['--column-header']
        args += self.full_path()
        env = {}
        env['TD_TOOLBELT_JAR_UPDATE'] = '0'
        if options['default_timezone']:
            env['TZ'] = options['default_timezone']
        with BulkImportUploadContext(env, log_dir=self.log_dir, tmp_dir=self.tmp_dir):
            logger.debug(' '.join(args))
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                raise RuntimeError(err)

    def run(self):
        self.run_upload()
        client = self.config.get_client()
        client.freeze_bulk_import(self.session)

class BulkImportPerform(luigi.Task):
    config = get_config()
    session = luigi.Parameter()
    options = luigi.Parameter(significant=False)

    def requires(self):
        return BulkImportUpload(self.session, options=self.options)

    def complete(self):
        client = self.config.get_client()
        try:
            session = client.bulk_import(self.session)
        except tdclient.api.NotFoundError:
            return False
        else:
            return session.status == 'ready'

    def run(self):
        client = self.config.get_client()
        session = client.bulk_import(self.session)
        if session.status == 'uploading':
            job = client.perform_bulk_import(self.session)
        else:
            job = client.job(session.job_id)
        logger.info("%s: performing...", self)
        while not job.finished():
            time.sleep(2)

class BulkImport(luigi.Task):
    config = get_config()
    session = luigi.Parameter()
    database = luigi.Parameter(significant=False)
    table = luigi.Parameter(significant=False)
    format = luigi.Parameter(significant=False, default='csv')
    columns = luigi.Parameter(significant=False)
    time_column = luigi.Parameter(significant=False)
    time_format = luigi.Parameter(significant=False)
    default_timezone = luigi.Parameter(significant=False)
    # CSV/TSV options
    column_header = luigi.BooleanParameter(significant=False, default=False)

    def complete(self):
        client = self.config.get_client()
        try:
            session = client.bulk_import(self.session)
        except tdclient.api.NotFoundError:
            return False
        else:
            return session.status == 'committed'

    def get_path(self):
        target = self.input()
        # LocalTarget
        if isinstance(target, luigi.LocalTarget):
            return os.path.abspath(target.path)
        # S3Target
        if isinstance(target, luigi.s3.S3Target):
            url = urlparse.urlparse(target.path)
            luigi_config = luigi.configuration.get_config()
            return "s3://{aws_access_key_id}:{aws_secret_access_key}@/{bucket}{path}".format(
                aws_access_key_id = luigi_config.get('s3', 'aws_access_key_id', os.environ.get('AWS_ACCESS_KEY_ID')),
                aws_secret_access_key = luigi_config.get('s3', 'aws_secret_access_key', os.environ.get('AWS_SECRET_ACCESS_KEY')),
                bucket = url.hostname,
                path = url.path
            )
        raise ValueError('unsupported target: {0}'.format(target))

    def run(self):
        options = {
            'database': self.database,
            'table': self.table,
            'path': self.get_path(),
            'format': self.format,
            'columns': self.columns,
            'time_column': self.time_column,
            'time_format': self.time_format,
            'default_timezone': self.default_timezone,
            'column_header': self.column_header,
        }

        # upload and perform
        yield BulkImportPerform(self.session, options=json.dumps(options))

        # commit
        client = self.config.get_client()
        client.commit_bulk_import(self.session)
