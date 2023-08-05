# coding: utf-8

from __future__ import unicode_literals
from requests.packages.urllib3.exceptions import TimeoutError

from .base_endpoint import BaseEndpoint


class Events(BaseEndpoint):
    """Box API endpoint for subscribing to changes in a Box account."""

    def get_url(self, *args):
        """Base class override."""
        return super(Events, self).get_url('events', *args)

    def get_events(self, limit=100, stream_position=0, stream_type='all'):
        """
        Get Box events from a given stream position for a given stream type.
        :param limit:
            Maximum number of events to return.
        :type limit:
            `int`
        :param stream_position:
            The location in the stream from which to start getting events. 0 is the beginning of time. 'now' will
            return no events and just current stream position.
        :type stream_position:
            `unicode`
        :param stream_type:
            Which type of events to return. Can be 'all', 'tree', or 'sync'.
        :type stream_type:
            `unicode`
        :returns:
            JSON response from the Box /events endpoint. Contains the next stream position to use for the next call,
            along with some number of events.
        :rtype:
            `dict`
        """
        url = self.get_url()
        params = {
            'limit': limit,
            'stream_position': stream_position,
            'stream_type': stream_type,
        }
        box_response = self._session.get(url, params=params)
        return box_response.json()

    def get_latest_stream_position(self):
        """
        Get the latest stream position. The return value can be used with :meth:`get_events` or
        :meth:`generate_events_with_long_polling`.
        """
        url = self.get_url()
        params = {
            'stream_position': 'now',
        }
        return self._session.get(url, params=params).json()['next_stream_position']

    def _get_all_events_since(self, stream_position):
        next_stream_position = stream_position
        while True:
            events = self.get_events(stream_position=next_stream_position)
            next_stream_position = events['next_stream_position']
            events = events['entries']
            if not events:
                raise StopIteration
            for event in events:
                yield event, next_stream_position

    def long_poll(self, options, stream_position):
        """
        Set up a long poll connection at the specified url.
        """
        long_poll_response = self._session.get(
            options['url'],
            timeout=options['retry_timeout'],
            params={'stream_position': stream_position}
        )
        return long_poll_response

    def generate_events_with_long_polling(self, stream_position=None):
        """
        Subscribe to events from the given stream position.
        :param stream_position:
            The location in the stream from which to start getting events. 0 is the beginning of time. 'now' will
            return no events and just current stream position.
        :type stream_position:
            `unicode`
        :returns:
            Events corresponding to changes on Box in realtime, as they come in.
        :rtype:
            `generator` of :class:`Event`
        """
        stream_position = stream_position if stream_position is not None else self.get_latest_stream_position()
        while True:
            options = self.get_long_poll_options()
            while True:
                try:
                    long_poll_response = self.long_poll(options, stream_position)
                except TimeoutError:
                    break
                else:
                    message = long_poll_response.json()['message']
                    if message == 'new_change':
                        next_stream_position = stream_position
                        for event, next_stream_position in self._get_all_events_since(stream_position):
                            yield event
                        stream_position = next_stream_position
                        break
                    elif message == 'reconnect':
                        continue
                    else:
                        break

    def get_long_poll_options(self):
        """
        Get the url and retry timeout for setting up a long polling connection.
        """
        url = self.get_url()
        box_response = self._session.options(url)
        return box_response.json()['entries'][0]
