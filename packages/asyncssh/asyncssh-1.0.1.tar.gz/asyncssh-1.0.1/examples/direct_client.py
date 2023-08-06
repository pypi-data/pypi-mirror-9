#!/usr/bin/env python3.4
#
# Copyright (c) 2013-2014 by Ron Frederick <ronf@timeheart.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation

import asyncio, asyncssh, sys

class MySSHTCPSession(asyncssh.SSHTCPSession):
    def data_received(self, data, datatype):
        # We use sys.stdout.buffer here because we're writing bytes
        sys.stdout.buffer.write(data)

    def connection_lost(self, exc):
        if exc:
            print('Direct connection error:', str(exc), file=sys.stderr)

@asyncio.coroutine
def run_client():
    conn, client = yield from asyncssh.create_connection(None, 'localhost')
    chan, session = yield from conn.create_connection(MySSHTCPSession,
                                                      'www.google.com', 80)

    # By default, TCP connections send and receive bytes
    chan.write(b'HEAD / HTTP/1.0\r\n\r\n')
    chan.write_eof()

    yield from chan.wait_closed()
    conn.close()

try:
    asyncio.get_event_loop().run_until_complete(run_client())
except (OSError, asyncssh.Error) as exc:
    sys.exit('SSH connection failed: ' + str(exc))
