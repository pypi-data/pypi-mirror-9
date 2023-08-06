"""
Process /etc/openssl/cert.pem file on OSX
"""

import OpenSSL

from datetime import datetime, timedelta

CERTS_FILE = '/etc/openssl/cert.pem'

SUBJECT_COMPONENT_ORDER = ( 'C', 'L', 'ST', 'O', 'OU', 'CN', 'EMAILADDRESS', 'MAIL', 'SERIALNUMBER', )

DATE_FORMATS = (
    '%Y%m%d%H%M%SZ',
    '%Y%m%d%H%M%S%Z',
)


class X509CertificateExtension(object):
    def __init__(self, certificate, index):
        self.certificate = certificate
        self.extension = certificate.x509.get_extension(index)

    @property
    def name(self):
        return self.extension.get_short_name()

    @property
    def critical(self):
        return self.extension.get_critical() == 1

    @property
    def data(self):
        # TODO - returns unprocessed ASN.1 data - parse it...
        return self.extension.get_data()

class X509Certificate(object):
    def __init__(self, data, filetype=OpenSSL.crypto.FILETYPE_PEM):
        self.x509 = OpenSSL.crypto.load_certificate(filetype, data)
        self.extensions = [X509CertificateExtension(self, i) for i in range(0, self.x509.get_extension_count())]

        self.subject_string = self.__parse_components__(self.x509.get_subject())
        self.issuer_string = self.__parse_components__(self.x509.get_issuer())

    def __parse_components__(self, value):
        if value is None:
            return None
        parts = dict(value.get_components())
        ordered_parts = []
        for k in SUBJECT_COMPONENT_ORDER:
            if k in parts.keys():
                ordered_parts.append((k, parts[k]))
        for k in parts.keys():
            if k not in SUBJECT_COMPONENT_ORDER:
                ordered_parts.append((k, parts[k]))
        return '/'.join('%s=%s' % (k,v) for k,v in ordered_parts)

    def __cmp__(self, other):
        if self.subject_string.lower() != other.subject_string.lower():
            return cmp(self.subject_string.lower(), other.subject_string.lower())

        for k in ('notbefore', 'expires', ):
            a = getattr(self, k)
            b = getattr(other, k)
            if a != b:
                return cmp(a, b)

        return 0

    def __repr__(self):
        return '%s' % self.subject

    def __parse_date__(self, value):
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass
        raise ValueError('Error parsing date %s' % value)

    @property
    def serialnumber(self):
        return self.x509.get_serial_number()

    @property
    def subject(self):
        return self.subject_string

    @property
    def issuer(self):
        return self.issuer_string

    @property
    def is_valid(self):
        now = datetime.now()
        return now >= self.notbefore and now <= self.expires

    @property
    def notbefore(self):
        value = self.x509.get_notBefore()
        if value is not None:
            try:
                value = self.__parse_date__(value)
            except ValueError, emsg:
                raise ValueError(emsg)
        return value

    @property
    def expires(self):
        value = self.x509.get_notAfter()
        if value is not None:
            try:
                value = self.__parse_date__(value)
            except ValueError, emsg:
                raise ValueError(emsg)
        return value


class OpenSSLCertificateList(list):
    def __init__(self, path=CERTS_FILE):
        self.path = path
        self.load(path)

    def __parse_certificates__(self, fd):
        certificate = ''
        for line in fd.readlines():
            certificate += line
            if line.rstrip() == '-----END CERTIFICATE-----':
                if certificate is not None:
                    yield X509Certificate(certificate.rstrip())
                    certificate = ''

    def load(self, path):
        with open(path, 'rb') as fd:
            for entry in self.__parse_certificates__(fd):
                self.append(entry)
        self.sort()

for certificate in OpenSSLCertificateList():
    print certificate.subject
    #print '  ', certificate.issuer
    #print '    ', certificate.notbefore, certificate.expires
