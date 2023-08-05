# (c) 2015, Ian Clegg <ian.clegg@sourcewarp.com>
#
# winrmlib is licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
__author__ = 'ian.clegg@sourcewarp.com'

import re
import base64
import logging

from struct import pack, unpack, calcsize
from requests.auth import AuthBase

from ntlmlib.context import NtlmContext
from ntlmlib.structure import Structure
from ntlmlib.authentication import PasswordAuthentication

try:
    from Crypto.PublicKey import RSA
    from Crypto.Util.asn1 import DerSequence
    from Crypto.Util.asn1 import DerObject
    from Crypto.Cipher import ARC4
except ImportError:
    print "Unable to import Crypto, ensure the python 'pycrypto' package is correctly installed"

try:
    from OpenSSL import (
        SSL, _util)
    from OpenSSL.SSL import (
        Error, SysCallError, WantReadError, WantWriteError, ZeroReturnError)
    from OpenSSL.SSL import (
        Context, ContextType, Session, Connection, ConnectionType)
except ImportError:
    print "pyOpenSSL is not installed, can't continue"

log = logging.getLogger(__name__)

# TODO: Refactor GSS into an independent module
GSS_API_SPNEGO_UUID              = '\x2b\x06\x01\x05\x05\x02'
ASN1_SEQUENCE                    = 0x30
ASN1_SEQUENCE                    = 0x30
ASN1_AID                         = 0x60
ASN1_OID                         = 0x06
ASN1_OCTET_STRING                = 0x04
ASN1_MECH_TYPE                   = 0xa0
ASN1_MECH_TOKEN                  = 0xa2
ASN1_SUPPORTED_MECH              = 0xa1
ASN1_RESPONSE_TOKEN              = 0xa2
ASN1_ENUMERATED                  = 0x0a


class gss_channel_bindings_struct(Structure):
    structure = (
        ('initiator_addtype', '<L=0'),
        ('initiator_address_len', '<L=0'),
        ('initiator_address_ptr', '<L=0'),
        ('acceptor_addrtype', '<L=0'),
        ('acceptor_address_len', '<L=0'),
        ('acceptor_address_ptr', '<L=0'),
        ('application_data_len', '<L=0'),
        ('application_data_ptr', '<L=0'),
        ('initiator_address', ':'),
        ('acceptor_address', ':'),
        ('application_data', ':'),
    )

    def __init__(self):
        Structure.__init__(self)
        self['initiator_addtype'] = 0
        self['initiator_address_len'] = 0
        self['acceptor_addrtype'] = 0
        self['acceptor_address_len'] = 0
        self['application_data_len'] = 0
        self['initiator_address'] = ''
        self['acceptor_address'] = ''
        self['application_data'] = ''

    def getData(self):
        # Initialise the lengths of the fields before processing
        self.fields['initiator_address_len'] = len(self['initiator_address'])
        self.fields['acceptor_address_len'] = len(self['acceptor_address'])
        self.fields['application_data_len'] = len(self['application_data'])

        # Returns the data that should be used for Channel Binding Hashes
        # RFC412 section 4.1.1.2
        # (1) For purposes of MD5 hash computation, each integer field and
        # input length field SHALL be formatted into four octets, using
        # little-endian octet ordering (we are on intel?)
        # (2) All input length fields within gss_buffer_desc elements of a
        # gss_channel_bindings_struct even those which are zero-valued,
        # SHALL be included in the hash calculation.  The value elements of
        # gss_buffer_desc elements SHALL be de-referenced, and the resulting
        # data SHALL be included within the hash computation, only for the
        # case of gss_buffer_desc elements having non-zero length
        # specifiers.
        data = pack('<L', self.fields['initiator_addtype'])
        data += pack('<L', self.fields['initiator_address_len'])
        data += self.fields['initiator_address']

        data += pack('<L', self.fields['acceptor_addrtype'])
        data += pack('<L', self.fields['acceptor_address_len'])
        data += self.fields['acceptor_address']

        data += pack('<L', self.fields['application_data_len'])
        data += self.fields['application_data']
        return data

