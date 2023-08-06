#!/usr/bin/env python

# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
scheduler.py

Command script to run schduled table jobs according to
defined configuration.

The config file uses the ConfigParser format. For example:

    [job1]
    table-name=pypi-download-stats-alerts
    criteria=duration:1day, package:steelscript
    output-file=statsalerts.csv
    csv=
    interval_seconds=10

    [job2]
    ; comments are prefixed by a semi-colon
    table-name=appfwk-alerts
    criteria=duration:1hour
    interval_seconds=15

    [job3]
    table-name=appfwk-alerts
    ; you can interpolate other values via keywords
    criteria=duration:%(interval_minutes)sminutes
    interval_seconds=0
    interval_minutes=15

    [job4]
    table-name=appfwk-alerts
    criteria=duration:%(interval_minutes)sminutes
    interval_seconds=0
    interval_minutes=15
    ; offsets can be used to run reports further in the past
    offset=1min

Each section name (the line with sourrounding brackets) will
translate into a scheduled job name.  The key-value pairs include
parameters for the table command itself (e.g. 'table-name', 'criteria'),
and job configuration that gets handled by the scheduler
(e.g. 'interval_trigger', 'interval_seconds').  Note that job configuration
keys are all prefixed with 'interval_'.

"""

import os
import re
import sys
import time
import signal
import logging
import datetime
from urlparse import urljoin
from ConfigParser import SafeConfigParser

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
except ImportError:
    print 'This module requires an additional python module'
    print 'called "apscheduler", ensure this is installed and try again'
    sys.exit(1)

import pytz
import requests

from steelscript.common import timeutils
from steelscript.commands.steel import (BaseCommand, shell, console,
                                        MainFailed, ShellFailed)


logger = logging.getLogger(__name__)


def process_criteria(kws):
    """Process criteria options into separate dict."""
    # get runtime parameters
    interval = kws.pop('interval')

    if interval['offset'] > datetime.timedelta(0):
        # round now to nearest whole second
        now = datetime.datetime.now(pytz.UTC)
        roundnow = timeutils.round_time(now, round_to=1)

        endtime = roundnow - interval['offset']
        logger.debug('Setting end time to %s (via offset: %s)' %
                     (endtime, interval['offset']))
    else:
        endtime = None

    # if we have criteria, parse and append to base
    criteria = kws.pop('criteria', None)
    if criteria:
        crits = re.split(',\s|,', criteria)
        critdict = dict(c.split(':', 1) for c in crits)

        if endtime:
            critdict['endtime'] = endtime
    else:
        critdict = dict()

    kws['offset'] = interval['offset']
    kws['delta'] = interval['delta']

    return critdict, kws


def run_table(*args, **kwargs):
    # combine base arguments
    argstr = ' '.join(args)

    # split out criteria
    criteria, options = process_criteria(kwargs)
    critargs = ' '.join('--criteria=%s:%s' % (k, v)
                        for k, v in criteria.iteritems())
    argstr = '%s %s' % (argstr, critargs)

    # format remaining keyword args
    kws = []
    for k, v in kwargs.iteritems():
        if v.lower() in ('true', ''):
            # handle empty or True attrs as command-line flags
            kws.append('--%s' % k)
        else:
            kws.append('--%s=%s' % (k, v))

    kws = ' '.join(kws)

    cmd = 'python manage.py %s %s' % (argstr, kws)
    logger.debug('running command: %s' % cmd)

    try:
        results = shell(cmd, cwd=os.getcwd(), save_output=True,
                        allow_fail=False, exit_on_fail=False, log_output=False)
    except ShellFailed as e:
        logger.error('Error processing table.  Error code: %s, '
                     'stdout results: %s' % (e.returncode, e.output))


def get_auth(authfile):
    """Parse simple auth from given file."""
    with open(authfile, 'r') as f:
        return tuple(f.readline().strip().split(':'))


def run_table_via_rest(url, authfile, verify, **kwargs):
    criteria, options = process_criteria(kwargs)

    s = requests.session()
    s.auth = get_auth(authfile)
    s.headers.update({'Accept': 'application/json'})
    s.verify = verify

    logger.debug('POSTing new job with criteria: %s' % criteria)
    r = s.post(url, data=criteria)
    if r.ok:
        logger.debug('Job creation sucessful.')
    else:
        logger.error('Error creating Job: %s' % r.content)

    if options.get('output-file', None):
        # check periodically until data is ready and write to file
        url = r.headers['Location']
        timeout = options['delta']
        interval = 1

        complete = False
        error = False
        now = datetime.datetime.now
        start = now()

        while (now() - start) < timeout:
            status = s.get(url)

            if status.json()['status'] == 3:
                logger.debug("Table completed successfully.")
                complete = True
                break

            if status.json()['status'] == 4:
                logger.error('Table reported error in processing: %s' %
                             status.json())
                complete = True
                error = True
                break

            logger.debug("Table not yet complete, sleeping for 1 second.")
            time.sleep(interval)

        if not complete:
            logger.warning("Timed out waiting for table to complete,"
                           "url is: %s" % url)
        elif not error:
            # get data and write as CSV
            data = s.get(urljoin(url, 'data/'))
            d = data.json()['data']
            with open(options['output-file'], 'a') as f:
                for row in d:
                    f.write(','.join(str(x) for x in row))
                    f.write('\n')
    else:
        # we aren't interested in results
        pass


class Command(BaseCommand):
    help = 'Interface to schedule table operations.'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        # XXX SIGHUP not available on windows
        signal.signal(signal.SIGHUP, self.signal_handler)
        # graceful shutdown on Ctrl-C
        signal.signal(signal.SIGINT, self.signal_handler)

    def add_options(self, parser):
        super(Command, self).add_options(parser)
        parser.add_option('-c', '--config',
                          help='Config file to read schedule from')
        parser.add_option('-r', '--rest-server', action='store', default=None,
                          help='Run jobs against running App Framework '
                               'server using a REST API.')
        parser.add_option('--insecure', action='store_true', default=False,
                          help='Allow connections without verifying SSL certs')
        # storing auth as a file will avoid having the actual credentials
        # passed in via the commandline and viewable under 'ps'
        parser.add_option('--authfile', action='store', default=None,
                          help='Path to file containing authentication '
                               'to rest-server in format "user:password"')

    def validate_args(self):
        if self.options.rest_server and not self.options.authfile:
            console('Must specify an authfile to use with rest-server.')
            sys.exit(1)

        if self.options.authfile and not self.options.rest_server:
            console('Must specify a rest-server for use with an authfile.')
            sys.exit(1)

    def get_settings(self):
        # holdover for direct python call
        settings = os.path.join(os.getcwd(), 'local_settings.py')
        if os.path.exists(settings):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'local_settings')
            return settings
        else:
            raise MainFailed('Unable to find local_settings.py file')

    def get_job_function(self, kwargs):
        # allow for alternate methods to call table commands in future
        # possibly direct API calls, or REST calls against running server

        if self.options.rest_server:
            # find id of table-name
            name = kwargs['table-name']
            baseurl = self.options.rest_server + '/data/tables/'
            verify = not self.options.insecure

            s = requests.session()
            s.auth = get_auth(self.options.authfile)
            s.headers.update({'Accept': 'application/json'})
            s.verify = verify

            tableid = None
            url = baseurl
            while tableid is None:
                r = s.get(url)
                results = r.json()['results']
                ids = [t['id'] for t in results if t['name'] == name]
                if len(ids) > 1:
                    msg = 'Multiple tables found for name %s: %s' % (name, ids)
                    raise ValueError(msg)
                elif len(ids) == 1:
                    tableid = ids[0]
                else:
                    url = r.json()['next']
                    if url is None:
                        raise ValueError('No table found for name %s' % (name))

            tableurl = urljoin(baseurl, str(tableid) + '/jobs/')

            job_params = {'func': run_table_via_rest,
                          'args': [tableurl, self.options.authfile, verify]}
        else:
            job_params = {'func': run_table,
                          'args': ['table']}
        return job_params

    def parse_config(self, job_config):
        """Breaks up dict from config section into job and function options.

        Returns new dict suitable for passing to add_job, plus dict
        of interval definitions.
        """
        # pull job scheduler kwargs from job_config dict
        interval = dict()
        offset = timeutils.parse_timedelta(job_config.pop('offset', '0'))

        keys = job_config.keys()
        job_kwargs = dict((k[9:], job_config.pop(k))
                          for k in keys if k.startswith('interval_'))

        # convert time fields to floats, populate interval dict
        for v in ['weeks', 'days', 'hours', 'minutes', 'seconds']:
            if v in job_kwargs:
                val = float(job_kwargs[v])
                job_kwargs[v] = val
                interval[v] = val
        interval['delta'] = datetime.timedelta(**interval)
        interval['offset'] = offset

        # hardcode the function call - don't allow config overrides
        func_params = self.get_job_function(job_config)
        job_kwargs.update(func_params)

        # embed interval and add remaining kwargs as
        # actual kwargs for function call
        job_config['interval'] = interval
        job_kwargs['kwargs'] = job_config

        return job_kwargs, interval

    def schedule_job(self, name, job_config):
        job_options, interval = self.parse_config(job_config)

        if interval['offset'] > datetime.timedelta(0):
            delta = interval['delta']
            offset = interval['offset']
            now = datetime.datetime.now(pytz.UTC)

            # this gives the latest rounded time in the past
            # so we add interval to it to get a future run time
            total_offset = timeutils.timedelta_total_seconds(delta + offset)
            next_run_time = timeutils.round_time(now,
                                                 round_to=total_offset,
                                                 trim=True)
            next_run_time += (delta + offset)

            logger.debug('Setting next run time to %s (delta: %s, offset: %s)'
                         % (next_run_time, delta, offset))
            job_options['next_run_time'] = next_run_time

        logger.debug('Scheduling job named %s with kwargs: %s' % (name,
                                                                  job_options))
        self.scheduler.add_job(name=name, trigger='interval', **job_options)

    def schedule_jobs(self):
        for s in self.parser.sections():
            job = dict(self.parser.items(s))
            self.schedule_job(s, job)

    def reload_config(self):
        logger.debug('Reloading job schedule configuration.')
        result = self.parser.read(self.options.config)
        if result is None:
            raise ValueError('No valid configuration loaded.')

        logger.debug('Clearing existing jobs.')
        for j in self.scheduler.get_jobs():
            self.scheduler.remove_job(j.id)

        self.schedule_jobs()

    def signal_handler(self, signum, frame):
        if signum == signal.SIGHUP:
            console('Received signal %s, reloading config' % signum)
            self.reload_config()
        else:
            console('Received signal %s, shutting down gracefully.' % signum)
            if self.scheduler.running:
                self.scheduler.shutdown()
            sys.exit()

    def main(self):
        self.scheduler = BlockingScheduler()
        self.parser = SafeConfigParser()

        if not self.options.config:
            raise MainFailed('Config file required')

        self.reload_config()

        logger.debug('Starting scheduler.')
        self.scheduler.start()
