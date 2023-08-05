from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__version__ = "0.1.0"

from analytics import Client


class SegmentIO(object):
    """This class is used to control Segment SDK integration to Flask
    application.

    Various configuration are supported to customize the behavior.

    SEGMENTIO_WRITE_KEY:
        Segment write key.

    SEGMENTIO_DEBUG:
        Enable/disable debugging. Default to `False`.

    SEGMENTIO_SEND:
        Enable/disable sending. Default to `True`.

    SEGEMENTIO_MAX_QUEUE_SIZE:
        Maximum queue size. Default to 100000.

    There are two usage modes which work very similar. One is binding
    the instance to a very specific Flask application::

        from flask import Flask
        from flask_segmentio import SegmentIO

        app = Flask(__name__)
        analytics = SegmentIO(app)

    The second possibility is to create the object once and configure
    application later to support it::

        from flask import Flask
        from flask_segmentio import SegmentIO

        analytics = SegmentIO()

        def create_ap():
            app = Flask(__name__)
            analytics.init_app(app)
            return app
    """
    def __init__(self, app=None):
        self.app = app
        self._client = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """This callback can be used to initialize an application for the use
        with Segment client.
        """
        app.config.setdefault("SEGMENTIO_WRITE_KEY", "")
        app.config.setdefault("SEGMENTIO_DEBUG", False)
        app.config.setdefault("SEGMENTIO_SEND", True)
        app.config.setdefault("SEGMENTIO_MAX_QUEUE_SIZE", 100000)

        app.extensions = getattr(app, "extensions", {})
        app.extensions["segmentio"] = self
        self.app = app

    @property
    def client(self):
        """Returns a cached object of Segment client. It's worth noting
        that accsessing this property without having a proper initialization
        step will raise an error."""
        assert self.app is not None, \
            "The segmentio extension was not registered " \
            "to the current application. Please make sure " \
            "to call init_app() first."

        if self._client is None:
            self._client = Client(
                self.app.config["SEGMENTIO_WRITE_KEY"],
                debug=self.app.config["SEGMENTIO_DEBUG"],
                send=self.app.config["SEGMENTIO_SEND"],
                on_error=self._on_error,
                max_queue_size=self.app.config["SEGMENTIO_MAX_QUEUE_SIZE"],
                )
        return self._client

    def track(self, *args, **kwargs):
        """Records the actions your users perform.

        Refer to https://segment.com/docs/libraries/python/#track
        for details.
        """
        return self.client.track(*args, **kwargs)

    def identify(self, *args, **kwargs):
        """Ties a user to their actions and record traits about them.

        Refer to https://segment.com/docs/libraries/python/#identify
        for details.
        """
        return self.client.identify(*args, **kwargs)

    def alias(self, *args, **kwargs):
        """Associates one identity with another.

        Refer to https://segment.com/docs/libraries/python/#alias
        for details.
        """
        return self.client.alias(*args, **kwargs)

    def group(self, *args, **kwargs):
        """Associates individual users with shared accounts or companies.

        Refer to https://segment.com/docs/libraries/python/#group
        for details.
        """
        return self.client.group(*args, **kwargs)

    def page(self, *args, **kwargs):
        """Records page views on your website, along with optional
        extra information about the page being viewed.

        Refer to https://segment.com/docs/libraries/python/#page
        for details.
        """
        return self.client.page(*args, **kwargs)

    def screen(self, *args, **kwargs):
        """Records screen views on your mobile app, along with optional
        extra information about the screen being viewed.

        Refer to https://segment.com/docs/libraries/python/#screen
        for details.
        """
        return self.client.screen(*args, **kwargs)

    def flush(self):
        """Forces a flush from the internal queue to the server.
        """
        self.client.flush()

    def _on_error(self, exc, batch):
        pass
