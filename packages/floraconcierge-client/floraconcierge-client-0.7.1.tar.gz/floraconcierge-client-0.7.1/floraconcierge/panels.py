from debug_toolbar.panels import Panel
from floraconcierge.client import ApiClient, ApiResult


class FloraConciergeRequests(Panel):
    name = 'FloraConciergeRequestsPanel'
    template = 'floraconcierge/debug_toolbar_floraconcierge_requests.html'
    title = 'FloraConcierge Api requests'
    nav_title = 'FloraConcierge'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(FloraConciergeRequests, self).__init__(*args, **kwargs)

        self._num_calls = 0
        self._calls_time = 0

    @property
    def nav_subtitle(self):
        return "%s calls in %.2fms" % (self._num_calls, self._calls_time)

    def process_response(self, request, response):
        api = request.api
        assert isinstance(api, ApiClient)

        call_time, calls = api.callstats()
        self._num_calls = len(calls)
        self._calls_time = call_time.total_seconds() * 1000

        queries = []
        width_ratio_tally = 0.0
        for c in calls:
            assert isinstance(c, ApiResult)

            q = {
                'name': c.func,
                'duration': c.time.total_seconds(),
                'duration_ms': c.time.total_seconds() * 1000,
                'width_ratio': c.time.total_seconds() / self._calls_time * 100,
                'params': c.params,
                'trace_color': '#800000',
                'url': c.url,
                'size': c.size,
                'data': c.dump()
            }

            try:
                q['width_ratio'] = (q['duration_ms'] / self._calls_time) * 100
                q['width_ratio_relative'] = (100.0 * q['width_ratio'] / (100.0 - width_ratio_tally))
            except ZeroDivisionError:
                q['width_ratio'] = 0
                q['width_ratio_relative'] = 0

            q['start_offset'] = width_ratio_tally

            width_ratio_tally += q['width_ratio']

            queries.append(q)

        self.record_stats({
            'calls': queries,
            'call_time': call_time.total_seconds()
        })
