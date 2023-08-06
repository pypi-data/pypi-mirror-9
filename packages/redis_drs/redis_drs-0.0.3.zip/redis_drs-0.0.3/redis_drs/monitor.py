
import redis

class ConfigurationError(Exception):
    ""

class KeyRemovalWatcher(object):


    def __init__(self, server, callback):
        self.server = server
        self.callback = callback
        self.pubsub = None
        self.pattern = '*'
        self.thread = None
        enabled_events = set(self.server.config_get().get('notify-keyspace-events', ''))
        desired_events = set('KE')  # FIXME
        if desired_events - enabled_events:
            raise ConfigurationError('Some required event notifications have not been enabled. '
                                    'See: http://redis.io/topics/notifications')

    def is_removal_message(self, name):
        # FIXME: there are definately some cases that aren't handled. FLUSH? ..
        if name in ['del', 'expired', 'evicted']:
            return True
        if name.startswith('rename_'):
            return True
        return False

    def handle_deleted_keys(self, message):
        if not self.is_removal_message(message['data']):
            return
        _, key = message['channel'].split(':')
        self.callback(key)

    def stop_watch(self):
        self.pubsub.punsubscribe(self.pattern)
        self.thread.stop()

    def start_watch(self):
        if self.pubsub is None:
            self.pubsub = self.server.pubsub()
        self.pubsub.psubscribe(**{self.pattern: self.handle_deleted_keys})
        self.thread = self.pubsub.run_in_thread(sleep_time=0.001)


