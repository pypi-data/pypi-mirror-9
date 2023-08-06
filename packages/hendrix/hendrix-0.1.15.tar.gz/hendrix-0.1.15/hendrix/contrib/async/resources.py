import json
import uuid

from twisted.internet import threads
from twisted.internet.protocol import Factory, Protocol
from txsockjs.factory import SockJSResource

from hendrix.resources import NamedResource

from .messaging import hxdispatcher
from .signals import message_signal


def send_signal(transport, data):
    message_signal.send(None, dispatcher=transport, data=data)


class MessageHandlerProtocol(Protocol):
    """
        A basic protocol for socket messaging
        using a hendrix messaging dispatcher to handle
        addressing messages to active sockets from
        different contexts
    """
    dispatcher = hxdispatcher
    guid = None

    def dataReceived(self, data):

        """
            Takes "data" which we assume is json encoded
            If data has a subject_id attribute, we pass that to the dispatcher
            as the subject_id so it will get carried through into any
            return communications and be identifiable to the client

            falls back to just passing the message along...

        """
        try:
            address = self.guid
            data = json.loads(data)
            threads.deferToThread(send_signal, self.dispatcher, data)

            if 'hx_subscribe' in data:
                return self.dispatcher.subscribe(self.transport, data)

            if 'address' in data:
                address = data['address']
            else:
                address = self.guid

            self.dispatcher.send(address, data)

        except Exception, exc:
            raise
            self.dispatcher.send(
                self.guid,
                {'message': data, 'error': str(exc)}
            )

    def connectionMade(self):
        """
        establish the address of this new connection and add it to the list of
        sockets managed by the dispatcher

        reply to the transport with a "setup_connection" notice
        containing the recipient's address for use by the client as a return
        address for future communications
        """
        self.transport.uid = str(uuid.uuid1())

        self.guid = self.dispatcher.add(self.transport)
        self.dispatcher.send(self.guid, {'setup_connection': self.guid})

    def connectionLost(self, something):
        "clean up the no longer useful socket in the dispatcher"
        self.dispatcher.remove(self.transport)


MessageResource = NamedResource('messages')
MessageResource.putChild(
    'main',
    SockJSResource(Factory.forProtocol(MessageHandlerProtocol))
)