def asn1encode(data = ''):
        #res = asn1.SEQUENCE(str).encode()
        #import binascii
        #print '\nalex asn1encode str: %s\n' % binascii.hexlify(str)
        if len(data) >= 0 and len(data) <= 0x7F:
            res = pack('B', len(data)) + data
        elif len(data) >= 0x80 and len(data) <= 0xFF:
            res = pack('BB', 0x81, len(data)) + data
        elif len(data) >= 0x100 and len(data) <= 0xFFFF:
            res = pack('!BH', 0x82, len(data)) + data
        elif len(data) >= 0x10000 and len(data) <= 0xffffff:
            res = pack('!BBH', 0x83, len(data) >> 16, len(data) & 0xFFFF) + data
        elif len(data) >= 0x1000000 and len(data) <= 0xffffffff:
            res = pack('!BL', 0x84, len(data)) + data
        else:
            raise Exception('Error in asn1encode')
        return str(res)

def asn1decode(data = ''):
    len1 = unpack('B', data[:1])[0]
    data = data[1:]
    if len1 == 0x81:
        pad = calcsize('B')
        len2 = unpack('B',data[:pad])[0]
        data = data[pad:]
        ans = data[:len2]
    elif len1 == 0x82:
        pad = calcsize('H')
        len2 = unpack('!H', data[:pad])[0]
        data = data[pad:]
        ans = data[:len2]
    elif len1 == 0x83:
        pad = calcsize('B') + calcsize('!H')
        len2, len3 = unpack('!BH', data[:pad])
        data = data[pad:]
        ans = data[:len2 << 16 + len3]
    elif len1 == 0x84:
        pad = calcsize('!L')
        len2 = unpack('!L', data[:pad])[0]
        data = data[pad:]
        ans = data[:len2]
    # 1 byte length, string <= 0x7F
    else:
        pad = 0
        ans = data[:len1]
    return ans, len(ans) + pad + 1

class GSSAPI():
# Generic GSSAPI Header Format
    def __init__(self, data = None):
        self.fields = {}
        self['UUID'] = 0
        if data:
             self.fromString(data)
        pass

    def __setitem__(self,key,value):
        self.fields[key] = value

    def __getitem__(self, key):
        return self.fields[key]

    def __delitem__(self, key):
        del self.fields[key]

    def __len__(self):
        return len(self.getData())

    def __str__(self):
        return len(self.getData())

    def fromString(self, data = None):
       	# Manual parse of the GSSAPI Header Format
        # It should be something like
        # AID = 0x60 TAG, BER Length
        # OID = 0x06 TAG
        # GSSAPI OID
        # UUID data (BER Encoded)
        # Payload
        next_byte = unpack('B',data[:1])[0]
        if next_byte != ASN1_AID:
            raise Exception('Unknown AID=%x' % next_byte)
        data = data[1:]
        decode_data, total_bytes = asn1decode(data)
        # Now we should have a OID tag
       	next_byte = unpack('B',decode_data[:1])[0]
        if next_byte !=  ASN1_OID:
            raise Exception('OID tag not found %x' % next_byte)
        decode_data = decode_data[1:]
        # Now the OID contents, should be SPNEGO UUID
        uuid, total_bytes = asn1decode(decode_data)
        self['OID'] = uuid
        # the rest should be the data
        self['Payload'] = decode_data[total_bytes:]
        #pass

    def dump(self):
        for i in self.fields.keys():
            print "%s: {%r}" % (i,self[i])

    def getData(self):
        ans = pack('B',ASN1_AID)
        ans += asn1encode(
               pack('B',ASN1_OID) +
               asn1encode(self['UUID']) +
               self['Payload'])
        return ans

# TODO: These are CredSSP specific ASN1 structures and should be refactored without GSS
class TSPasswordCreds(GSSAPI):
# TSPasswordCreds ::= SEQUENCE {
#         domainName  [0] OCTET STRING,
#         userName    [1] OCTET STRING,
#         password    [2] OCTET STRING
# }
   def __init__(self, data=None):
       GSSAPI.__init__(self, data)
       del self['UUID']

   def getData(self):
       ans = pack('B', ASN1_SEQUENCE)
       ans += asn1encode( pack('B', 0xa0) +
              asn1encode( pack('B', ASN1_OCTET_STRING) +
              asn1encode( self['domain'].encode('utf-16le'))) +
              pack('B', 0xa1) +
              asn1encode( pack('B', ASN1_OCTET_STRING) +
              asn1encode( self['username'].encode('utf-16le'))) +
              pack('B', 0xa2) +
              asn1encode( pack('B', ASN1_OCTET_STRING) +
              asn1encode( self['password'].encode('utf-16le'))))
       return ans

