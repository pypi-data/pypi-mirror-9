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
import xmltodict
from collections import OrderedDict
from requests import Session
from exception import WSManException
from exception import AuthenticationException
from authentication import HttpCredSSPAuth
from authentication import HttpNtlmAuth


class Service(object):
    """
    SOAP Service
    """

    def __init__(self, endpoint, username, password, delegation=False, **kwargs):
        """
        # Kerberos authentication does not require a password if the MIT kerberos GSS-API mechanism already has a
        # valid service ticket for the WSMAN service on the target server. However if the callee wishes to use
        # credential delegation with Kerberos they must still provide a password (see Microsoft [MS-CSSP] Protocol)
        #
        # Credential delegation requires an authentication mechanism which provide message integrity and confidentiality
        # such as NTLM or Kerberos; basic authentication cannot be used.
        #
        # Kerberos requires the username in UPN (RFC xxxx) form. UPN or NetBIOS usernames can be used whith NTLM
        """
        self.session = Session()
        self.endpoint = endpoint
        self.session.auth = Service._determine_auth_mechanism(username, password, delegation)

    def invoke(self, headers, body):
        """
        Invokes the soap service
        """
        xml = Service._create_request(headers, body)
      #  try:
        response = self.session.post(self.endpoint, verify=False, data=xml)
    #    except Exception, e:
         #   b =e
      #      pass
      #  print response.content

        if response.status_code == 200:
            return Service._parse_response(response.content)

        if 500 < response.status_code >= 400:
            if response.status_code == 401:
                # auth denied
                raise AuthenticationException("")
            else:
                # another 40x
                raise AuthenticationException("")
        else:
            Service._parse_response(response.content)

    @staticmethod
    def _determine_auth_mechanism(username, password, delegation):
        """
        if the username contains at '@' sign we will use kerberos
        if the username contains a '/ we will use ntlm
        if the user does not contain either we will try ntlm, then basic
        either NTLM or Kerberos. In fact its basically always Negotiate.
        """
        if re.match('(.*)@(.+)', username) is not None:
            if delegation is True:
                raise Exception('Kerberos is not yet supported, specify the username in <domain>\<username> form for NTLM')
            else:
                raise Exception('Kerberos is not yet supported, specify the username in <domain>>\<username> form for NTLM')

        # check for NT format 'domain\username' a blank domain or username is invalid
        legacy = re.match('(.*)\\\\(.*)', username)
        if legacy is not None:
            if not legacy.group(1):
                raise Exception('Please specify the Windows domain for user in <domain>\<username> format')
            if not legacy.group(2):
                raise Exception('Please specify the Username of the user in <domain>\<username> format')
            if delegation is True:
                return HttpCredSSPAuth(legacy.group(1), legacy.group(2), password)
            else:
                return HttpNtlmAuth(legacy.group(1), legacy.group(2), password)

        # attempt NTLM (local account, not domain) - if username is '' then we try anonymous NTLM auth
        # as if anyone will configure that - uf!
        return HttpNtlmAuth('', username, password)

    @staticmethod
    def _create_request(headers, body):
        """
        Create the SOAP 1.2 Envelope
        An ordered dictionary is required to ensure the same order is reflected in the XML, otherwise the
        SOAP Body element would appear before the Header element.
        """
        envelope = OrderedDict()
        for (namespace, alias) in Service.Namespaces.iteritems():
            envelope['@xmlns:' + alias] = namespace
        envelope['soap:Header'] = headers
        envelope['soap:Body'] = body
        return xmltodict.unparse({'soap:Envelope': envelope}, encoding='utf-8')

    @staticmethod
    def _parse_response(xml):
        """
        Attempt to parse the SOAP response and return a python object
        Raise a WSManException if a Fault is found
        """
        try:
            soap_response = xmltodict.parse(xml, process_namespaces=True, namespaces=Service.Namespaces)
            body = soap_response['soap:Envelope']['soap:Body']
            if body is not None and 'Fault' in body:
                raise WSManException("SOAP Fault")
            return body
        except Exception, e:
            b =e
            raise WSManException("Invalid Soap Response")

Service.Avaliable_Mechanisms = ["basic", "ntlm", "kerberos"]
Service.Namespaces = {
    'http://www.w3.org/2003/05/soap-envelope': 'soap',
    'http://schemas.xmlsoap.org/ws/2004/08/addressing': 'a',
    'http://schemas.dmtf.org/wbem/wsman/1/cimbinding.xsd': 'b',
    'http://schemas.xmlsoap.org/ws/2004/09/enumeration': 'n',
    'http://schemas.xmlsoap.org/ws/2004/09/transfer': 'x',
    'http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd': 'w',
    'http://schemas.microsoft.com/wbem/wsman/1/wsman.xsd': 'p',
    'http://schemas.microsoft.com/wbem/wsman/1/windows/shell': 'rsp',
    'http://schemas.microsoft.com/wbem/wsman/1/config': 'cfg'
}
