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

@asyncio.coroutine
def run_client():
    conn, client = yield from asyncssh.create_connection(None, 'localhost')
    stdin, stdout, stderr = yield from conn.open_session('bc')

    for op in ['2+2', '1*2*3*4', '2^32']:
        stdin.write(op + '\n')
        result = yield from stdout.readline()
        print(op, '=', result, end='')

    conn.close()

try:
    asyncio.get_event_loop().run_until_complete(run_client())
except (OSError, asyncssh.Error) as exc:
    sys.exit('SSH connection failed: ' + str(exc))
