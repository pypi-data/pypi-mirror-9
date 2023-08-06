# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import re
import copy
import logging
import datetime

import pytz
import pandas
from django import forms

from steelscript.common.timeutils import timedelta_total_seconds
from steelscript.appfwk.apps.datasource.forms import fields_add_time_selection
from steelscript.appfwk.apps.datasource.models import \
    Job, Table, TableField, BatchJobRunner
from steelscript.appfwk.apps.datasource.modules.analysis import \
    AnalysisException, AnalysisTable, AnalysisQuery


logger = logging.getLogger(__name__)


TIMES = (['12:00am'] +
         ['%d:00am' % h for h in range(1, 12)] +
         ['12:00pm'] +
         ['%d:00pm' % h for h in range(1, 12)])


def parse_time(t_str):
    m = re.match("^([0-9]+):([0-9][0-9]) *([aApP][mM]?)?$", t_str)
    if not m:
        raise ValueError("Could not parse time string: %s" % t_str)
    hours = int(m.group(1))
    minutes = int(m.group(2))
    ampm = m.group(3)
    if ampm:
        if ampm.lower()[0] == 'p':
            hours += 12
    return datetime.time(hours, minutes, 0)


def replace_time(dt, t, tz):
    # Need to strip off the tzinfo, change the hours/minutes
    # then re-localize to the requested timezone
    # This ensures DST is handled properly
    return tz.localize(dt.replace(hour=t.hour,
                                  minute=t.minute,
                                  second=0,
                                  microsecond=0,
                                  tzinfo=None))


def fields_add_business_hour_fields(obj,
                                    initial_biz_hours_start='8:00am',
                                    initial_biz_hours_end='5:00pm',
                                    initial_biz_hours_tzname='US/Eastern',
                                    initial_biz_hours_weekends=False,
                                    **kwargs):

    kwargs['initial_duration'] = kwargs.get('initial_duration', '1w')
    fields_add_time_selection(obj, show_start=True, **kwargs)

    time_choices = {'choices': zip(TIMES, TIMES)}
    business_hours_start = TableField(keyword='business_hours_start',
                                      label='Start Business',
                                      initial=initial_biz_hours_start,
                                      field_cls=forms.ChoiceField,
                                      field_kwargs=time_choices,
                                      required=True)
    business_hours_start.save()
    obj.fields.add(business_hours_start)

    business_hours_end = TableField(keyword='business_hours_end',
                                    label='End Business',
                                    initial=initial_biz_hours_end,
                                    field_cls=forms.ChoiceField,
                                    field_kwargs=time_choices,
                                    required=True)
    business_hours_end.save()
    obj.fields.add(business_hours_end)

    tz_choices = {'choices': zip(pytz.common_timezones,
                                 pytz.common_timezones)}
    business_hours_tzname = TableField(keyword='business_hours_tzname',
                                       label='Business Timezone',
                                       initial=initial_biz_hours_tzname,
                                       field_cls=forms.ChoiceField,
                                       field_kwargs=tz_choices,
                                       required=True)
    business_hours_tzname.save()
    obj.fields.add(business_hours_tzname)

    business_hours_weekends = TableField(keyword='business_hours_weekends',
                                         field_cls=forms.BooleanField,
                                         label='Business includes weekends',
                                         initial=initial_biz_hours_weekends,
                                         required=False)
    business_hours_weekends.save()
    obj.fields.add(business_hours_weekends)


def get_timestable(biztable):
    return Table.from_ref(biztable.options.tables['times'])


class BusinessHoursTimesTable(AnalysisTable):

    class Meta:
        proxy = True

    _query_class = 'BusinessHoursTimesQuery'

    def post_process_table(self, field_options):
        super(BusinessHoursTimesTable, self).post_process_table(field_options)

        self.add_column('starttime', 'Start time', datatype='time',
                        iskey=True, sortasc=True)
        self.add_column('endtime',   'End time', datatype='time', iskey=True)
        self.add_column('totalsecs', 'Total secs')
        fields_add_business_hour_fields(self)


