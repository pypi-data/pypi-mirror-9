from frasco import Feature, action, current_app
from statsd import StatsClient


class StatsdFeature(Feature):
    name = "statsd"
    defaults = {"host": "localhost",
                "port": 8125,
                "prefix": None,
                "maxudpsize": 512,
                "log": False}

    def init_app(self, app):
        if self.options['host']:
            self.client = StatsClient(
                host=self.options['host'],
                port=self.options['port'],
                prefix=self.options['prefix'],
                maxudpsize=self.options['maxudpsize'])
        self.timer_stack = []

    def _log(self, action, stat, value):
        if self.options['log']:
            current_app.logger.info('STATSD: %s: %s = %s' % (action, stat, value))

    @action('statsd_incr', default_option='stat')
    def incr(self, stat, value=1, rate=1):
        if self.client:
            self.client.incr(stat, value, rate)
        self._log('incr', stat, value)

    @action('statsd_decr', default_option='stat')
    def decr(self, stat, value=1, rate=1):
        if self.client:
            self.client.decr(stat, value, rate)
        self._log('decr', stat, value)

    @action('statsd_gauge')
    def gauge(self, stat, value, rate=1, delta=False):
        if self.client:
            self.client.gauge(stat, value, rate, delta)
        self._log('gauge', stat, value)

    @action('statsd_gauge_incr', default_option='stat')
    def gauge_incr(self, stat, value=1, rate=1):
        self.gauge(stat, value, rate, True)

    @action('statsd_set')
    def set(self, stat, value, rate=1):
        if self.client:
            self.client.set(stat, value, rate)
        self._log('set', stat, value)

    @action('statsd_timing')
    def timing(self, stat, delta, rate=1):
        if self.client:
            self.client.timing(stat, delta, rate)
        self._log('timing', stat, delta)

    @action('statsd_timer')
    def timer(self, stat, rate=1):
        if self.client:
            return self.client.timer(stat, rate)

    @action('statsd_start_timer', default_option='stat')
    def start_timer(self, stat, rate=1):
        timer = self.client.timer(stat, rate)
        self.timer_stack.append(timer)
        timer.start()
        return timer

    @action('statsd_stop_timer')
    def stop_timer(self):
        if self.timer_stack:
            timer = self.timer_stack.pop()
            timer.stop()
            return timer