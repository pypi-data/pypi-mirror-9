from __future__ import absolute_import

import logging

from twisted.internet import reactor

from autobahn.twisted import wamp, websocket
from autobahn.wamp.serializer import JsonSerializer
from twisted.internet.endpoints import clientFromString
from autobahn.wamp import types


class WampBroadcaster(object):
    HEARTBEAT_INTERVAL = 120

    def __init__(self, host, port, target=None):
        self.host = host
        self.port = port
        self.target = target
        self.url = 'ws://%s:%s/' % (self.host, self.port)
        self.logger = logging.getLogger('broadcaster')
        logging.getLogger("twisted").setLevel(logging.ERROR)
        self.logger.debug('Configured broadcaster: %s' % self.url)
        self.client = None
        self.on_session_open_handlers = []
        self.queue = []
        self._client_watchdog()

    def connect(self):
        self.logger.warn("Caught invalid call to `connect()`, this is not required since the client now autoconnects.")

    def _connect(self):
        if self.client:
            self.logger.debug('already connected to broadcaster %s' % self.url)
            return
        broadcaster = self
        self.logger.debug('trying to connect to broadcaster %s' % self.url)

        class BroadcasterComponent(wamp.ApplicationSession):

            def onJoin(self, details):
                broadcaster.client = self
                broadcaster.onSessionOpen()

            def onDisconnect(self):
                broadcaster.logger.debug("Disconnected from broadcaster at %s, will reconnect" % broadcaster.host)
                broadcaster.client = None

        component_config = types.ComponentConfig(realm="yadt")
        session_factory = wamp.ApplicationSessionFactory(config=component_config)
        session_factory.session = BroadcasterComponent
        serializers = [JsonSerializer()]
        transport_factory = websocket.WampWebSocketClientFactory(session_factory,
                                                                 serializers=serializers,
                                                                 url="ws://{0}:{1}/wamp".format(self.host,
                                                                                                self.port),
                                                                 debug=False,
                                                                 debug_wamp=False)
        client = clientFromString(reactor, "tcp:{0}:{1}".format(self.host,
                                                                self.port))
        from functools import partial
        client.connect(transport_factory).addErrback(
            partial(broadcaster.logger.warning, "Could not connect to broadcaster at %s"))

    def addOnSessionOpenHandler(self, handler):
        self.on_session_open_handlers.append(handler)

    def _client_watchdog(self, delay=1):
        if hasattr(self, 'client') and self.client:
            reactor.callLater(1, self._client_watchdog)
        else:
            reactor.callLater(delay, self._client_watchdog, min(60, 2 * delay))
            self.logger.debug('client not set, trying to connect')
            if delay > 1:
                self.logger.debug('(scheduling next try in %s seconds)' % delay)
            return self._connect()

    def onSessionOpen(self):
        if self.target:
            self.logger.debug("subscribing to %s" % self.target)
            self.client.subscribe(self.onEvent, self.target)
        for handler in self.on_session_open_handlers:
            handler()
        self.on_session_open_handlers = []  # run handlers only once

        if self.queue:
            number_of_events_to_flush = len(self.queue)
            for (target, event) in self.queue:
                self._publish(target, event)
            self.queue = self.queue[number_of_events_to_flush:]

        reactor.callLater(WampBroadcaster.HEARTBEAT_INTERVAL, self._heartbeat)

    def _heartbeat(self):
        self._sendEvent('heartbeat', None)
        reactor.callLater(WampBroadcaster.HEARTBEAT_INTERVAL, self._heartbeat)

    def onEvent(self, event):
        """
        As opposed to wamp v1 the arity of this method __MUST__ be 2, not 3
        """
        pass

    def sendFullUpdate(self, data, tracking_id=None):
        return self._sendEvent('full-update', data, tracking_id)

    def sendServiceChange(self, data, tracking_id=None):
        return self._sendEvent('service-change', data, tracking_id)

    def _sendEvent(self, id, data, tracking_id=None, target=None, **kwargs):
        if not target:
            target = self.target
        self.logger.debug('Going to send event %s on target %r' % (id, target))

        event = {
            'type': 'event',
            'id': id,
            'tracking_id': tracking_id,
            'target': target,
            'payload': data
        }
        for kwarg_key, kwarg_val in kwargs.iteritems():
            event[kwarg_key] = kwarg_val

        self._publish(target, event)

    def _publish(self, target, event):
        if not self._check_connection():
            self.logger.debug('Queueing event %s on %s since not connected' % (
                event,
                target))
            self.queue.append((target, event))
            return
        self.client.publish(target, event)

    def _check_connection(self):
        if not self.client:
            warning_sent_attribute_name = 'not_connected_warning_sent'
            if not getattr(self, warning_sent_attribute_name, False):
                setattr(self, warning_sent_attribute_name, True)
                self.logger.warning(
                    'Could not connect to broadcaster at %s' % self.url)
            self.logger.debug('not connected, queueing data')
            return False
        return True

    def publish_cmd_for_target(self, target, cmd, state, message=None, tracking_id=None):
        self._sendEvent(id='cmd',
                        data=None,
                        tracking_id=tracking_id,
                        target=target,
                        cmd=cmd,
                        state=state,
                        message=message)

    def publish_cmd(self, cmd, state, message=None, tracking_id=None):
        self._sendEvent(id='cmd',
                        data=None,
                        tracking_id=tracking_id,
                        target=self.target,
                        cmd=cmd,
                        state=state,
                        message=message)

    def publish_request_for_target(self, target, cmd, args, tracking_id=None):
        self._sendEvent(id='request',
                        data=None,
                        tracking_id=tracking_id,
                        target=target,
                        cmd=cmd,
                        args=args)