class TSCredentials(GSSAPI):
# TSCredentials ::= SEQUENCE {
#        credType    [0] INTEGER,
#        credentials [1] OCTET STRING
# }
    def __init__(self, data=None):
        GSSAPI.__init__(self,data)
        del self['UUID']

    def getData(self):
        # Let's pack the credentials field
        credentials =  pack('B',0xa1)
        credentials += asn1encode(pack('B',ASN1_OCTET_STRING) +
                       asn1encode(self['credentials']))

        ans = pack('B',ASN1_SEQUENCE)
        ans += asn1encode( pack('B', 0xa0) +
            asn1encode( pack('B', 0x02) +
            asn1encode( pack('B', self['type']))) +
            credentials)
        return ans


class TSRequest(GSSAPI):
# TSRequest ::= SEQUENCE {
#	version     [0] INTEGER,
#       negoTokens  [1] NegoData OPTIONAL,
#       authInfo    [2] OCTET STRING OPTIONAL,
#	pubKeyAuth  [3] OCTET STRING OPTIONAL,
#}
#
# NegoData ::= SEQUENCE OF SEQUENCE {
#        negoToken [0] OCTET STRING
#}
#

    def __init__(self, data=None):
        GSSAPI.__init__(self,data)
        del self['UUID']

    def fromString(self, data = None):
        next_byte = unpack('B',data[:1])[0]
        if next_byte != ASN1_SEQUENCE:
            raise Exception('SEQUENCE expected! (%x)' % next_byte)
        data = data[1:]
        decode_data, total_bytes = asn1decode(data)

        next_byte = unpack('B',decode_data[:1])[0]
        if next_byte !=  0xa0:
            raise Exception('0xa0 tag not found %x' % next_byte)
        decode_data = decode_data[1:]
        next_bytes, total_bytes = asn1decode(decode_data)
        # The INTEGER tag must be here
        if unpack('B',next_bytes[0])[0] != 0x02:
            raise Exception('INTEGER tag not found %r' % next_byte)
        next_byte, _ = asn1decode(next_bytes[1:])
        self['Version'] = unpack('B',next_byte)[0]
        decode_data = decode_data[total_bytes:]
        next_byte = unpack('B',decode_data[:1])[0]
        if next_byte == 0xa1:
            # We found the negoData token
            decode_data, total_bytes = asn1decode(decode_data[1:])

            next_byte = unpack('B',decode_data[:1])[0]
            if next_byte != ASN1_SEQUENCE:
                raise Exception('ASN1_SEQUENCE tag not found %r' % next_byte)
            decode_data, total_bytes = asn1decode(decode_data[1:])

            next_byte = unpack('B',decode_data[:1])[0]
            if next_byte != ASN1_SEQUENCE:
                raise Exception('ASN1_SEQUENCE tag not found %r' % next_byte)
            decode_data, total_bytes = asn1decode(decode_data[1:])

            next_byte = unpack('B',decode_data[:1])[0]
            if next_byte != 0xa0:
                raise Exception('0xa0 tag not found %r' % next_byte)
            decode_data, total_bytes = asn1decode(decode_data[1:])

            next_byte = unpack('B',decode_data[:1])[0]
            if next_byte != ASN1_OCTET_STRING:
                raise Exception('ASN1_OCTET_STRING tag not found %r' % next_byte)
            decode_data2, total_bytes = asn1decode(decode_data[1:])
            # the rest should be the data
            self['negoTokens'] = decode_data2
            decode_data = decode_data[total_bytes+1:]

        if next_byte == 0xa2:
            # ToDo: Check all this
            # We found the authInfo token
            decode_data, total_bytes = asn1decode(decode_data[1:])
            next_byte = unpack('B',decode_data[:1])[0]
            if next_byte != ASN1_OCTET_STRING:
                raise Exception('ASN1_OCTET_STRING tag not found %r' % next_byte)
            decode_data2, total_bytes = asn1decode(decode_data[1:])
            self['authInfo'] = decode_data2
            decode_data = decode_data[total_bytes+1:]

        if next_byte == 0xa3:
            # ToDo: Check all this
            # We found the pubKeyAuth token
            decode_data, total_bytes = asn1decode(decode_data[1:])
            next_byte = unpack('B',decode_data[:1])[0]
            if next_byte != ASN1_OCTET_STRING:
                raise Exception('ASN1_OCTET_STRING tag not found %r' % next_byte)
            decode_data2, total_bytes = asn1decode(decode_data[1:])
            self['pubKeyAuth'] = decode_data2

    def getData(self):
        # Do we have pubKeyAuth?
        if self.fields.has_key('pubKeyAuth'):
            pubKeyAuth = pack('B',0xa3)
            pubKeyAuth += asn1encode(pack('B', ASN1_OCTET_STRING) + asn1encode(self['pubKeyAuth']))
        else:
            pubKeyAuth = ''

        if self.fields.has_key('authInfo'):
            authInfo = pack('B',0xa2)
            authInfo+= asn1encode(pack('B', ASN1_OCTET_STRING) +
                       asn1encode(self['authInfo']))
        else:
            authInfo = ''

        if self.fields.has_key('negoTokens'):
            negoData = pack('B',0xa1)
            negoData += asn1encode(pack('B', ASN1_SEQUENCE) +
                        asn1encode(pack('B', ASN1_SEQUENCE) +
                        asn1encode(pack('B', 0xa0) +
                        asn1encode(pack('B', ASN1_OCTET_STRING) +
                        asn1encode(self['negoTokens'])))))
        else:
            negoData = ''

        ans = pack('B', ASN1_SEQUENCE)
        ans += asn1encode(pack('B',0xa0) +
            # credssp version (Integer type is 0x02, version is 0x02)
            asn1encode(pack('B',0x02) + asn1encode(pack('B',0x02))) +
            # credssp version 2
            negoData + authInfo + pubKeyAuth)

        return ans


