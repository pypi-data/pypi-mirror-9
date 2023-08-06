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

"""SSH Diffie-Hellman key exchange handlers"""

from hashlib import sha1, sha256

from .constants import *
from .kex import *
from .logging import *
from .misc import *
from .packet import *
from .public_key import *


# SSH KEX DH message values
MSG_KEXDH_INIT  = 30
MSG_KEXDH_REPLY = 31

# SSH KEX DH group exchange message values
MSG_KEX_DH_GEX_REQUEST_OLD = 30
MSG_KEX_DH_GEX_GROUP       = 31
MSG_KEX_DH_GEX_INIT        = 32
MSG_KEX_DH_GEX_REPLY       = 33
MSG_KEX_DH_GEX_REQUEST     = 34

# SSH KEX group exchange key sizes
KEX_DH_GEX_MIN_SIZE        = 1024
KEX_DH_GEX_PREFERRED_SIZE  = 2048
KEX_DH_GEX_MAX_SIZE        = 8192

# SSH Diffie-Hellman group 1 parameters
_group1_g = 2
_group1_p = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece65381ffffffffffffffff

# SSH Diffie-Hellman group 14 parameters
_group14_g = 2
_group14_p = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca18217c32905e462e36ce3be39e772c180e86039b2783a2ec07a28fb5c55df06f4c52c9de2bcbf6955817183995497cea956ae515d2261898fa051015728e5a8aacaa68ffffffffffffffff


class _KexDH(Kex):
    """Handler for Diffie-Hellman key exchange"""

    def __init__(self, alg, conn, hash, g, p):
        super().__init__(alg, conn, hash)

        self._g = g
        self._p = p
        self._q = (p - 1) // 2

        if conn.is_client():
            self._send_init(MSG_KEXDH_INIT)

    def _send_init(self, pkttype):
        self._x = randrange(2, self._q)
        self._e = pow(self._g, self._x, self._p)

        self._conn._send_packet(Byte(pkttype), MPInt(self._e))

    def _send_reply(self, pkttype):
        if not 1 <= self._e < self._p:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Kex DH e out of range')

        y = randrange(2, self._q)
        self._f = pow(self._g, y, self._p)

        k = pow(self._e, y, self._p)

        if k < 1:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Kex DH k out of range')

        host_key, host_key_data = self._conn._get_server_host_key()

        h = self._compute_hash(host_key_data, k)
        sig = host_key.sign(h)

        self._conn._send_packet(Byte(pkttype),String(host_key_data),
                                MPInt(self._f), String(sig))

        self._conn._send_newkeys(k, h)

    def _verify_reply(self, host_key_data, sig):
        if not 1 <= self._f < self._p:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Kex DH f out of range')

        host_key = self._conn._validate_server_host_key(host_key_data)

        k = pow(self._f, self._x, self._p)

        if k < 1:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Kex DH k out of range')

        h = self._compute_hash(host_key_data, k)
        if not host_key.verify(h, sig):
            raise DisconnectError(DISC_KEY_EXCHANGE_FAILED,
                                  'Key exchange hash mismatch')

        self._conn._send_newkeys(k, h)

    def _compute_hash(self, host_key_data, k):
        hash = self._hash()
        hash.update(String(self._conn._client_version))
        hash.update(String(self._conn._server_version))
        hash.update(String(self._conn._client_kexinit))
        hash.update(String(self._conn._server_kexinit))
        hash.update(String(host_key_data))
        hash.update(MPInt(self._e))
        hash.update(MPInt(self._f))
        hash.update(MPInt(k))
        return hash.digest()

    def _process_init(self, pkttype, packet):
        if self._conn.is_client() or not self._p:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected kex init msg')

        self._e = packet.get_mpint()
        packet.check_end()

        self._send_reply(MSG_KEXDH_REPLY)

    def _process_reply(self, pkttype, packet):
        if self._conn.is_server():
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected kex reply msg')

        host_key = packet.get_string()
        self._f = packet.get_mpint()
        sig = packet.get_string()
        packet.check_end()

        self._verify_reply(host_key, sig)

    packet_handlers = {
        MSG_KEXDH_INIT:     _process_init,
        MSG_KEXDH_REPLY:    _process_reply
    }


