# Copyright (c) 2015, OLogN Technologies AG. All rights reserved.
#
# Redistribution and use of this file in source and compiled
# forms, with or without modification, are permitted
# provided that the following conditions are met:
#     * Redistributions in source form must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in compiled form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the OLogN Technologies AG nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL OLogN Technologies AG BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE

# pylint: disable=W0613

from binascii import hexlify

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, maybeDeferred, returnValue
from twisted.internet.serialport import SerialPort

import smartanthill.network.protocol as sanp
from smartanthill.exception import NetworkRouterConnectFailure
from smartanthill.service import SAMultiService
from smartanthill.util import get_service_named


class ControlService(SAMultiService):

    def __init__(self, name):
        SAMultiService.__init__(self, name)
        self._protocol = sanp.ControlProtocolWrapping(
            self.climessage_protocallback)
        self._litemq = None

    def startService(self):
        self._litemq = get_service_named("litemq")
        self._protocol.makeConnection(self)
        self._litemq.consume("network", "control.in", "transport->control",
                             self.inmessage_mqcallback)
        self._litemq.consume("network", "control.out", "client->control",
                             self.outmessage_mqcallback)
        SAMultiService.startService(self)

    def stopService(self):
        SAMultiService.stopService(self)
        self._litemq.unconsume("network", "control.in")
        self._litemq.unconsume("network", "control.out")

    def write(self, message):
        self._litemq.produce("network", "control->transport", message,
                             dict(binary=True))

    def inmessage_mqcallback(self, message, properties):
        self.log.debug("Received incoming raw message %s" % hexlify(message))
        self._protocol.dataReceived(message)

    def outmessage_mqcallback(self, message, properties):
        self.log.debug("Received outgoing %s and properties=%s" %
                       (message, properties))
        self._protocol.send_message(message)

    def climessage_protocallback(self, message):
        self.log.debug("Received incoming client %s" % message)
        self._litemq.produce("network", "control->client", message)


class TransportService(SAMultiService):

    def __init__(self, name):
        SAMultiService.__init__(self, name)
        self._protocol = sanp.TransportProtocolWrapping(
            self.rawmessage_protocallback)
        self._litemq = None

    def startService(self):
        self._litemq = get_service_named("litemq")
        self._protocol.makeConnection(self)
        self._litemq.consume("network", "transport.in", "routing->transport",
                             self.insegment_mqcallback)
        self._litemq.consume("network", "transport.out", "control->transport",
                             self.outmessage_mqcallback, ack=True)
        SAMultiService.startService(self)

    def stopService(self):
        SAMultiService.stopService(self)
        self._litemq.unconsume("network", "transport.in")
        self._litemq.unconsume("network", "transport.out")

    def rawmessage_protocallback(self, message):
        self.log.debug("Received incoming raw message %s" % hexlify(message))
        self._litemq.produce("network", "transport->control", message,
                             dict(binary=True))

    def write(self, segment):
        self._litemq.produce("network", "transport->routing", segment,
                             dict(binary=True))

    def insegment_mqcallback(self, message, properties):
        self.log.debug("Received incoming segment %s" % hexlify(message))
        self._protocol.dataReceived(message)

    @inlineCallbacks
    def outmessage_mqcallback(self, message, properties):
        self.log.debug("Received outgoing message %s" % hexlify(message))
        ctrlmsg = sanp.ControlProtocol.rawmessage_to_message(message)

        def _on_err(failure):
            self._litemq.produce("network", "transport->err", ctrlmsg)
            failure.raiseException()

        d = maybeDeferred(self._protocol.send_message, message)
        d.addErrback(_on_err)
        result = yield d
        if result and ctrlmsg.ack:
            self._litemq.produce("network", "transport->ack", ctrlmsg)
        returnValue(result)


class RouterService(SAMultiService):

    RECONNECT_DELAY = 1  # in seconds

    def __init__(self, name, options):
        SAMultiService.__init__(self, name, options)
        self._protocol = sanp.RoutingProtocolWrapping(
            self.inpacket_protocallback)
        self._router_device = None
        self._litemq = None
        self._reconnect_nums = 0
        self._reconnect_callid = None

    def startService(self):
        connection = self.options['connection']
        try:
            if connection.get_type() == "serial":
                _kwargs = connection.params
                _kwargs['protocol'] = self._protocol
                _kwargs['reactor'] = reactor

                # rename port's argument
                if "port" in _kwargs:
                    _kwargs['deviceNameOrPortNumber'] = _kwargs['port']
                    del _kwargs['port']

                self._router_device = SerialPort(**_kwargs)
        except:
            self.log.error(NetworkRouterConnectFailure(self.options))
            self._reconnect_nums += 1
            self._reconnect_callid = reactor.callLater(
                self._reconnect_nums * self.RECONNECT_DELAY, self.startService)
            return

        self._litemq = get_service_named("litemq")
        self._litemq.consume(
            exchange="network",
            queue="routing.out." + self.name,
            routing_key="transport->routing",
            callback=self.outsegment_mqcallback
        )

        SAMultiService.startService(self)

    def stopService(self):
        SAMultiService.stopService(self)
        if self._reconnect_callid:
            self._reconnect_callid.cancel()
        if self._router_device:
            self._router_device.loseConnection()
        if self._litemq:
            self._litemq.unconsume("network", "routing.out." + self.name)

    def inpacket_protocallback(self, packet):
        self.log.debug("Received incoming packet %s" % hexlify(packet))
        self._litemq.produce("network", "routing->transport",
                             sanp.RoutingProtocol.packet_to_segment(packet),
                             dict(binary=True))

    def outsegment_mqcallback(self, message, properties):
        # check destination ID  @TODO
        if ord(message[2]) not in self.options['deviceids']:
            return False
        self.log.debug("Received outgoing segment %s" % hexlify(message))
        self._protocol.send_segment(message)


class ConnectionInfo(object):

    def __init__(self, uri):
        assert ":" in uri
        self.uri = uri
        parts = uri.split(":")
        self.type_ = parts[0]
        self.params = dict()

        for part in parts[1:]:
            key, value = part.split("=")
            self.params[key] = value

    def __repr__(self):
        return "ConnectionInfo: %s" % self.uri

    def get_uri(self):
        return self.uri

    def get_type(self):
        return self.type_


class NetworkService(SAMultiService):

    def __init__(self, name, options):
        SAMultiService.__init__(self, name, options)
        self._litemq = None

    def startService(self):
        self._litemq = get_service_named("litemq")
        self._litemq.declare_exchange("network")

        ControlService("network.control").setServiceParent(self)
        TransportService("network.transport").setServiceParent(self)

        devices = get_service_named("device").get_devices()
        for devid, devobj in devices.iteritems():
            netopts = devobj.options.get("network", {})
            rconn = netopts.get("router", None)
            if not rconn:
                continue

            _options = {"connection": ConnectionInfo(rconn),
                        "deviceids": [devid]}
            RouterService("network.router.%d" % devid,
                          _options).setServiceParent(self)

        SAMultiService.startService(self)

    def stopService(self):
        SAMultiService.stopService(self)
        self._litemq.undeclare_exchange("network")


def makeService(name, options):
    return NetworkService(name, options)
