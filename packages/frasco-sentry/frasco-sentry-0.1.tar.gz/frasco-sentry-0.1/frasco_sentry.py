from frasco import Feature, actions
from raven.contrib.flask import Sentry


class SentryFeature(Feature):
    name = "sentry"

    def init_app(self, app):
        self.client = Sentry(app, dsn=self.options["dsn"])

    @action("capture_sentry_message", default_option="msg")
    def capture_message(self, msg):
        self.client.captureMessage(msg)