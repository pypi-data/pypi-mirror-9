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

from ws4py.messaging import TextMessage
import logging
import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket, EchoWebSocket
import time

logger = logging.getLogger(__name__)

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
                $('#msg').append('<code>'+evt.data+'</code><br />');
                window.scrollTo = document.body.scrollHeight();
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

class HTMLFormatter(logging.Formatter):
    """Formats html records.
    """
    def format(self, record):
        msg = str(record.levelname).lower() + ":" + record.getMessage() + "<br />"
        return msg


class CherrypyHandler(logging.Handler):
    """Sends the record through a websocket.
    """

    def __init__(self, port=9000):
        logging.Handler.__init__(self)
        cherrypy.tree.mount(Root(), "/",
                            config={'/ws': {'tools.websocket.on': True,
                                            'tools.websocket.handler_cls': EchoWebSocket}})
        self._engine = cherrypy.engine
        print "init ok"
        self._engine.start()
        print "engine started"

    def emit(self, record):
        print "calling emit"
        message = self.format(record)
        print message
        self._engine.publish("websocket-broadcast", TextMessage(message))

    def close(self):
        logging.Handler.close(self)
        self._engine.stop()

if __name__ == '__main__':
    logger = logging.getLogger("")
    logger.setLevel(logging.DEBUG)
    ch = CherrypyHandler()
    print "cpyh started"
    ch.setLevel(logging.DEBUG)

    #formatter = HTMLFormatter()
    #ch.setFormatter(formatter)
    ch.setFormatter(logging.Formatter("[%(levelname)s: %(asctime)s :"
                                      " %(name)s] %(message)s",
                                      '%Y-%m-%d %H:%M:%S'))
    logger.addHandler(ch)

    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # ch.setFormatter(logging.Formatter("[%(levelname)s: %(asctime)s :"
    #                                   " %(name)s] %(message)s",
    #                                   '%Y-%m-%d %H:%M:%S'))

    # logger.addHandler(ch)

    logger = logging.getLogger("pytroll")
    logger.setLevel(logging.DEBUG)
    
    from posttroll.logger import Logger
    try:
        logger = Logger()
        logger.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.stop()
        print ("Thanks for using pytroll/cpylogger. "
               "See you soon on www.pytroll.org!")