class _KexDHGex(_KexDH):
    """Handler for Diffie-Hellman group exchange"""

    def __init__(self, alg, conn, hash):
        Kex.__init__(self, alg, conn, hash)

        self._p = 0

        if conn.is_client():
            self._request = UInt32(KEX_DH_GEX_MIN_SIZE) + \
                            UInt32(KEX_DH_GEX_PREFERRED_SIZE) + \
                            UInt32(KEX_DH_GEX_MAX_SIZE)

            conn._send_packet(Byte(MSG_KEX_DH_GEX_REQUEST), self._request)

    def _compute_hash(self, host_key_data, k):
        hash = self._hash()
        hash.update(String(self._conn._client_version))
        hash.update(String(self._conn._server_version))
        hash.update(String(self._conn._client_kexinit))
        hash.update(String(self._conn._server_kexinit))
        hash.update(String(host_key_data))
        hash.update(self._request)
        hash.update(MPInt(self._p))
        hash.update(MPInt(self._g))
        hash.update(MPInt(self._e))
        hash.update(MPInt(self._f))
        hash.update(MPInt(k))
        return hash.digest()

    def _process_request(self, pkttype, packet):
        if self._conn.is_client():
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected kex request msg')

        self._request = packet.get_remaining_payload()

        if pkttype == MSG_KEX_DH_GEX_REQUEST_OLD:
            min = KEX_DH_GEX_MIN_SIZE
            n = packet.get_uint32()
            max = KEX_DH_GEX_MAX_SIZE
        else:
            min = packet.get_uint32()
            n = packet.get_uint32()
            max = packet.get_uint32()

        packet.check_end()

        # TODO: For now, just select between group1 and group14 primes
        #       based on the requested group size

        if n <= 1024:
            self._p, self._g = _group1_p, _group1_g
        else:
            self._p, self._g = _group14_p, _group14_g

        self._q = (self._p - 1) // 2

        self._conn._send_packet(Byte(MSG_KEX_DH_GEX_GROUP), MPInt(self._p),
                                MPInt(self._g))

    def _process_group(self, pkttype, packet):
        if self._conn.is_server():
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected kex group msg')

        self._p = packet.get_mpint()
        self._g = packet.get_mpint()
        packet.check_end()

        self._q = (self._p - 1) // 2

        self._send_init(MSG_KEX_DH_GEX_INIT)

    def _process_init(self, pkttype, packet):
        if self._conn.is_client() or not self._p:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected kex init msg')

        self._e = packet.get_mpint()
        packet.check_end()

        self._send_reply(MSG_KEX_DH_GEX_REPLY)

    def _process_reply(self, pkttype, packet):
        if self._conn.is_server() or not self._p:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected kex reply msg')

        host_key = packet.get_string()
        self._f = packet.get_mpint()
        sig = packet.get_string()
        packet.check_end()

        self._verify_reply(host_key, sig)

    packet_handlers = {
        MSG_KEX_DH_GEX_REQUEST_OLD: _process_request,
        MSG_KEX_DH_GEX_GROUP:       _process_group,
        MSG_KEX_DH_GEX_INIT:        _process_init,
        MSG_KEX_DH_GEX_REPLY:       _process_reply,
        MSG_KEX_DH_GEX_REQUEST:     _process_request
    }


register_kex_alg(b'diffie-hellman-group-exchange-sha256', _KexDHGex, sha256)
register_kex_alg(b'diffie-hellman-group-exchange-sha1',   _KexDHGex, sha1)
register_kex_alg(b'diffie-hellman-group14-sha1',          _KexDH,    sha1,
                 _group14_g, _group14_p)
register_kex_alg(b'diffie-hellman-group1-sha1',           _KexDH,    sha1,
                 _group1_g,  _group1_p)