class BusinessHoursTimesQuery(AnalysisQuery):

    def post_run(self):
        criteria = self.job.criteria

        tzname = criteria.business_hours_tzname
        logger.debug("%s: timezone: %s" % (self.job, tzname))
        tz = pytz.timezone(tzname)

        # Convert to datetime objects in the requested timezone
        st = criteria.starttime.astimezone(tz)
        et = criteria.endtime.astimezone(tz)
        logger.debug("%s: times: %s - %s" % (self.job, st, et))

        # Business hours start/end, as string "HH:MMam" like 8:00am
        sb = parse_time(criteria.business_hours_start)
        eb = parse_time(criteria.business_hours_end)

        weekends = criteria.business_hours_weekends

        # Iterate from st to et until
        times = []
        t = st
        while t <= et:
            # Set t0/t1 to date of t but time of sb/eb
            t0 = replace_time(t, sb, tz)
            t1 = replace_time(t, eb, tz)

            # Advance t by 1 day
            t = t + datetime.timedelta(days=1)
            # Strip timezone, then re-add to account for DST
            t = tz.localize(t.replace(tzinfo=None))

            # Skip weekends
            if not weekends and t0.weekday() >= 5:
                continue

            # Now see if we have any overlap of biz hours for today
            if et < t0:
                # Report end time is today before biz hours start, all done
                break

            if et < t1:
                # Report end time is today in the middle of biz hours, adjust
                t1 = et

            if t1 < st:
                # Report start time occurs today *after* biz end, nothing today
                continue

            if t0 < st:
                # Report start time occurs today in the middle of the biz hours
                # Adjust t0
                t0 = st

            logger.debug("%s: start: %s, end: %s, duration: %s" %
                         (self.job, str(t0), str(t1),
                          str(timedelta_total_seconds(t1-t0))))
            times.append((t0, t1, timedelta_total_seconds(t1-t0)))

        if len(times) == 0:
            self.data = None
        else:
            # manually assign data types to avoid Python 2.6 issues
            # when converting date times
            columns = ['starttime', 'endtime', 'totalsecs']
            s1 = pandas.Series([x[0] for x in times], dtype='datetime64[ns]')
            s2 = pandas.Series([x[1] for x in times], dtype='datetime64[ns]')
            tt = pandas.Series([x[2] for x in times], dtype='int')

            # create dataframe then assign using correct column ordering
            df = pandas.DataFrame(dict(zip(columns, [s1, s2, tt])))
            self.data = df[columns]

        return True


class BusinessHoursTable(AnalysisTable):

    class Meta:
        proxy = True

    _query_class = 'BusinessHoursQuery'

    TABLE_OPTIONS = {'aggregate': None}

    @classmethod
    def create(cls, name, basetable, aggregate, **kwargs):
        timestable = BusinessHoursTimesTable.create(name + '-times')
        kwargs['tables'] = {'times': timestable}
        kwargs['related_tables'] = {'basetable': basetable}
        kwargs['aggregate'] = aggregate
        return super(BusinessHoursTable, cls).create(name, **kwargs)

    def post_process_table(self, field_options):
        super(BusinessHoursTable, self).post_process_table(field_options)

        self.copy_columns(self.options['related_tables']['basetable'])
        for col in self.get_columns(synthetic=True):
            col.synthetic = False
            col.compute_expression = ''
            col.save()


class BusinessHoursQuery(AnalysisQuery):

    def post_run(self):
        criteria = self.job.criteria

        tzname = criteria.business_hours_tzname
        tz = pytz.timezone(tzname)

        times = self.tables['times']

        if times is None or len(times) == 0:
            self.data = None
            return True

        basetable = Table.from_ref(
            self.table.options.related_tables['basetable']
        )

        # Create all the jobs
        batch = BatchJobRunner(self)
        for i, row in times.iterrows():
            (t0, t1) = (row['starttime'], row['endtime'])
            sub_criteria = copy.copy(criteria)
            sub_criteria.starttime = t0.astimezone(tz)
            sub_criteria.endtime = t1.astimezone(tz)

            job = Job.create(table=basetable, criteria=sub_criteria,
                             update_progress=False)

            logger.debug("Created %s: %s - %s" % (job, t0, t1))
            batch.add_job(job)

        if len(batch.jobs) == 0:
            self.data = None
            return True

        # Run all the Jobs
        batch.run()

        # collect all key names
        keynames = []
        istime = False
        for key in basetable.get_columns(iskey=True):
            keynames.append(key.name)
            if key.istime():
                istime = True

        # Now collect the data
        total_secs = 0
        dfs = []
        idx = 0
        for job in batch.jobs:
            if job.status == Job.ERROR:
                raise AnalysisException("%s for %s-%s failed: %s" %
                                        (job, job.criteria.starttime,
                                         job.criteria.endtime,
                                         job.message))
            subdf = job.data()
            logger.debug("%s: returned %d rows" %
                         (job, len(subdf) if subdf is not None else 0))
            if subdf is None:
                continue

            logger.debug("%s: actual_criteria %s" % (job, job.actual_criteria))
            t0 = job.actual_criteria.starttime
            t1 = job.actual_criteria.endtime
            if not istime:
                subdf['__secs__'] = timedelta_total_seconds(t1 - t0)
            total_secs += timedelta_total_seconds(t1 - t0)
            idx += 1
            dfs.append(subdf)

        if len(dfs) == 0:
            self.data = None
            return True

        df = pandas.concat(dfs, ignore_index=True)
        if not istime:
            if 'aggregate' in self.table.options:
                ops = self.table.options['aggregate']
                for col in basetable.get_columns(iskey=False):
                    if col.name not in ops:
                        ops[col.name] = 'sum'

            else:
                ops = 'sum'

            df = avg_groupby_aggregate(df, keynames, ops,
                                       '__secs__', total_secs)

        self.data = df
        return True


