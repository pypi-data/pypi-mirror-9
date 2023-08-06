from datetime import datetime

from twisted.trial.unittest import TestCase

from go_metrics.metrics.graphite_time_parser import (
    TimeParserValueError, interval_to_seconds, parse_time)


class TestGraphiteTimeParser(TestCase):
    """
    Tests for Graphite-compatible time parsing functions.
    """

    def assert_TPVE(self, *args, **kw):
        """
        Convenience wrapper for asserting TimeParserValueError is raised.
        """
        return self.assertRaises(TimeParserValueError, *args, **kw)

    def assert_interval_to_seconds(self, expected, *inputs):
        """
        Convenience wrapper for testing multiple equivalent interval strings at
        once.
        """
        for value in inputs:
            self.assertEqual(interval_to_seconds(value), expected)

    def test_interval_to_seconds_with_invalid_value(self):
        """
        A TimeParserValueError is raised for various invalid values.
        """
        self.assert_TPVE(interval_to_seconds, "")
        self.assert_TPVE(interval_to_seconds, "s")
        self.assert_TPVE(interval_to_seconds, "1")
        self.assert_TPVE(interval_to_seconds, "three days")
        self.assert_TPVE(interval_to_seconds, "-1h")
        self.assert_TPVE(interval_to_seconds, "2fortnights")

    def test_interval_to_seconds_with_seconds(self):
        """
        With a suffix of "s" or "seconds", the interval is parsed in seconds.
        """
        self.assert_interval_to_seconds(0, "0s", "0second", "0seconds")
        self.assert_interval_to_seconds(1, "1s", "1second", "1seconds")
        self.assert_interval_to_seconds(60, "60s", "60second", "60seconds")
        self.assert_interval_to_seconds(
            1234567, "1234567s", "1234567second", "1234567seconds")
        self.assert_interval_to_seconds(12, "012s", "012second", "012seconds")

    def test_interval_to_seconds_with_minutes(self):
        """
        With a suffix of "min" or "minutes", the interval is parsed in minutes.
        """
        self.assert_interval_to_seconds(
            0, "0min", "0mins", "0minute", "0minutes")
        self.assert_interval_to_seconds(
            60, "1min", "1mins", "1minute", "1minutes")
        self.assert_interval_to_seconds(
            3600, "60min", "60mins", "60minute", "60minutes")
        self.assert_interval_to_seconds(
            1234567 * 60, "1234567min", "1234567mins", "1234567minute",
            "1234567minutes")
        self.assert_interval_to_seconds(
            720, "012min", "012mins", "012minute", "012minutes")

    def test_interval_to_seconds_with_hours(self):
        """
        With a suffix of "h" or "hours", the interval is parsed in hours.
        """
        self.assert_interval_to_seconds(0, "0h", "0hour", "0hours")
        self.assert_interval_to_seconds(3600, "1h", "1hour", "1hours")
        self.assert_interval_to_seconds(24 * 3600, "24h", "24hour", "24hours")
        self.assert_interval_to_seconds(
            1234 * 3600, "1234h", "1234hour", "1234hours")
        self.assert_interval_to_seconds(
            12 * 3600, "012h", "012hour", "012hours")

    def test_interval_to_seconds_with_days(self):
        """
        With a suffix of "d" or "days", the interval is parsed in days.
        """
        self.assert_interval_to_seconds(0, "0d", "0day", "0days")
        self.assert_interval_to_seconds(86400, "1d", "1day", "1days")
        self.assert_interval_to_seconds(60 * 86400, "60d", "60day", "60days")
        self.assert_interval_to_seconds(
            1234 * 86400, "1234d", "1234day", "1234days")
        self.assert_interval_to_seconds(
            14 * 86400, "014d", "014day", "014days")

    def test_interval_to_seconds_with_weeks(self):
        """
        With a suffix of "w" or "weeks", the interval is parsed in weeks.
        """
        self.assert_interval_to_seconds(0, "0w", "0week", "0weeks")
        self.assert_interval_to_seconds(604800, "1w", "1week", "1weeks")
        self.assert_interval_to_seconds(4 * 604800, "4w", "4week", "4weeks")
        self.assert_interval_to_seconds(
            123 * 604800, "123w", "123week", "123weeks")
        self.assert_interval_to_seconds(
            12 * 604800, "012w", "012week", "012weeks")

    def test_interval_to_seconds_with_months(self):
        """
        With a suffix of "mon" or "months", the interval is parsed in months.
        """
        self.assert_interval_to_seconds(0, "0mon", "0month", "0months")
        self.assert_interval_to_seconds(2592000, "1mon", "1month", "1months")
        self.assert_interval_to_seconds(
            12 * 2592000, "12mon", "12month", "12months")
        self.assert_interval_to_seconds(
            123 * 2592000, "123mon", "123month", "123months")
        self.assert_interval_to_seconds(
            12 * 2592000, "012mon", "012month", "012months")

    def test_interval_to_seconds_with_years(self):
        """
        With a suffix of "y" or "years", the interval is parsed in years.
        """
        self.assert_interval_to_seconds(0, "0y", "0year", "0years")
        self.assert_interval_to_seconds(31536000, "1y", "1year", "1years")
        self.assert_interval_to_seconds(5 * 31536000, "5y", "5year", "5years")
        self.assert_interval_to_seconds(
            123 * 31536000, "123y", "123year", "123years")
        self.assert_interval_to_seconds(
            2 * 31536000, "02y", "02year", "02years")

    def test_parse_time_with_invalid_interval(self):
        """
        If given a time_str starting with "-" and containing an invalid
        interval, a TimeParserValueError is raised.
        """
        now = datetime(2015, 2, 1, 0, 0, 0)
        self.assert_TPVE(parse_time, "-0", now)
        self.assert_TPVE(parse_time, "-12", now)
        self.assert_TPVE(parse_time, "-12fortnights", now)
        self.assert_TPVE(parse_time, "-20150101", now)

    def test_parse_time_with_interval(self):
        """
        If given a time_str starting with "-", the time is parsed as an
        interval prior to "now".
        """
        now = datetime(2015, 2, 1, 0, 0, 0)
        self.assertEqual(parse_time("-0s", now), now)
        self.assertEqual(
            parse_time("-1s", now), datetime(2015, 1, 31, 23, 59, 59))
        self.assertEqual(
            parse_time("-1s", now), datetime(2015, 1, 31, 23, 59, 59))
        self.assertEqual(
            parse_time("-2w", now), datetime(2015, 1, 18, 0, 0, 0))
        self.assertEqual(
            parse_time("-2w", datetime(2015, 1, 24, 10, 15, 25)),
            datetime(2015, 1, 10, 10, 15, 25))

    def test_parse_time_special_values(self):
        """
        The strings "now", "yesterday", "today", and "tomorrow" return what one
        might expect.
        """
        now1 = datetime(2015, 2, 1, 0, 0, 0)
        now2 = datetime(2015, 1, 24, 10, 15, 25)
        self.assertEqual(parse_time("now", now1), now1)
        self.assertEqual(parse_time("now", now2), now2)
        self.assertEqual(
            parse_time("yesterday", now1), datetime(2015, 1, 31, 0, 0, 0))
        self.assertEqual(
            parse_time("yesterday", now2), datetime(2015, 1, 23, 10, 15, 25))
        self.assertEqual(parse_time("today", now1), now1)
        self.assertEqual(parse_time("today", now2), now2)
        self.assertEqual(
            parse_time("tomorrow", now1), datetime(2015, 2, 2, 0, 0, 0))
        self.assertEqual(
            parse_time("tomorrow", now2), datetime(2015, 1, 25, 10, 15, 25))

    def test_parse_time_absolute_datetime(self):
        """
        Absolute timestamps in the form ``HH:MM_YYYYMMDD`` are parsed into
        appropriate datetimes with seconds set to zero.
        """
        self.assertEqual(
            parse_time("00:00_20150201", None), datetime(2015, 2, 1, 0, 0, 0))
        self.assertEqual(
            parse_time("00:00_19700101", None), datetime(1970, 1, 1, 0, 0, 0))

    def test_parse_time_absolute_date(self):
        """
        Absolute timestamps in the form ``YYYYMMDD`` are parsed into
        appropriate datetimes with the time set to midnight.
        """
        self.assertEqual(
            parse_time("20150201", None), datetime(2015, 2, 1, 0, 0, 0))
        self.assertEqual(
            parse_time("19700101", None), datetime(1970, 1, 1, 0, 0, 0))
        self.assertEqual(
            parse_time("19010101", None), datetime(1901, 1, 1, 0, 0, 0))
        self.assertEqual(
            parse_time("99991231", None), datetime(9999, 12, 31, 0, 0, 0))

    def test_parse_time_unix_timestamp(self):
        """
        Unix timestamps are accepted as absolute time specifications.
        """
        self.assertEqual(
            parse_time("1422748800", None), datetime(2015, 2, 1, 0, 0, 0))
        self.assertEqual(parse_time("0", None), datetime(1970, 1, 1, 0, 0, 0))
        # The following are treated as unix timestamps, not YYYYMMDD strings.
        self.assertEqual(
            parse_time("19000101", None), datetime(1970, 8, 8, 21, 48, 21))
        self.assertEqual(
            parse_time("20150132", None), datetime(1970, 8, 22, 5, 15, 32))
        self.assertEqual(
            parse_time("20151301", None), datetime(1970, 8, 22, 5, 35, 1))

    def test_parse_time_with_invalid_absolute_datetime(self):
        """
        If given a time_str containing an invalid value, a TimeParserValueError
        is raised.
        """
        self.assert_TPVE(parse_time, "", None)
        self.assert_TPVE(parse_time, "blahblah", None)
        # This is detected as a YYYYMMDD string, but it's invalid.
        self.assert_TPVE(parse_time, "20150231", None)

        # Graphite accepts the following, we don't.
        self.assert_TPVE(parse_time, "2015_02_01", None)
        self.assert_TPVE(parse_time, "12:35 20150201", None)
        self.assert_TPVE(parse_time, "12:3520150201", None)
        self.assert_TPVE(parse_time, "12/31/99", None)
        self.assert_TPVE(parse_time, "6pm today", None)
        self.assert_TPVE(parse_time, "noon tomorrow", None)
        self.assert_TPVE(parse_time, "january 1", None)
        self.assert_TPVE(parse_time, "monday", None)
