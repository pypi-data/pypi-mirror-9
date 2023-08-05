#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Netius System
# Copyright (C) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Netius System.
#
# Hive Netius System is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Netius System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Netius System. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os

import netius

from . import http

BOUNDARY = "mjpegboundary"
""" The defualt boundary string value to be used in
case no boundary is provided to the app """

class MJPGServer(http.HTTPServer):
    """
    Server class for the creation of an http server for
    the providing of a motion jpeg stream (as in spec).

    This class should only be seen as a foundation and
    proper implementation should be made from this.
    """

    def __init__(self, boundary = BOUNDARY, *args, **kwargs):
        http.HTTPServer.__init__(self, *args, **kwargs)
        self.boundary = boundary

    def on_data_http(self, connection, parser):
        http.HTTPServer.on_data_http(self, connection, parser)

        status = "200 OK"
        headers = [
            ("Content-type", "multipart/x-mixed-replace; boundary=%s" % self.boundary),
            ("Cache-Control", "no-cache"),
            ("Connection", "close"),
            ("Pragma", "no-cache")
        ]

        version_s = parser.version_s
        headers = dict(headers)

        buffer = []
        buffer.append("%s %s\r\n" % (version_s, status))
        for key, value in headers.items():
            buffer.append("%s: %s\r\n" % (key, value))
        buffer.append("\r\n")

        data = "".join(buffer)
        connection.send(data)

        def send(connection):
            self.on_send_mjpg(connection)

            delay = self.get_delay(connection)
            data = self.get_image(connection)

            if not data: self.warning("No image retrieved from provider")
            if not data: data = b""

            data_l = len(data)

            buffer = []
            buffer.append(netius.legacy.bytes("--%s\r\n" % self.boundary))
            buffer.append(b"Content-Type: image/jpeg\r\n")
            buffer.append(netius.legacy.bytes("Content-Length: %d\r\n" % data_l))
            buffer.append(b"\r\n")
            buffer.append(data)
            buffer.append(b"\r\n")

            buffer_d = b"".join(buffer)

            def next(connection):
                def callable(): send(connection)
                self.delay(callable, delay)

            connection.send(buffer_d, callback = next)

        send(connection)

    def on_send_mjpg(self, connection):
        pass

    def get_delay(self, connection):
        return 1

    def get_image(self, connection):
        has_index = hasattr(connection, "index")
        if not has_index: connection.index = 0
        target = connection.index % 2
        connection.index += 1

        base_path = os.path.dirname(__file__)
        extras_path = os.path.join(base_path, "extras")
        file_path = os.path.join(extras_path, "boy_%d.jpg" % target)

        file = open(file_path, "rb")
        try: data = file.read()
        finally: file.close()

        return data

if __name__ == "__main__":
    server = MJPGServer()
    server.serve(env = True)