# TODO: NTLM is encryption is not supported
# TODO: You should use HTTPS to get Transport security
# TODO: RUN: winrm set winrm/config/service @{AllowUnencrypted="true"}
class HttpNtlmAuth(AuthBase):
    # NTLM Negotiate Request
    def __init__(self, domain, username, password, session=None):
        # TODO: What about the domain?
        domain = "SERVER2012"
        self.username = username
        self.password = password
        self.domain = domain
        self.ntlm_regex = re.compile('(?:.*,)*\s*Negotiate\s*([^,]*),?', re.I)

    def _get_ntlm_header(self, response):
        authreq = response.headers.get('www-authenticate', None)
        if authreq:
            match_obj = self.ntlm_regex.search(authreq)
            if match_obj and len(match_obj.group(1)) > 0:
                encoded = match_obj.group(1)
                return base64.b64decode(encoded)
        return None

    @staticmethod
    def _set_ntlm_header(request, value):
        request.headers['Authorization'] = "Negotiate {0}".format(base64.b64encode(value))
        return request

    @staticmethod
    def _encrypt(request, context):
        plaintext_body = request.body
        encrypted_body = context.wrap_message(plaintext_body)

        request.headers['Content-Type'] = 'multipart/encrypted;protocol="application/HTTP-SPNEGO-session-encrypted";boundary="Encrypted Boundary"'
        body = ''
        body += '--Encrypted Boundary\r\n'
        body += ' Content-Type: application/HTTP-SPNEGO-session-encrypted\r\n'
        body += ' OriginalContent: type=application/soap+xml;charset=UTF-8;Length='
        body += str(len(plaintext_body))
        body += '\r\n--Encrypted Boundary\r\n'
        body += 'Content-Type: application/octet-stream\r\n'
        body += '\x10\x00\x00\x00'  # length of NTLM signature as 32bit word
        body += encrypted_body
        body += '--Encrypted Boundary--\r\n'
        request.body = body
        request.headers['Content-Length'] = str(len(body))
        return request

    def _ntlm_processor(self):
        response = (yield)
        context = self._get_ntlm_header(response)

        if context is None:
            # NTLM Negotiate Request
            context = NtlmContext(PasswordAuthentication(self.domain, self.username, self.password), session_security='encrypt')
            context_generator = context.initialize_security_context()

            negotiate_token = context_generator.send(None)
            http_response = yield self._set_ntlm_header(response.request, negotiate_token)

            challenge_response = self._get_ntlm_header(http_response)
            if challenge_response is None:
                raise Exception("failed")

            authenticate = context_generator.send(challenge_response)
            #self._set_ntlm_header(response.request, authenticate)
            #http_response = yield self._encrypt(response.request, context)
            http_response = yield self._set_ntlm_header(response.request, authenticate)

            if self._get_ntlm_header(http_response) is None:
                raise Exception('Authentication Failed')

    def handle_401(self, response, **kwargs):
        ntlm_processor = self._ntlm_processor()
        next(ntlm_processor)

        while response.status_code == 401:
            # This is required
            response.content
            response.raw.release_conn()
            client_request = ntlm_processor.send(response)
            response = response.connection.send(client_request, **kwargs)

        return response

    def handle_other(self, response, **kwargs):
        return response

    def handle_response(self, response, **kwargs):
        #if self.pos is not None:
            # Rewind the file position indicator of the body to where
            # it was to resend the request.
        #    response.request.body.seek(self.pos)

        if response.status_code == 401:
            _r = self.handle_401(response, **kwargs)
            log.debug("handle_response(): returning {0}".format(_r))
            return _r
        else:
            _r = self.handle_other(response, **kwargs)
            log.debug("handle_response(): returning {0}".format(_r))
            return _r

    def __call__(self, request):
        request.headers["Connection"] = "Keep-Alive"
        request.headers["Content-Type"] = "application/soap+xml;charset=UTF-8"

        request.register_hook('response', self.handle_response)
        return request



