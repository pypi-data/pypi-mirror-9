from luigi_td.config import get_config
from luigi_td.client import ResultProxy
from luigi_td.targets.result import ResultTarget
from luigi_td.targets.td import DatabaseTarget
from luigi_td.targets.td import TableTarget

import time
import luigi
import jinja2

import logging
logger = logging.getLogger('luigi-interface')

class DatabaseTask(luigi.Task):
    config = get_config()
    database_name = luigi.Parameter()
    action = luigi.Parameter(default='create')

    def output(self):
        return DatabaseTarget(self.database_name)

    def run(self):
        client = self.config.get_client()
        logger.debug('%s: creating database: %s', self, self.database_name)
        client.create_database(self.database_name)

class TableTask(luigi.Task):
    config = get_config()
    database_name = luigi.Parameter()
    table_name = luigi.Parameter()
    action = luigi.Parameter(default='create')
    schema = luigi.Parameter(is_list=True, default=[], significant=False)
    empty = luigi.BooleanParameter(default=False, significant=False)

    def requires(self):
        return DatabaseTask(self.database_name)

    def output(self):
        return TableTarget(self.database_name, self.table_name, self.schema, empty=self.empty)

    def run(self):
        client = self.config.get_client()
        logger.debug('%s: creating table: %s.%s', self, self.database_name, self.table_name)
        client.create_log_table(self.database_name, self.table_name)
        if self.schema != []:
            logger.debug('%s: updating schema for %s.%s', self, self.database_name, self.table_name)
            client.update_schema(self.database_name, self.table_name, [s.split(':') for s in self.schema])

# query

class Timeout(Exception):
    pass

class Query(luigi.Task):
    config = get_config()
    debug = False
    timeout = None
    type = 'hive'
    database = None
    source = None
    variables = {}

    def query(self):
        return NotImplemented()

    def load_query(self, source):
        env = jinja2.Environment(loader=jinja2.PackageLoader(self.__module__, '.'))
        template = env.get_template(source)
        return template.render(task=self, **self.variables)

    def run_query(self, query):
        result = self.output()
        result_url = None
        if isinstance(result, ResultTarget):
            result_url = result.get_result_url()
        client = self.config.get_client()
        job = client.query(self.database, 
                           query,
                           type = self.type,
                           result_url = result_url)
        job._update_status()
        logger.info("%s: td.job.url: %s", self, job.url)

        # wait for the result
        try:
            if self.timeout:
                timeout = time.time() + self.timeout
            else:
                timeout = None
            while not job.finished():
                if timeout and time.time() > timeout:
                    raise Timeout('{0} timed out'.format(self))
                time.sleep(2)
        except:
            # kill query on exceptions
            job.kill()
            raise
        job._update_status()

        logger.info("%s: td.job.result: job_id=%s status=%s", self, job.job_id, job.status())

        if not job.success():
            stderr = job._debug['stderr']
            if stderr:
                logger.error(stderr)
            raise RuntimeError("job {0} {1}\n\nOutput:\n{2}".format(job.job_id, job.status(), job._debug['cmdout']))

        return ResultProxy(job)

    def run(self):
        if hasattr(self, 'query_file'):
            self.source = self.query_file
        query = self.load_query(self.source) if self.source else self.query()
        result = self.run_query(query)
        target = self.output()
        if target and isinstance(target, ResultTarget):
            target.save_result_state(result)

        if self.debug:
            import pandas as pd
            TERMINAL_WIDTH = 120
            pd.options.display.width = TERMINAL_WIDTH
            print '-' * TERMINAL_WIDTH
            print 'Query result:'
            print result.to_dataframe()
            print '-' * TERMINAL_WIDTH
