"""
Graphite backend for the metrics api.
"""

from datetime import datetime
from urllib import urlencode
from urlparse import urljoin

from twisted.internet.defer import inlineCallbacks, returnValue

import treq

from confmodel.errors import ConfigError
from confmodel.fields import ConfigText, ConfigBool, ConfigInt

from go_metrics.metrics.base import (
    Metrics, MetricsBackend, MetricsBackendError, BadMetricsQueryError)
from go_metrics.metrics.graphite_time_parser import (
    interval_to_seconds, parse_time)


def agg_from_name(name):
    return name.split('.')[-1]


def is_error(resp):
    return 400 <= resp.code <= 599


def omit_nulls(datapoints):
    return [d for d in datapoints if d['y'] is not None]


def zeroize_nulls(datapoints):
    return [{
        'x': d['x'],
        'y': 0.0 if d['y'] is None else d['y']
    } for d in datapoints]


null_parsers = {
    'keep': lambda x: x,
    'omit': omit_nulls,
    'zeroize': zeroize_nulls,
}


class GraphiteMetrics(Metrics):
    def _build_metric_name(self, name, interval, align_to_from):
        agg = agg_from_name(name)
        full_name = "go.campaigns.%s.%s" % (self.owner_id, name)

        return (
            "alias(summarize(%s, '%s', '%s', %s), '%s')" %
            (full_name, interval, agg, align_to_from, name))

    def _build_render_url(self, params):
        metrics = params['m']

        targets = [
            self._build_metric_name(
                name, params['interval'], params['align_to_from'])
            for name in metrics]

        url = urljoin(self.backend.config.graphite_url, 'render/')
        return "%s?%s" % (url, urlencode({
            'format': 'json',
            'target': targets,
            'from': params['from'],
            'until': params['until'],
        }, True))

    def _parse_datapoints(self, datapoints):
        return [{
            'x': x * 1000,
            'y': y,
        } for (y, x) in datapoints]

    def _parse_response(self, data, null_parser):
        return dict(
            (d['target'], null_parser(self._parse_datapoints(d['datapoints'])))
            for d in data)

    def _get_auth(self):
        config = self.backend.config

        if config.username is not None and config.password is not None:
            return (config.username, config.password)
        else:
            return None

    def _predict_data_size(self, start, end, interval):
        """
        Use the start and end times and interval size to predict the number of
        data points being requested.
        """
        now = datetime.utcnow()
        # "end" can be earlier than "start".
        period = abs(parse_time(end, now) - parse_time(start, now))
        interval_secs = interval_to_seconds(interval)
        return (period.seconds + 86400 * period.days) / interval_secs

    @inlineCallbacks
    def get(self, **kw):
        params = {
            'm': [],
            'from': '-24h',
            'until': '-0s',
            'nulls': 'zeroize',
            'interval': '1hour',
            'align_to_from': 'false',
        }
        params.update(kw)

        if (isinstance(params['m'], basestring)):
            params['m'] = [params['m']]

        predicted_size = self._predict_data_size(
            params['from'], params['until'], params['interval'])
        predicted_size *= max(1, len(params['m']))
        max_response_size = self.backend.config.max_response_size
        if predicted_size > max_response_size:
            raise BadMetricsQueryError(
                "%s data points requested, maximum allowed is %s" % (
                    predicted_size, max_response_size))

        if params['nulls'] not in null_parsers:
            raise BadMetricsQueryError(
                "Unrecognised null parser '%s'" % (params['nulls'],))

        url = self._build_render_url(params)
        resp = yield treq.get(
            url,
            auth=self._get_auth(),
            persistent=self.backend.config.persistent)

        if is_error(resp):
            raise MetricsBackendError(
                "Got error response interacting with metrics backend")

        null_parser = null_parsers[params['nulls']]
        returnValue(self._parse_response((yield resp.json()), null_parser))


class GraphiteBackendConfig(MetricsBackend.config_class):
    graphite_url = ConfigText(
        "Url for the graphite web server to query",
        default='http://127.0.0.1:8080')

    persistent = ConfigBool(
        ("Flag given to treq telling it whether to maintain a single "
         "connection for the requests made to graphite's web app."),
        default=True)

    username = ConfigText(
        "Basic auth username for authenticating requests to graphite.",
        required=False)

    password = ConfigText(
        "Basic auth password for authenticating requests to graphite.",
        required=False)

    max_response_size = ConfigInt(
        ("Maximum number of data points to return. If a request specifies a "
         "time range and interval that contains more data than this, it is "
         "rejected."),
        default=10000)

    def post_validate(self):
        auth = (self.username, self.password)
        exists = [x is not None for x in auth]

        if any(exists) and not all(exists):
            raise ConfigError(
                "Either both a username and password need to be given or "
                "neither for graphite backend config")


class GraphiteBackend(MetricsBackend):
    model_class = GraphiteMetrics
    config_class = GraphiteBackendConfig
