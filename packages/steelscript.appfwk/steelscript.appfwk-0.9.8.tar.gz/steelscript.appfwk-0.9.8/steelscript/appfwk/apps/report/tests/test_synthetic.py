# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import logging

from django.conf import settings
import pytz

from steelscript.appfwk.apps.datasource.models import Job
from steelscript.appfwk.apps.preferences.models import PortalUser
from steelscript.appfwk.apps.report.tests import reportrunner

logger = logging.getLogger(__name__)


class SyntheticTest(reportrunner.ReportRunnerTestCase):

    def setUp(self):
        super(SyntheticTest, self).setUp()
        self.assertEqual(settings.TIME_ZONE, 'UTC')

    def run_with_criteria(self, criteria, expected):

        widgets = self.run_report(criteria)

        for i, e in enumerate(expected):
            w = widgets.values()[i]
            self.assertEqual(w['status'], Job.COMPLETE,
                             'Widget %d, message %s' % (i, w['message']))

            data = dict(w['data'])
            logger.debug("Widget %d, data: %s" % (i, data))
            logger.debug("Expected: %s" % expected)
            self.assertEqual(len(data), len(e))

            #from IPython import embed; embed()
            for k, v in e.iteritems():
                self.assertEqual(data[k], v,
                                 "Time %s => %s vs %s" %
                                 (k, v, data[k]))

    def make_data(self, t0, t1, delta):
        data = {}
        value = delta / 60

        if (t0 % delta) != 0:
            data[t0-(t0%delta)] = ((delta - (t0 % delta)) / 60)
            t0 = t0-(t0%delta) + delta

        for t in range(t0, t1, delta):
            if t + delta <= t1:
                data[t] = value
            else:
                data[t] = (t1 % delta) / 60

        return data


class NoResample(SyntheticTest):

    report = 'synthetic_noresample'

    def test_basic(self):
        self.run_with_criteria({'endtime_0': '12/1/2013',
                                'endtime_1': '11:00 am',
                                'duration': '15min'},
                               # 11 AM UTC
                               [self.make_data(1385894700, 1385895600, 60)])

    def test_eastern_timezone(self):
        user = PortalUser.objects.get(username='admin')
        tz = user.timezone
        user.timezone = pytz.timezone('US/Eastern')
        user.save()
        self.run_with_criteria({'endtime_0': '12/1/2013',
                                'endtime_1': '11:00 am',
                                'duration': '15min'},
                               # 11 AM EDT
                               [self.make_data(1385912700, 1385913600, 60)])
        user.timezone = tz
        user.save()

    def test_pacific_timezone(self):
        user = PortalUser.objects.get(username='admin')
        tz = user.timezone
        user.timezone = pytz.timezone('US/Pacific')
        user.save()
        self.run_with_criteria({'endtime_0': '12/1/2013',
                                'endtime_1': '11:00 am',
                                'duration': '15min'},
                               # 11 AM Pacific
                               [self.make_data(1385923500, 1385924400, 60)])
        user.timezone = tz
        user.save()


class Resample(SyntheticTest):

    report = 'synthetic_resample'

    def test_basic(self):
        self.run_with_criteria({'endtime_0': '12/1/2013',
                                'endtime_1': '11:00 am',
                                'duration': '15min',
                                'resolution': '2min'},
                               [self.make_data(1385894700, 1385895600, 120)])

        self.run_with_criteria({'endtime_0': '12/1/2013',
                                'endtime_1': '11:01 am',
                                'duration': '16min',
                                'resolution': '2min'},
                               [self.make_data(1385894700, 1385895660, 120)])

        self.run_with_criteria({'endtime_0': '12/1/2013',
                                'endtime_1': '11:01 am',
                                'duration': '15min',
                                'resolution': '2min'},
                               [self.make_data(1385894760, 1385895660, 120)])

        self.run_with_criteria({'endtime_0': '12/1/2013',
                                'endtime_1': '11:01 am',
                                'duration': '16min',
                                'resolution': '2min'},
                               [self.make_data(1385894700, 1385895660, 120)])

    def test_eastern_timezone(self):
        user = PortalUser.objects.get(username='admin')
        tz = user.timezone
        user.timezone = pytz.timezone('US/Eastern')
        user.save()
        self.run_with_criteria({'endtime_0': '12/1/2013',
                                'endtime_1': '11:00 am',
                                'duration': '15min', 'resolution': '2min'},
                               # 11 AM EDT
                               [self.make_data(1385912700, 1385913600, 120)])
        user.timezone = tz
        user.save()

    def test_pacific_timezone(self):
        user = PortalUser.objects.get(username='admin')
        tz = user.timezone
        user.timezone = pytz.timezone('US/Pacific')
        user.save()
        self.run_with_criteria({'endtime_0': '12/1/2013',
                                'endtime_1': '11:00 am',
                                'duration': '15min', 'resolution': '2min'},
                               # 11 AM Pacific
                               [self.make_data(1385923500, 1385924400, 120)])
        user.timezone = tz
        user.save()