def avg_groupby_aggregate(df, keys, ops, t_col, total_t):
    """Groupby/aggregate with support for weighted averge column

    Group the data frame `df` on `keys` using the operation dict
    defined in `ops` just like the standard `df.aggregate(ops)`
    call, but support a `avg` operation that computes a
    weighted average using `weight_col` as the weight.

    This is used for aggregating multiple reports over different
    timeframes, where the rows from each report have a weight
    representing the time interval covered by the row in seconds.

    `df`       source pandas DataFrame

    `keys`     array of key column names

    `ops`      dict of operations to perform on each column.
               the key is the column, the value is either a
               numpy operation (et.sum, mean) or another function.
               Use 'avg' to compute the time weighted average

    `t_col`    the name of the column holding the time interval
               covered by each row

    `total_t`  the total time interval covered by all reports
               in the `df` source data

    For example, consider 3 queries over different intervals, the first
    is 1 hour (3600 seconds), the second and third both cover 8 hours
    (28800 seconds).  The results from each query are all in the
    same DataFrame.

    >>> q1_data = [['tcp',   72000,    20,          3600],
                   ['udp',   3600,     1,           3600],
                   ['icmp',  360,      0.1,         3600]]

    >>> q2_data = [['tcp',   1152000,  40,          28800],
                   ['udp',   57600,    2,           28800]]

    >>> q3_data = [['tcp',   1440000,  50,          28800],
                   ['udp',   201600,   7,           28800],
                   ['icmp',  8640,     0.3,         28800]]

    >>> data = q1_data.copy()
    >>> data.append(q2_data)
    >>> data.append(q3_data)

    >>> df = pandas.DataFrame(data,
           columns = ['proto', 'bytes', 'avg_bytes', 'interval'])

    >>> avg_groupby_aggregate(df, ['proto'],
                               {'bytes': sum, 'avg_bytes': 'avg'},
                               'interval', 3600 + 28800 + 28800)

        proto     bytes    avg_bytes
    0    icmp      9000     0.147059
    1    tcp    2664000    43.529412
    2    udp     262800     4.294118

    """
    # The basic idea is to leverage the pandas aggregate() function, but
    # it works most simply column by column, whereas we need to
    # leverage the weight of each row as it may change.
    #
    # We can get this done by instead computing weighted value for each
    # row, using pandas to aggregate using sum on just the weighted sum
    # columns, and then dividing the resulting sums by the total interval
    #
    # Basic algorithm for a column x:
    #   1. Compute x__weighted__ == x * t_col for all rows
    #   2. Group by and aggregate the weighted cols by sum()
    #   3. Compute the resulted x = sum(x__weighted__) / total_t

    # Simple function to define a unique column name
    # for the weighted total column for an existing column name
    def weighted_col(name):
        return name + '__weighted__'

    # The ops dictionary defines the map of column names and the aggregation
    # function.  Iterate through this map
    newops = {}
    for k, v in ops.iteritems():
        if v == 'avg':
            df[weighted_col(k)] = df[k] * df[t_col]
            newops[weighted_col(k)] = 'sum'
        else:
            newops[k] = ops[k]

    result = df.groupby(keys).aggregate(newops).reset_index()
    for k, v in ops.iteritems():
        if v == 'avg':
            result[k] = result[weighted_col(k)] / total_t
            del result[weighted_col(k)]
            del df[weighted_col(k)]

    return result
