#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Test websockets
"""

# doesn't work

# import socket, threading, time

# def handle(s):
#     print repr(s.recv(4096))
#     s.send('''
# HTTP/1.1 101 Web Socket Protocol Handshake\r
# Upgrade: WebSocket\r
# Connection: Upgrade\r
# WebSocket-Origin: http://localhost:8888\r
# WebSocket-Location: ws://localhost:9876/\r
# WebSocket-Protocol: sample
#   '''.strip() + '\r\n\r\n')
#     time.sleep(1)
#     s.send('\x00hello\xff')
#     time.sleep(1)
#     s.send('\x00world\xff')
#     s.close()

# s = socket.socket()
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# s.bind(('', 9876))
# s.listen(1)
# while True:
#     t, _ = s.accept()
#     threading.Thread(target=handle, args=(t,)).start()

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import threading
import time

cherrypy.config.update({'server.socket_port': 9000})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

idx = """
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Web Socket Example</title>
    <meta charset="UTF-8">
    <script>
      window.onload = function() {
        var s = new WebSocket("ws://localhost:9876/");
        s.onopen = function(e) { alert("opened"); }
        s.onclose = function(e) { alert("closed"); }
        s.onmessage = function(evt) { $('#msg').append('<p>'+evt.data+'</p>');
                }; 
      };
    </script>
  </head>
    <body>
      <div id="holder" style="width:600px; height:300px"></div>
    </body>
</html>
""".strip()

idx2 = """
<!DOCTYPE html>
<html>
<head>
<script src='http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js'></script>
<script>
    $(document).ready(function() {
            function debug(str) {
                $('#debug').append('<p>'+str+'</p>');
                };
            ws = new WebSocket('ws://localhost:9000/ws');

/* Define websocket handlers */
      ws.onmessage = function(evt) {
                $('#msg').append(evt.data+'<br />');
                document.scrollTop = document.scrollHeight;
                };
      ws.onclose = function() {
                debug('socket closed');
                };
      ws.onopen = function() {
                debug('connected...');
                ws.send('Hello.\\n');
            };
            });
/* Define click handler */

    $(document).click(function () {
                ws.send('Click!');
            });
</script>
</head>
<body>
    <div id='debug'></div>
    <div id='msg'></div>
</body>
</html>
""".strip()

class Root(object):
    @cherrypy.expose
    def index(self):
        #return 'some HTML with a websocket javascript connection'
        return idx2

    @cherrypy.expose
    @cherrypy.tools.websocket(on=False)
    def ws(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler
        #return handler

item = Root()

from ws4py.messaging import TextMessage
from posttroll.subscriber import Subscribe

#cherrypy.config.update({'/ws': {'tools.websocket.on': True,
#                                'tools.websocket.handler_cls': WebSocket}})
cherrypy.tree.mount(Root(), "/", config={'/ws': {'tools.websocket.on': True,
                                'tools.websocket.handler_cls': WebSocket}})

#cherrypy.quickstart(item, '/', config={'/ws': {'tools.websocket.on': True,
#                                               'tools.websocket.handler_cls': EchoWebSocket}})
#pause
cherrypy.engine.start()

def send(msg):
    cherrypy.engine.publish("websocket-broadcast", TextMessage(msg))

try:
    with Subscribe(services=[""], addr_listener=True) as sub:
        for msg in sub.recv(1):
            if msg:
                if msg.type in ["log.debug", "log.info",
                                "log.warning", "log.error",
                                "log.critical"]:
                    send(msg.type + " " + msg.subject + " " +
                         msg.sender + " " +
                         str(msg.data) + " " +
                         str(msg.time))

                elif msg.binary:
                    send(msg.subject + " " +
                         msg.sender + " " +
                         msg.type + " " +
                         "[binary] " +
                         str(msg.time))
                else:
                    send(msg.subject + " " +
                         msg.sender + " " +
                         msg.type + " " +
                         str(msg.data) + " " +
                         str(msg.time))

finally:
    cherrypy.engine.stop()

pause
#cherrypy.engine.publish("websocket-broadcast", msg)



class EchoWebSocket(WebSocket):
    def received_message(self, message):
        """
Automatically sends back the provided ``message`` to
its originating endpoint.
"""
        self.send(message.data, message.is_binary)
        # cnt = 0
        # while True:
            
        #     msg = TextMessage("hej " + str(cnt))
        #     self.send(msg.data, msg.is_binary)
        #     time.sleep(1)
        #     cnt += 1

        with Subscribe(services=[""], addr_listener=True) as sub:
            for msg in sub.recv(1):
                if msg:
                    if msg.type in ["log.debug", "log.info",
                                    "log.warning", "log.error",
                                    "log.critical"]:
                        self.send(msg.type + " " + msg.subject + " " +
                                                   msg.sender + " " +
                                                   str(msg.data) + " " +
                                                   str(msg.time))

                    elif msg.binary:
                        self.send(msg.subject + " " +
                                  msg.sender + " " +
                                  msg.type + " " +
                                  "[binary] " +
                                  str(msg.time))
                    else:
                        self.send(msg.subject + " " +
                                  msg.sender + " " +
                                  msg.type + " " +
                                  str(msg.data) + " " +
                                  str(msg.time))
#                if not self.loop:
#                    self.send("Stop logging")
#                    break

#cherrypy.quickstart(item, '/', config={'/ws': {'tools.websocket.on': True,
#                                                 'tools.websocket.handler_cls': EchoWebSocket}})

class listener( threading.Thread ):

    def __init__(self):
        threading.Thread.__init__( self )
        self.cpy = None		

    def run( self ):
        #self.cpy = cherrypy.quickstart( self )
        self.cpy = cherrypy.quickstart(item, '/', config={'/ws': {'tools.websocket.on': True,
                                                                  'tools.websocket.handler_cls': EchoWebSocket}})

    def stop( self ):
        self.cpy.stop()


interf = listener()
interf.start()

print "ready"