class HttpCredSSPAuth(AuthBase):
    def __init__(self, domain, username, password):
        # TODO: What about the domain?
        self.domain = domain
        self.username = username
        self.password = password
        self.credssp_regex = re.compile('(?:.*,)*\s*CredSSP\s*([^,]*),?', re.I)
        self.tls_credssp_context = SSL.Context(SSL.TLSv1_METHOD)
        # The cipher suites for CredSSP TLS session do not appear to be explicitly
        # documented. Inspection of the Microsoft SChannel implementation on Windows
        # 2012 R2 revels that RC4-SHA must be specified
        self.tls_credssp_context.set_cipher_list('RC4-SHA')

    def _get_credssp_header(self, response):
        authenticate_header = response.headers.get('www-authenticate', None)
        if authenticate_header:
            match_obj = self.credssp_regex.search(authenticate_header)
            if match_obj and len(match_obj.group(1)) > 0:
                encoded = match_obj.group(1)
                return base64.b64decode(encoded)
        return None

    @staticmethod
    def _set_credssp_header(request, value):
        request.headers['Authorization'] = "CredSSP {0}".format(base64.b64encode(value))
        return request

    @staticmethod
    def _get_rsa_public_key(cert):
        """
        PyOpenSSL does not provide a public method to export the public key from a certificate as a properly formatted
        ASN.1 RSAPublicKey structure. There are 'hacks' which use dump_privatekey(crypto.FILETYPE_ASN1, <public_key>),
        but this dumps the public key within a PrivateKeyInfo structure which is not suitable for a comparison. This
        approach uses the PyOpenSSL CFFI bindings to invoke the i2d_RSAPublicKey() which correctly extracts the key
        material in an ASN.1 RSAPublicKey structure.
        :param cert: The ASN.1 Encoded Certificate
        :return: The ASN.1 Encoded RSAPublicKey structure containing the supplied certificates public Key
        """
        openssl_pkey = cert.get_pubkey()
        openssl_lib = _util.binding.lib
        ffi = _util.binding.ffi
        buf = ffi.new("unsigned char **")
        rsa = openssl_lib.EVP_PKEY_get1_RSA(openssl_pkey._pkey)
        length = openssl_lib.i2d_RSAPublicKey(rsa, buf)
        public_key = ffi.buffer(buf[0], length)[:]
        ffi.gc(buf[0], openssl_lib.OPENSSL_free)
        return public_key


    def _credssp_processor(self):
        """
        Implements a state machine
        :return:
        """
        response = (yield)
        context = self._get_credssp_header(response)

        # 1. First, secure the channel with a RC4-SHA TLS Handshake
        if context is None:
            tls_credssp = SSL.Connection(self.tls_credssp_context)
            tls_credssp.set_connect_state()
            while True:
                try:
                    tls_credssp.do_handshake()
                except SSL.WantReadError:
                    response = yield self._set_credssp_header(response.request, tls_credssp.bio_read(4096))
                    context = self._get_credssp_header(response)
                    if context is None:
                        raise Exception('TLS Handshake error')
                    tls_credssp.bio_write(context)
                else:
                    break

        # 2. Send an TSRequest containing an NTLM Negotiate Request
        context = NtlmContext(PasswordAuthentication(self.domain, self.username, self.password), session_security='encrypt')
        context_generator = context.initialize_security_context()
        negotiate_token = context_generator.send(None)

        ts_request = TSRequest()
        ts_request['negoTokens'] = negotiate_token
        tls_credssp.send(ts_request.getData())

        http_challenge_response = yield self._set_credssp_header(response.request, tls_credssp.bio_read(4096))

        # Extract and decrypt the encoded TSRequest response struct from the Negotiate header
        authenticate_header = self._get_credssp_header(http_challenge_response)
        if authenticate_header is None:
            raise Exception("failed")
        tls_credssp.bio_write(authenticate_header)

        # NTLM Challenge Response and Server Public Key Validation
        ts_request.fromString(tls_credssp.recv(8192))
        challenge_token = ts_request['negoTokens']
        server_cert = tls_credssp.get_peer_certificate()
        certificate_digest = base64.b16decode(server_cert.digest('SHA256').replace(':', ''))

        channel_binding_structure = gss_channel_bindings_struct()
        channel_binding_structure['application_data'] = "tls-server-end-point:" + certificate_digest
        public_key = HttpCredSSPAuth._get_rsa_public_key(server_cert)

        # The RSAPublicKey must be 'wrapped' using the negotiated GSSAPI mechanism and send to the server along with
        # the final SPNEGO token. This step of the CredSSP protocol is designed to thwart 'man-in-the-middle' attacks

        # Build and encrypt the response to the server
        ts_request = TSRequest()
        ts_request['negoTokens'] = context_generator.send(challenge_token)
        ts_request['pubKeyAuth'] = context.wrap_message(public_key)

        tls_credssp.send(ts_request.getData())
        enc_type3 = tls_credssp.bio_read(8192)
        auth_response = yield self._set_credssp_header(response.request, enc_type3)
        # authentciated!

        # 4. Send the Credentials to be delegated, these are encrypted with both NTLM v2 and then by TLS
        tsp = TSPasswordCreds()
        tsp['domain'] = self.domain
        tsp['username'] = self.username
        tsp['password'] = self.password

        tsc = TSCredentials()
        tsc['type'] = 1
        tsc['credentials'] = tsp.getData()

        ts_request = TSRequest()
        ts_request['authInfo'] = context.wrap_message(tsc.getData())

        tls_credssp.send(ts_request.getData())
        final = tls_credssp.bio_read(8192)
        http_response = yield self._set_credssp_header(response.request, final)

        if self._get_credssp_header(http_response) is None:
                raise Exception('Authentication Failed')

    def handle_401(self, response, **kwargs):
        credssp_processor = self._credssp_processor()
        next(credssp_processor)

        while response.status_code == 401:
            # This is required
            response.content
            response.raw.release_conn()
            client_request = credssp_processor.send(response)
            response = response.connection.send(client_request, **kwargs)

        return response

    def handle_other(self, response, **kwargs):
        return response

    def handle_response(self, response, **kwargs):
        #if self.pos is not None:
            # Rewind the file position indicator of the body to where
            # it was to resend the request.
        #    response.request.body.seek(self.pos)

        if response.status_code == 401:
            _r = self.handle_401(response, **kwargs)
            log.debug("handle_response(): returning {0}".format(_r))
            return _r
        else:
            _r = self.handle_other(response, **kwargs)
            log.debug("handle_response(): returning {0}".format(_r))
            return _r

    def __call__(self, request):
        request.headers["Connection"] = "Keep-Alive"
        request.headers["Content-Type"] = "application/soap+xml;charset=UTF-8"

        request.register_hook('response', self.handle_response)
        return request