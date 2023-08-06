# -*- coding: utf-8 -*-
"""This module contains class objects for all supported DynDNS Record types

These DNS_Records should really only need to be created via a zone instance but
could also be created independently if passed valid zone, fqdn data
"""
from .errors import DynectInvalidArgumentError
from .session import DynectSession
from ..compat import force_unicode

__author__ = 'jnappi'
__all__ = ['DNSRecord', 'ARecord', 'AAAARecord', 'CERTRecord', 'CNAMERecord',
           'DHCIDRecord', 'DNAMERecord', 'DNSKEYRecord', 'DSRecord',
           'KEYRecord', 'KXRecord', 'LOCRecord', 'IPSECKEYRecord', 'MXRecord',
           'NAPTRRecord', 'PTRRecord', 'PXRecord', 'NSAPRecord', 'RPRecord',
           'NSRecord', 'SOARecord', 'SPFRecord', 'SRVRecord', 'TLSARecord',
           'TXTRecord']


class DNSRecord(object):
    """Base record object contains functionality to be used across all other
    record type objects
    """

    def __init__(self, zone, fqdn, create=True):
        super(DNSRecord, self).__init__()
        self._zone = zone
        self._fqdn = fqdn
        self._ttl = None
        self._record_type = None
        self._record_id = None
        self.create = create
        self.api_args = {'rdata': {}}

    def _create_record(self, api_args):
        """Make the API call to create the current record type

        :param api_args: arguments to be pased to the API call
        """
        if self.create:
            if not self._fqdn.endswith('.'):
                self._fqdn += '.'
            if not self._record_type.endswith('Record'):
                self._record_type += 'Record'
            uri = '/{}/{}/{}/'.format(self._record_type, self._zone,
                                      self._fqdn)
            response = DynectSession.get_session().execute(uri, 'POST',
                                                           api_args)
            self._build(response['data'])

    def _get_record(self, record_id):
        """Get an existing record object from the DynECT System

        :param record_id: The id of the record you would like to get
        """
        if self.create:
            if not self._fqdn.endswith('.'):
                self._fqdn += '.'
            if not self._record_type.endswith('Record'):
                self._record_type += 'Record'
            self._record_id = record_id
            uri = '/{}/{}/{}/{}/'.format(self._record_type, self._zone,
                                         self._fqdn, self._record_id)
            response = DynectSession.get_session().execute(uri, 'GET', {})
            self._build(response['data'])

    def _update_record(self, api_args):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        if not self._fqdn.endswith('.'):
            self._fqdn += '.'
        if not self._record_type.endswith('Record'):
            self._record_type += 'Record'
        uri = '/{}/{}/{}/{}/'.format(self._record_type, self._zone, self._fqdn,
                                     self._record_id)
        response = DynectSession.get_session().execute(uri, 'PUT', api_args)
        self._build(response['data'])

    def _build(self, data):
        for key, val in data.items():
            if key == 'rdata':
                for r_key, r_val in val.items():
                    setattr(self, '_' + r_key, r_val)
            else:
                setattr(self, '_' + key, val)

    def rdata(self):
        """Return a records rdata"""
        rdata = {}
        for key, val in self.__dict__.items():
            if key.startswith('_') and not hasattr(val, '__call__') \
                    and key != '_record_type' and key != '_record_id':
                if 'ttl' not in key and 'zone' not in key and 'fqdn' not in key:
                    rdata[key[1:]] = val
        return rdata

    @property
    def geo_node(self):
        return {'zone': self._zone, 'fqdn': self._fqdn}

    @property
    def geo_rdata(self):
        data = DNSRecord.rdata(self)
        return {x: data[x] for x in data if data[x] is not None}

    @property
    def rec_name(self):
        return self._record_type.replace('Record', '').lower()

    def delete(self):
        """Delete the current record"""
        api_args = {}
        if not self._fqdn.endswith('.'):
            self._fqdn += '.'
        if not self._record_type.endswith('Record'):
            self._record_type += 'Record'
        uri = '/{}/{}/{}/{}/'.format(self._record_type, self.zone, self.fqdn,
                                     self._record_id)
        DynectSession.get_session().execute(uri, 'DELETE', api_args)

    @property
    def zone(self):
        """Once the zone is set, it will be a read only property"""
        return self._zone

    @zone.setter
    def zone(self, value):
        pass

    @property
    def fqdn(self):
        """Once the fqdn is set, it will be a read only property"""
        return self._fqdn

    @fqdn.setter
    def fqdn(self, value):
        pass

    @property
    def record_id(self):
        """The unique ID of this record from the DynECT System"""
        return self._record_id

    @record_id.setter
    def record_id(self, value):
        pass

    @property
    def ttl(self):
        """The TTL for this record"""
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        """Set the value of this record's ttl property"""
        self._ttl = value
        self.api_args['ttl'] = self._ttl
        self._update_record(self.api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<{}>: {}').format(self._record_type, self._fqdn)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class ARecord(DNSRecord):
    """The IPv4 Address (A) Record forward maps a host name to an IPv4 address.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.ARecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param address: IPv4 address for the record
        :param ttl: TTL for this record
        """
        if 'create' in kwargs:
            super(ARecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'ARecord'
        else:
            super(ARecord, self).__init__(zone, fqdn)
            self._record_type = 'ARecord'
            self._ttl = self._address = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            else:
                self._post(*args, **kwargs)

    def _post(self, address, ttl=0):
        """Create a new :class:`~dyn.tm.records.ARecord` on the DynECT System
        """
        self._address = address
        self._ttl = ttl
        self.api_args = {'rdata': {'address': self._address},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.ARecord`'s rdata as a JSON blob
        """
        guts = super(ARecord, self).rdata()
        shell = {'a_rdata': guts}
        return shell

    @property
    def address(self):
        """Return the value of this record's address property"""
        return self._address

    @address.setter
    def address(self, value):
        """Set the value of this record's address property"""
        self._address = value
        if 'rdata' not in self.api_args:
            self.api_args['rdata'] = {}
        self.api_args['rdata']['address'] = self._address
        self._update_record(self.api_args)

    def __str__(self):
        """str override"""
        return '<ARecord>: {}'.format(self._address)

    def __repr__(self):
        """print override"""
        return '<ARecord>: {}'.format(self._address)


class AAAARecord(DNSRecord):
    """The IPv6 Address (AAAA) Record is used to forward map hosts to IPv6
    addresses and is the current IETF recommendation for this purpose.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.AAAARecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param address: IPv6 address for the record
        :param ttl: TTL for this record
        """
        if 'create' in kwargs:
            super(AAAARecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'AAAARecord'
        else:
            super(AAAARecord, self).__init__(zone, fqdn)
            self._record_type = 'AAAARecord'
            self._address = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            else:
                self._post(*args, **kwargs)

    def _post(self, address, ttl=0):
        """Create a new :class:`~dyn.tm.records.AAAARecord` on the DynECT
        System
        """
        self._address = address
        self._ttl = ttl
        self.api_args = {'rdata': {'address': self._address},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.AAAARecord`'s rdata as a JSON
        blob
        """
        guts = super(AAAARecord, self).rdata()
        shell = {'aaaa_rdata': guts}
        return shell

    @property
    def address(self):
        """Return the value of this record's address property"""
        return self._address

    @address.setter
    def address(self, value):
        """Set the value of this record's address property"""
        self._address = value
        self.api_args['rdata']['address'] = self._address
        self._update_record(self.api_args)

    def __str__(self):
        """str override"""
        return '<AAAARecord>: {}'.format(self._address)

    def __repr__(self):
        """print override"""
        return '<AAAARecord>: {}'.format(self._address)


class CERTRecord(DNSRecord):
    """The Certificate (CERT) Record may be used to store either public key
    certificates or Certificate Revocation Lists (CRL) in the zone file.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`~dyn.tm.records.CERTRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param format: Numeric value for the certificate type
        :param tag: Numeric value for the public key certificate
        :param algorithm: Public key algorithm number used to generate the
            certificate
        :param certificate: The public key certificate
        :param ttl: TTL for this record in seconds
        """
        if 'create' in kwargs:
            super(CERTRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'CERTRecord'
        else:
            super(CERTRecord, self).__init__(zone, fqdn)
            self._record_type = 'CERTRecord'
            self._format = self._tag = self._algorithm = None
            self._certificate = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif len(args) + len(kwargs) == 1:
                self._get_record(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, format, tag, algorithm, certificate, ttl=0):
        """Create a new :class:`~dyn.tm.records.CERTRecord` on the DynECT
        System
        """
        self._format = format
        self._tag = tag
        self._algorithm = algorithm
        self._certificate = certificate
        self._ttl = ttl
        self.api_args = {'rdata': {'format': self._format,
                                   'tag': self._tag,
                                   'algorithm': self._algorithm,
                                   'certificate': self._certificate},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.CERTRecord`'s rdata as a JSON
        blob
        """
        guts = super(CERTRecord, self).rdata()
        shell = {'cert_rdata': guts}
        return shell

    @property
    def format(self):
        """Numeric value for the certificate type."""
        return self._format

    @format.setter
    def format(self, value):
        self._format = value
        self.api_args['rdata']['format'] = self._format
        self._update_record(self.api_args)

    @property
    def tag(self):
        """Numeric value for the public key certificate"""
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value
        self.api_args['rdata']['tag'] = self._tag
        self._update_record(self.api_args)

    @property
    def algorithm(self):
        """Public key algorithm number used to generate the certificate"""
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        self._algorithm = value
        self.api_args['rdata']['algorithm'] = self._algorithm
        self._update_record(self.api_args)

    @property
    def certificate(self):
        """The public key certificate"""
        return self._certificate

    @certificate.setter
    def certificate(self, value):
        self._certificate = value
        self.api_args['rdata']['certificate'] = self._certificate
        self._update_record(self.api_args)


class CNAMERecord(DNSRecord):
    """The Canonical Name (CNAME) Records map an alias to the real or canonical
    name that may lie inside or outside the current zone.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.CNAMERecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param cname: Hostname
        :param ttl: TTL for this record
        """
        if 'create' in kwargs:
            super(CNAMERecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'CNAMERecord'
        else:
            super(CNAMERecord, self).__init__(zone, fqdn)
            self._record_type = 'CNAMERecord'
            self._cname = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            else:
                self._post(*args, **kwargs)

    def _post(self, cname, ttl=0):
        """Create a new :class:`~dyn.tm.records.CNAMERecord` on the DynECT
        System
        """
        self._cname = cname
        self._ttl = ttl
        self.api_args = {'rdata': {'cname': self._cname},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.CNAMERecord`'s rdata as a JSON
        blob
        """
        guts = super(CNAMERecord, self).rdata()
        shell = {'cname_rdata': guts}
        return shell

    @property
    def cname(self):
        """Hostname"""
        return self._cname

    @cname.setter
    def cname(self, value):
        self._cname = value
        self.api_args['rdata']['cname'] = self._cname
        self._update_record(self.api_args)

    def __eq__(self, other):
        """Equivalence override"""
        if isinstance(other, CNAMERecord):
            return self.cname == other.cname
        elif isinstance(other, str):
            return self.cname == other
        return False


class DHCIDRecord(DNSRecord):
    """The :class:`~dyn.tm.records.DHCIDRecord` provides a means by which DHCP
    clients or servers can associate a DHCP client's identity with a DNS name,
    so that multiple DHCP clients and servers may deterministically perform
    dynamic DNS updates to the same zone.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.DHCIDRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param digest: Base-64 encoded digest of DHCP data
        :param ttl: TTL for this record
        """
        if 'create' in kwargs:
            super(DHCIDRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'DHCIDRecord'
        else:
            super(DHCIDRecord, self).__init__(zone, fqdn)
            self._record_type = 'DHCIDRecord'
            self._digest = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif len(args) + len(kwargs) == 1:
                self._get_record(*args, **kwargs)
            elif 'digest' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) == 2:
                self._post(*args, **kwargs)

    def _post(self, digest, ttl=0):
        """Create a new :class:`~dyn.tm.records.DHCIDRecord` on the DynECT
        System
        """
        self._digest = digest
        self._ttl = ttl
        self.api_args = {'rdata': {'digest': self._digest},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.DHCIDRecord`'s rdata as a JSON
        blob
        """
        guts = super(DHCIDRecord, self).rdata()
        shell = {'dhcid_rdata': guts}
        return shell

    @property
    def digest(self):
        """Base-64 encoded digest of DHCP data"""
        return self._digest

    @digest.setter
    def digest(self, value):
        self._digest = value
        self.api_args['rdata']['digest'] = self._digest
        self._update_record(self.api_args)


class DNAMERecord(DNSRecord):
    """The Delegation of Reverse Name (DNAME) Record is designed to assist the
    delegation of reverse mapping by reducing the size of the data that must be
    entered. DNAME's are designed to be used in conjunction with a bit label but
    do not strictly require one. However, do note that without a bit label a
    DNAME is equivalent to a CNAME when used in a reverse-map zone file.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.DNAMERecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param dname: Target Hostname
        :param ttl: TTL for this record
        """
        if 'create' in kwargs:
            super(DNAMERecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'DNAMERecord'
        else:
            super(DNAMERecord, self).__init__(zone, fqdn)
            self._record_type = 'DNAMERecord'
            self._dname = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'dname' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) == 2:
                self._post(*args, **kwargs)

    def _post(self, dname, ttl=0):
        """Create a new :class:`~dyn.tm.records.DNAMERecord` on the DynECT
        System
        """
        self._dname = dname
        self._ttl = ttl
        self.api_args = {'rdata': {'dname': self._dname},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.DNAMERecord`'s rdata as a JSON
        blob
        """
        guts = super(DNAMERecord, self).rdata()
        shell = {'dname_rdata': guts}
        return shell

    @property
    def dname(self):
        """Target hostname"""
        return self._dname

    @dname.setter
    def dname(self, value):
        self._dname = value
        self.api_args['rdata']['dname'] = self._dname
        self._update_record(self.api_args)


class DNSKEYRecord(DNSRecord):
    """The DNSKEY Record describes the public key of a public key (asymmetric)
    cryptographic algorithm used with DNSSEC.nis. It is typically used to
    authenticate signed keys or zones.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`~dyn.tm.records.DNSKEYRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param protocol: Numeric value for protocol
        :param public_key: The public key for the DNSSEC signed zone
        :param algorithm: Numeric value representing the public key encryption
            algorithm which will sign the zone. Must be one of 1 (RSA-MD5), 2
            (Diffie-Hellman), 3 (DSA/SHA-1), 4 (Elliptic Curve), or
            5 (RSA-SHA-1)
        :param flags: Numeric value confirming this is the zone's DNSKEY
        :param ttl: TTL for this record. Use 0 for zone default
        """
        if 'create' in kwargs:
            super(DNSKEYRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'DNSKEYRecord'
        else:
            super(DNSKEYRecord, self).__init__(zone, fqdn)
            self._record_type = 'DNSKEYRecord'
            self._algorithm = self._flags = self._protocol = None
            self._public_key = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif len(args) + len(kwargs) == 1:
                self._get_record(*args, **kwargs)
            elif 'protocol' in kwargs or 'public_key' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, protocol, public_key, algorithm=5, flags=256,
              ttl=0):
        """Create a new :class:`~dyn.tm.records.DNSKEYRecord` on the DynECT
        System
        """
        valid = range(1, 6)
        if algorithm not in valid:
            raise DynectInvalidArgumentError('algorthim', algorithm, valid)
        self._algorithm = algorithm
        self._flags = flags
        self._protocol = protocol
        self._public_key = public_key
        self._ttl = ttl
        self.api_args = {'rdata': {'algorithm': self._algorithm,
                                   'flags': self._flags,
                                   'protocol': self._protocol,
                                   'public_key': self._public_key},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.DNSKEYRecord`'s rdata as a JSON
        blob
        """
        guts = super(DNSKEYRecord, self).rdata()
        shell = {'dnskey_rdata': guts}
        return shell

    @property
    def algorithm(self):
        """Public key encryption algorithm will sign the zone"""
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        self._algorithm = value
        self.api_args['rdata']['algorithm'] = self._algorithm
        self._update_record(self.api_args)

    @property
    def flags(self):
        """Numeric value confirming this is the zone's DNSKEY"""
        return self._flags

    @flags.setter
    def flags(self, value):
        self._flags = value
        self.api_args['rdata']['flags'] = self._flags
        self._update_record(self.api_args)

    @property
    def protocol(self):
        """Numeric value for protocol. Set to 3 for DNSSEC"""
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value
        self.api_args['rdata']['protocol'] = self._protocol
        self._update_record(self.api_args)

    @property
    def public_key(self):
        """The public key for the DNSSEC signed zone"""
        return self._public_key

    @public_key.setter
    def public_key(self, value):
        self._public_key = value
        self.api_args['rdata']['public_key'] = self._public_key
        self._update_record(self.api_args)


class DSRecord(DNSRecord):
    """The Delegation Signer (DS) record type is used in DNSSEC to create the
    chain of trust or authority from a signed parent zone to a signed child
    zone.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`~dyn.tm.records.DSRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param digest: The digest in hexadecimal form. 20-byte,
            hexadecimal-encoded, one-way hash of the DNSKEY record surrounded
            by parenthesis characters '(' & ')'
        :param keytag: The digest mechanism to use to verify the digest
        :param algorithm: Numeric value representing the public key encryption
            algorithm which will sign the zone. Must be one of 1 (RSA-MD5), 2
            (Diffie-Hellman), 3 (DSA/SHA-1), 4 (Elliptic Curve), or
            5 (RSA-SHA-1)
        :param digtype: the digest mechanism to use to verify the digest. Valid
            values are SHA1, SHA256
        :param ttl: TTL for this record. Use 0 for zone default
        """
        if 'create' in kwargs:
            super(DSRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'DSRecord'
        else:
            super(DSRecord, self).__init__(zone, fqdn)
            self._record_type = 'DSRecord'
            self._algorithm = self._digest = self._digtype = self._keytag = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif len(args) + len(kwargs) == 1:
                self._get_record(*args, **kwargs)
            elif 'digest' in kwargs or 'keytag' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, digest, keytag, algorithm=5, digtype=1, ttl=0):
        """Create a new :class:`~dyn.tm.records.DSRecord` on the DynECT System
        """
        self._digest = digest
        self._keytag = keytag
        valid = range(1, 6)
        if algorithm not in valid:
            raise DynectInvalidArgumentError('algorthim', algorithm, valid)
        self._algorithm = algorithm
        self._digtype = digtype
        self._ttl = ttl
        self.api_args = {'rdata': {'algorithm': self._algorithm,
                                   'digest': self._digest,
                                   'digtype': self._digtype,
                                   'keytag': self._keytag},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.DSRecord`'s rdata as a JSON blob
        """
        guts = super(DSRecord, self).rdata()
        shell = {'ds_rdata': guts}
        return shell

    @property
    def algorithm(self):
        """Identifies the encoding algorithm"""
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        self._algorithm = value
        self.api_args['rdata']['algorithm'] = self._algorithm
        self._update_record(self.api_args)

    @property
    def digest(self):
        """The digest in hexadecimal form. 20-byte, hexadecimal-encoded, 
        one-way hash of the DNSKEY record surrounded by parenthesis characters
        """
        return self._digest

    @digest.setter
    def digest(self, value):
        self._digest = value
        self.api_args['rdata']['digest'] = self._digest
        self._update_record(self.api_args)

    @property
    def digtype(self):
        """Identifies which digest mechanism to use to verify the digest"""
        return self._digtype

    @digtype.setter
    def digtype(self, value):
        self._digtype = value
        self.api_args['rdata']['digtype'] = self._digtype
        self._update_record(self.api_args)

    @property
    def keytag(self):
        """Identifies which digest mechanism to use to verify the digest"""
        return self._keytag

    @keytag.setter
    def keytag(self, value):
        self._keytag = value
        self.api_args['rdata']['keytag'] = self._keytag
        self._update_record(self.api_args)


class KEYRecord(DNSRecord):
    """"Public Key" (KEY) Records are used for the storage of public keys for
    use by multiple applications such as IPSec, SSH, etc..., as well as for use
    by DNS security methods including the original DNSSEC protocol. However,
    as of RFC3445 the use of :class:`~dyn.tm.records.KEYRecord`'s have been
    limited to use in DNS Security operations such as DDNS and zone transfer
    due to the difficulty of querying for specific uses.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`~dyn.tm.records.KEYRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param algorithm: Numeric value representing the public key encryption
            algorithm which will sign the zone. Must be one of 1 (RSA-MD5), 2
            (Diffie-Hellman), 3 (DSA/SHA-1), 4 (Elliptic Curve), or
            5 (RSA-SHA-1)
        :param flags: See RFC 2535 for information on KEY record flags
        :param protocol: Numeric identifier of the protocol for this KEY record
        :param public_key: The public key for this record
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(KEYRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'KEYRecord'
        else:
            super(KEYRecord, self).__init__(zone, fqdn)
            self._record_type = 'KEYRecord'
            self._algorithm = self._flags = self._protocol = None
            self._public_key = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif len(args) + len(kwargs) == 1:
                self._get_record(*args, **kwargs)
            elif 'algorithm' in kwargs or 'flags' in kwargs or 'protocol' in \
                    kwargs or 'public_key' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, algorithm, flags, protocol, public_key, ttl=0):
        """Create a new :class:`~dyn.tm.records.KEYRecord` on the DynECT System
        """
        valid = range(1, 6)
        if algorithm not in valid:
            raise DynectInvalidArgumentError('algorthim', algorithm, valid)
        self._algorithm = algorithm
        self._flags = flags
        self._protocol = protocol
        self._public_key = public_key
        self._ttl = ttl
        self.api_args = {'rdata': {'algorithm': self._algorithm,
                                   'flags': self._flags,
                                   'protocol': self._protocol,
                                   'public_key': self._public_key},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.KEYRecord`'s rdata as a JSON
        blob
        """
        guts = super(KEYRecord, self).rdata()
        shell = {'key_rdata': guts}
        return shell

    @property
    def algorithm(self):
        """Numeric identifier for algorithm used"""
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        self._algorithm = value
        self.api_args['rdata']['algorithm'] = self._algorithm
        self._update_record(self.api_args)

    @property
    def flags(self):
        """See RFC 2535 for information about Key record flags"""
        return self._flags

    @flags.setter
    def flags(self, value):
        self._flags = value
        self.api_args['rdata']['flags'] = self._flags
        self._update_record(self.api_args)

    @property
    def protocol(self):
        """Numeric identifier of the protocol for this KEY record"""
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value
        self.api_args['rdata']['protocol'] = self._protocol
        self._update_record(self.api_args)

    @property
    def public_key(self):
        """The public key for this record"""
        return self._public_key

    @public_key.setter
    def public_key(self, value):
        self._public_key = value
        self.api_args['rdata']['public_key'] = self._public_key
        self._update_record(self.api_args)


class KXRecord(DNSRecord):
    """The "Key Exchanger" (KX) Record type is provided with one or more
    alternative hosts.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`~dyn.tm.records.KXRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param exchange: Hostname that will act as the Key Exchanger. The
            hostname must have a :class:`~dyn.tm.records.CNAMERecord`, an
            :class:`~dyn.tm.records.ARecord` and/or an
            :class:`~dyn.tm.records.AAAARecord` associated with it
        :param preference: Numeric value for priority usage. Lower value takes
            precedence over higher value where two records of the same type
            exist on the zone/node
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(KXRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'KXRecord'
        else:
            super(KXRecord, self).__init__(zone, fqdn)
            self._record_type = 'KXRecord'
            self._exchange = self._preference = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif len(args) + len(kwargs) == 1:
                self._get_record(*args, **kwargs)
            elif 'exchange' in kwargs or 'preference' in \
                    kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, exchange, preference, ttl=0):
        """Create a new :class:`~dyn.tm.records.KXRecord` on the DynECT System
        """
        self._exchange = exchange
        self._preference = preference
        self._ttl = ttl
        self.api_args = {'rdata': {'exchange': self._exchange,
                                   'preference': self._preference},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.KXRecord`'s rdata as a JSON blob
        """
        guts = super(KXRecord, self).rdata()
        shell = {'kx_rdata': guts}
        return shell

    @property
    def exchange(self):
        """Hostname that will act as the Key Exchanger. The hostname must have 
        a CNAME record, an A Record and/or an AAAA record associated with it
        """
        return self._exchange

    @exchange.setter
    def exchange(self, value):
        self._exchange = value
        self.api_args['rdata']['exchange'] = self._exchange
        self._update_record(self.api_args)

    @property
    def preference(self):
        """Numeric value for priority usage. Lower value takes precedence over 
        higher value where two records of the same type exist on the zone/node
        """
        return self._preference

    @preference.setter
    def preference(self, value):
        self._preference = value
        self.api_args['rdata']['preference'] = self._preference
        self._update_record(self.api_args)


class LOCRecord(DNSRecord):
    """:class:`~dyn.tm.records.LOCRecord`'s allow for the definition of
    geographic positioning information associated with a host or service name.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`~dyn.tm.records.LOCRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param altitude: Measured in meters above sea level
        :param horiz_pre:
        :param latitude: Measured in degrees, minutes, and seconds with N/S
            indicator for North and South
        :param longitude: Measured in degrees, minutes, and seconds with E/W
            indicator for East and West
        :param size:
        :param version:
        :param vert_pre:
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(LOCRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'LOCRecord'
        else:
            super(LOCRecord, self).__init__(zone, fqdn)
            self._record_type = 'LOCRecord'
            self._altitude = self._latitude = self._longitude = None
            self._horiz_pre = self._size = self._vert_pre = None
            # Version is required to be 0
            self._version = 0
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'altitude' in kwargs or 'latitude' in \
                    kwargs or 'longitude' in kwargs or 'horiz_pre' in \
                    kwargs or 'size' in kwargs or 'vert_pre' in \
                    kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, altitude, latitude, longitude, horiz_pre=10000, size=1,
              vert_pre=10, ttl=0):
        """Create a new :class:`~dyn.tm.records.LOCRecord` on the DynECT System
        """
        self._altitude = altitude
        self._latitude = latitude
        self._longitude = longitude
        self._horiz_pre = horiz_pre
        self._size = size
        self._vert_pre = vert_pre
        self._ttl = ttl
        self.api_args = {'rdata': {'altitude': self._altitude,
                                   'horiz_pre': self._horiz_pre,
                                   'latitude': self._latitude,
                                   'longitude': self._longitude,
                                   'size': self._size,
                                   'version': self._version,
                                   'vert_pre': self._vert_pre},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.LOCRecord`'s rdata as a JSON
        blob
        """
        guts = super(LOCRecord, self).rdata()
        shell = {'loc_rdata': guts}
        return shell

    @property
    def altitude(self):
        """Measured in meters above sea level"""
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        self._altitude = value
        self.api_args['rdata']['altitude'] = self._altitude
        self._update_record(self.api_args)

    @property
    def latitude(self):
        """Measured in degrees, minutes, and seconds with N/S indicator for 
        North and South. Example: 45 24 15 N, where 45 = degrees, 24 = minutes, 
        15 = seconds
        """
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        self._latitude = value
        self.api_args['rdata']['latitude'] = self._latitude
        self._update_record(self.api_args)

    @property
    def longitude(self):
        """Measured in degrees, minutes, and seconds with E/W indicator for 
        East and West. Example 89 23 18 W, where 89 = degrees, 23 = minutes, 
        18 = seconds
        """
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        self._longitude = value
        self.api_args['rdata']['longitude'] = self._longitude
        self._update_record(self.api_args)

    @property
    def horiz_pre(self):
        """Defaults to 10,000 meters"""
        return self._horiz_pre

    @horiz_pre.setter
    def horiz_pre(self, value):
        self._horiz_pre = value
        self.api_args['rdata']['horiz_pre'] = self._horiz_pre
        self._update_record(self.api_args)

    @property
    def size(self):
        """Defaults to 1 meter"""
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self.api_args['rdata']['size'] = self._size
        self._update_record(self.api_args)

    @property
    def vert_pre(self):
        return self._vert_pre

    @vert_pre.setter
    def vert_pre(self, value):
        self._vert_pre = value
        self.api_args['rdata']['vert_pre'] = self._vert_pre
        self._update_record(self.api_args)

    @property
    def version(self):
        """Number of the representation. Must be zero (0)
        NOTE: Version has no setter, because it will never not be 0
        """
        return self._version


class IPSECKEYRecord(DNSRecord):
    """The IPSECKEY is used for storage of keys used specifically for IPSec
    oerations
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.IPSECKEYRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param precedence: Indicates priority among multiple IPSECKEYS. Lower
            numbers are higher priority
        :param gatetype: Gateway type. Must be one of 0, 1, 2, or 3
        :param algorithm: Public key's cryptographic algorithm and format. Must
            be one of 0, 1, or 2
        :param gateway: Gateway used to create IPsec tunnel. Based on Gateway
            type
        :param public_key: Base64 encoding of the public key. Whitespace is
            allowed
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(IPSECKEYRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'IPSECKEYRecord'
        else:
            super(IPSECKEYRecord, self).__init__(zone, fqdn)
            self.valid_gatetypes = range(0, 4)
            self.valid_algorithms = range(0, 3)
            self._record_type = 'IPSECKEYRecord'
            self._precedence = self._gatetype = self._algorithm = None
            self._gateway = self._public_key = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'precedence' in kwargs or 'gatetype' in \
                    kwargs or 'algorithm' in kwargs or 'gateway' in \
                    kwargs or 'public_key' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, precedence, gatetype, algorithm, gateway, public_key,
              ttl=0):
        """Create a new :class:`~dyn.tm.records.IPSECKEYRecord` on the DynECT
        System
        """
        self._precedence = precedence
        if gatetype not in self.valid_gatetypes:
            raise DynectInvalidArgumentError('gatetype', gatetype,
                                             self.valid_gatetypes)
        self._gatetype = gatetype
        if algorithm not in self.valid_algorithms:
            raise DynectInvalidArgumentError('algorithm', algorithm,
                                             self.valid_algorithms)
        self._algorithm = algorithm
        self._gateway = gateway
        self._public_key = public_key
        self._ttl = ttl
        self.api_args = {'rdata': {'precedence': self._precedence,
                                   'gatetype': self._gatetype,
                                   'algorithm': self._algorithm,
                                   'gateway': self._gateway,
                                   'public_key': self._public_key},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.IPSECKEYRecord`'s rdata as a
        JSON blob
        """
        guts = super(IPSECKEYRecord, self).rdata()
        shell = {'ipseckey_rdata': guts}
        return shell

    @property
    def precedence(self):
        """Indicates priority among multiple IPSECKEYS. Lower numbers are
        higher priority
        """
        return self._precedence

    @precedence.setter
    def precedence(self, value):
        self._precedence = value
        self.api_args['rdata']['precedence'] = self._precedence
        self._update_record(self.api_args)

    @property
    def gatetype(self):
        """Gateway type. Must be one of 0, 1, 2, or 3"""
        return self._gatetype

    @gatetype.setter
    def gatetype(self, value):
        self._gatetype = value
        self.api_args['rdata']['gatetype'] = self._gatetype
        self._update_record(self.api_args)

    @property
    def algorithm(self):
        """Public key's cryptographic algorithm and format"""
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        self._algorithm = value
        self.api_args['rdata']['algorithm'] = self._algorithm
        self._update_record(self.api_args)

    @property
    def gateway(self):
        """Gateway used to create IPsec tunnel. Based on Gateway type"""
        return self._gateway

    @gateway.setter
    def gateway(self, value):
        self._gateway = value
        self.api_args['rdata']['gateway'] = self._gateway
        self._update_record(self.api_args)

    @property
    def public_key(self):
        """Base64 encoding of the public key. Whitespace is allowed"""
        return self._public_key

    @public_key.setter
    def public_key(self, value):
        self._public_key = value
        self.api_args['rdata']['public_key'] = self._public_key
        self._update_record(self.api_args)


class MXRecord(DNSRecord):
    """The "Mail Exchanger" record type specifies the name and relative
    preference of mail servers for a Zone. Defined in RFC 1035
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.MXRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param exchange: Hostname of the server responsible for accepting mail
            messages in the zone
        :param preference: Numeric value for priority usage. Lower value takes
            precedence over higher value where two records of the same type
            exist on the zone/node.
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(MXRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'MXRecord'
        else:
            super(MXRecord, self).__init__(zone, fqdn)
            self._record_type = 'MXRecord'
            self._exchange = self._preference = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'exchange' in kwargs or 'preference' in \
                    kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) >= 1:
                self._post(*args, **kwargs)

    def _post(self, exchange, preference=10, ttl=0):
        """Create a new :class:`~dyn.tm.records.MXRecord` on the DynECT System
        """
        self._exchange = exchange
        self._preference = preference
        self._ttl = ttl
        self.api_args = {'rdata': {'exchange': self._exchange,
                                   'preference': self._preference},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.MXRecord`'s rdata as a JSON blob
        """
        guts = super(MXRecord, self).rdata()
        shell = {'mx_rdata': guts}
        return shell

    @property
    def exchange(self):
        """Hostname of the server responsible for accepting mail messages in 
        the zone
        """
        return self._exchange

    @exchange.setter
    def exchange(self, value):
        self._exchange = value
        self.api_args['rdata']['exchange'] = self._exchange
        self._update_record(self.api_args)

    @property
    def preference(self):
        """Numeric value for priority usage. Lower value takes precedence over 
        higher value where two records of the same type exist on the zone/node
        """
        return self._preference

    @preference.setter
    def preference(self, value):
        self._preference = value
        self.api_args['rdata']['preference'] = self._preference
        self._update_record(self.api_args)


class NAPTRRecord(DNSRecord):
    """Naming Authority Pointer Records are a part of the Dynamic Delegation
    Discovery System (DDDS). The NAPTR is a generic record that defines a `rule`
    that may be applied to private data owned by a client application."""

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.NAPTRRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param order: Indicates the required priority for processing NAPTR
            records. Lowest value is used first.
        :param preference: Indicates priority where two or more NAPTR records
            have identical order values. Lowest value is used first.
        :param services: Always starts with "e2u+" (E.164 to URI). After the
            e2u+ there is a string that defines the type and optionally the
            subtype of the URI where this :class:`~dyn.tm.records.NAPTRRecord`
            points.
        :param regexp: The NAPTR record accepts regular expressions
        :param replacement: The next domain name to find. Only applies if this
            :class:`~dyn.tm.records.NAPTRRecord` is non-terminal.
        :param flags: Should be the letter "U". This indicates that this NAPTR
            record terminal
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(NAPTRRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'NAPTRRecord'
        else:
            super(NAPTRRecord, self).__init__(zone, fqdn)
            self._record_type = 'NAPTRRecord'
            self._order = self._preference = self._flags = self._services = None
            self._regexp = self._replacement = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'order' in kwargs or 'preference' in kwargs or 'services' in \
                    kwargs or 'regexp' in kwargs or 'replacement' in \
                    kwargs or 'flags' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, order, preference, services, regexp, replacement,
              flags='U', ttl=0):
        """Create a new :class:`~dyn.tm.records.NAPTRRecord` on the DynECT
        System
        """
        self._order = order
        self._preference = preference
        self._flags = flags
        self._services = services
        self._regexp = regexp
        self._replacement = replacement
        self._ttl = ttl
        self.api_args = {'rdata': {'order': self._order,
                                   'preference': self._preference,
                                   'flags': self._flags,
                                   'services': self._services,
                                   'regexp': self._regexp,
                                   'replacement': self._replacement},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.NAPTRRecord`'s rdata as a JSON
        blob
        """
        guts = super(NAPTRRecord, self).rdata()
        shell = {'naptr_rdata': guts}
        return shell

    @property
    def order(self):
        """Indicates the required priority for processing NAPTR records. Lowest 
        value is used first
        """
        return self._order

    @order.setter
    def order(self, value):
        self._order = value
        self.api_args['rdata']['order'] = self._order
        self._update_record(self.api_args)

    @property
    def preference(self):
        """Indicates priority where two or more NAPTR records have identical 
        order values. Lowest value is used first.
        """
        return self._preference

    @preference.setter
    def preference(self, value):
        self._preference = value
        self.api_args['rdata']['preference'] = self._preference
        self._update_record(self.api_args)

    @property
    def flags(self):
        """Should be the letter "U". This indicates that this NAPTR record 
        terminal (E.164 number that maps directly to a URI)
        """
        return self._flags

    @flags.setter
    def flags(self, value):
        self._flags = value
        self.api_args['rdata']['flags'] = self._flags
        self._update_record(self.api_args)

    @property
    def services(self):
        """Always starts with "e2u+" (E.164 to URI). After the e2u+ there is a 
        string that defines the type and optionally the subtype of the URI 
        where this NAPTR record points
        """
        return self._services

    @services.setter
    def services(self, value):
        self._services = value
        self.api_args['rdata']['services'] = self._services
        self._update_record(self.api_args)

    @property
    def regexp(self):
        """The NAPTR record accepts regular expressions"""
        return self._regexp

    @regexp.setter
    def regexp(self, value):
        self._regexp = value
        self.api_args['rdata']['regexp'] = self._regexp
        self._update_record(self.api_args)

    @property
    def replacement(self):
        """The next domain name to find. Only applies if this NAPTR record is 
        non-terminal
        """
        return self._replacement

    @replacement.setter
    def replacement(self, value):
        self._replacement = value
        self.api_args['rdata']['replacement'] = self._replacement
        self._update_record(self.api_args)


class PTRRecord(DNSRecord):
    """Pointer Records are used to reverse map an IPv4 or IPv6 IP address to a
    host name
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`~dyn.tm.records.PTRRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param ptrdname: The hostname where the IP address should be directed
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(PTRRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'PTRRecord'
        else:
            super(PTRRecord, self).__init__(zone, fqdn)
            self._record_type = 'PTRRecord'
            self._ptrdname = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'ptrdname' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, ptrdname, ttl=0):
        """Create a new :class:`~dyn.tm.records.PTRRecord` on the DynECT System
        """
        self._ptrdname = ptrdname
        self._ttl = ttl
        self.api_args = {'rdata': {'ptrdname': self._ptrdname},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.PTRRecord`'s rdata as a JSON
        blob
        """
        guts = super(PTRRecord, self).rdata()
        shell = {'ptr_rdata': guts}
        return shell

    @property
    def ptrdname(self):
        """Hostname where the IP address should be directed"""
        return self._ptrdname

    @ptrdname.setter
    def ptrdname(self, value):
        self._ptrdname = value
        self.api_args['rdata']['ptrdname'] = self._ptrdname
        self._update_record(self.api_args)


class PXRecord(DNSRecord):
    """The X.400 to RFC 822 E-mail RR allows mapping of ITU X.400 format e-mail
    addresses to RFC 822 format e-mail addresses using a MIXER-conformant
    gateway.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.PXRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param preference: Sets priority for processing records of the same
            type. Lowest value is processed first.
        :param map822: mail hostname
        :param mapx400: The domain name derived from the X.400 part of MCGAM
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(PXRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'PXRecord'
        else:
            super(PXRecord, self).__init__(zone, fqdn)
            self._record_type = 'PXRecord'
            self._preference = self._map822 = self._mapx400 = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'preference' in kwargs or 'map822' in kwargs or 'mapx400' in \
                    kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, preference, map822, mapx400, ttl=0):
        """Create a new :class:`~dyn.tm.records.PXRecord` on the DynECT System
        """
        self._preference = preference
        self._map822 = map822
        self._mapx400 = mapx400
        self._ttl = ttl
        self.api_args = {'rdata': {'preference': self._preference,
                                   'map822': self._map822,
                                   'mapx400': self._mapx400},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.PXRRecord`'s rdata as a JSON
        blob
        """
        guts = super(PXRecord, self).rdata()
        shell = {'pxr_rdata': guts}
        return shell

    @property
    def preference(self):
        """Sets priority for processing records of the same type. Lowest value 
        is processed first
        """
        return self._preference

    @preference.setter
    def preference(self, value):
        self._preference = value
        self.api_args['rdata']['preference'] = self._preference
        self._update_record(self.api_args)

    @property
    def map822(self):
        """mail hostname"""
        return self._map822

    @map822.setter
    def map822(self, value):
        self._map822 = value
        self.api_args['rdata']['map822'] = self._map822
        self._update_record(self.api_args)

    @property
    def mapx400(self):
        """Enter the domain name derived from the X.400 part of MCGAM"""
        return self._mapx400

    @mapx400.setter
    def mapx400(self, value):
        self._mapx400 = value
        self.api_args['rdata']['mapx400'] = self._mapx400
        self._update_record(self.api_args)


class NSAPRecord(DNSRecord):
    """The Network Services Access Point record is the equivalent of an RR for
    ISO's Open Systems Interconnect (OSI) system in that it maps a host name to
    an endpoint address.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.PXRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param nsap: Hex-encoded NSAP identifier
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(NSAPRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'NSAPRecord'
        else:
            super(NSAPRecord, self).__init__(zone, fqdn)
            self._record_type = 'NSAPRecord'
            self._nsap = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'nsap' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, nsap, ttl=0):
        """Create a new :class:`~dyn.tm.records.NSAPRecord` on the DynECT
        System
        """
        self._nsap = nsap
        self._ttl = ttl
        self.api_args = {'rdata': {'nsap': self._nsap},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.NSAPRecord`'s rdata as a JSON
        blob
        """
        guts = super(NSAPRecord, self).rdata()
        shell = {'nsap_rdata': guts}
        return shell

    @property
    def nsap(self):
        """Hex-encoded NSAP identifier"""
        return self._nsap

    @nsap.setter
    def nsap(self, value):
        self._nsap = value
        self.api_args['rdata']['nsap'] = self._nsap
        self._update_record(self.api_args)


class RPRecord(DNSRecord):
    """The Respnosible Person record allows an email address and some optional
    human readable text to be associated with a host. Due to privacy and spam
    considerations, :class:`~dyn.tm.records.RPRecords` are not widely used on
    public servers but can provide very useful contact data during diagnosis
    and debugging network problems.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.RPRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param mbox: Email address of the Responsible Person.
        :param txtdname: Hostname where a TXT record exists with more
            information on the responsible person.
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(RPRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'RPRecord'
        else:
            super(RPRecord, self).__init__(zone, fqdn)
            self._record_type = 'RPRecord'
            self._mbox = self._txtdname = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'mbox' in kwargs or 'txtdname' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, mbox, txtdname, ttl=0):
        """Create a new :class:`~dyn.tm.records.RPRecord` on the DynECT System
        """
        if '@' in mbox:
            mbox = mbox.replace('@', '.')
        self._mbox = mbox
        self._txtdname = txtdname
        self._ttl = ttl
        self.api_args = {'rdata': {'mbox': self._mbox,
                                   'txtdname': self._txtdname},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.RPRecord`'s rdata as a JSON blob
        """
        guts = super(RPRecord, self).rdata()
        shell = {'rp_rdata': guts}
        return shell

    @property
    def mbox(self):
        """Email address of the Responsible Person. Data format: Replace @ 
        symbol with a dot '.' in the address
        """
        return self._mbox

    @mbox.setter
    def mbox(self, value):
        self._mbox = value
        self.api_args['rdata']['mbox'] = self._mbox
        self._update_record(self.api_args)

    @property
    def txtdname(self):
        """Hostname where a TXT record exists with more information on the 
        responsible person
        """
        return self._txtdname

    @txtdname.setter
    def txtdname(self, value):
        self._txtdname = value
        self.api_args['rdata']['txtdname'] = self._txtdname
        self._update_record(self.api_args)


class NSRecord(DNSRecord):
    """Nameserver Records are used to list all the nameservers that will respond
    authoritatively for a domain.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.NSRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param nsdname: Hostname of the authoritative Nameserver for the zone
        :param service_class: Hostname of the authoritative Nameserver for the
            zone
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(NSRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'NSRecord'
        else:
            super(NSRecord, self).__init__(zone, fqdn)
            self._record_type = 'NSRecord'
            self._nsdname = None
            self._service_class = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'nsdname' in kwargs or 'service_class' in \
                    kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, nsdname, service_class='', ttl=0):
        """Create a new :class:`~dyn.tm.records.NSRecord` on the DynECT System
        """
        self._nsdname = nsdname
        self._service_class = service_class
        self._ttl = ttl
        self.api_args = {'rdata': {'nsdname': self._nsdname},
                         'ttl': self._ttl,
                         'service_class': self._service_class}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.NSRecord`'s rdata as a JSON blob
        """
        guts = super(NSRecord, self).rdata()
        shell = {'ns_rdata': guts}
        return shell

    @property
    def nsdname(self):
        """Hostname of the authoritative Nameserver for the zone"""
        return self._nsdname

    @nsdname.setter
    def nsdname(self, value):
        self._nsdname = value
        self.api_args['rdata']['nsdname'] = self._nsdname
        self._update_record(self.api_args)

    @property
    def service_class(self):
        """Hostname of the authoritative Nameserver for the zone"""
        return self._service_class

    @service_class.setter
    def service_class(self, value):
        self._service_class = value
        api_args = {'rdata': {'nsdname': self._nsdname},
                    'service_class': self._service_class}
        self._update_record(api_args)


class SOARecord(DNSRecord):
    """The Start of Authority Record describes the global properties for the
    Zone (or domain). Only one SOA Record is allowed under a zone at any given
    time. NOTE: Dynect users do not have the permissions required to create or
    delete SOA records on the Dynect System.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.SOARecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        """
        if 'create' in kwargs:
            super(SOARecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'SOARecord'
        else:
            super(SOARecord, self).__init__(zone, fqdn)
            self._record_type = 'SOARecord'
            self._rname = self._serial_style = self._minimum = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif len(args) > 0:
                self._get_record(*args)
            else:
                # Users can not POST or DELETE SOA Records
                pass
            self.api_args = {'rdata': {'rname': self._rname}}

    def rdata(self):
        """Return this :class:`~dyn.tm.records.SOARecord`'s rdata as a JSON
        blob
        """
        guts = super(SOARecord, self).rdata()
        shell = {'soa_rdata': guts}
        return shell

    @property
    def rname(self):
        """Domain name which specifies the mailbox of the person responsible 
        for this zone
        """
        return self._rname

    @rname.setter
    def rname(self, value):
        self._rname = value
        self.api_args['rdata']['rname'] = self._rname
        self._update_record(self.api_args)

    @property
    def serial_style(self):
        """The style of the zone's serial"""
        return self._serial_style

    @serial_style.setter
    def serial_style(self, value):
        self._serial_style = value
        api_args = {'rdata': {'rname': self._rname},
                    'serial_style': self._serial_style}
        self._update_record(api_args)

    @property
    def minimum(self):
        """The minimum TTL for this :class:`~dyn.tm.records.SOARecord`"""
        return self._minimum

    @minimum.setter
    def minimum(self, value):
        self._minimum = value
        api_args = {'rdata': {'rname': self._rname, 'minimum': self._minimum}}
        self._update_record(api_args)

    @property
    def ttl(self):
        """The TTL for this record"""
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        """Set the value of this SOARecord's ttl property"""
        self._ttl = value
        api_args = {'rdata': {'rname': self._rname},
                    'ttl': self._ttl}
        self._update_record(api_args)

    def delete(self):
        """Users can not POST or DELETE SOA Records"""
        pass


class SPFRecord(DNSRecord):
    """Sender Policy Framework Records are used to allow a recieving Message
    Transfer Agent (MTA) to verify that the originating IP of an email from a
    sender is authorized to send main for the sender's domain.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.SPFRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param txtdata: Free text containing SPF record information
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(SPFRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'SPFRecord'
        else:
            super(SPFRecord, self).__init__(zone, fqdn)
            self._record_type = 'SPFRecord'
            self._txtdata = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'txtdata' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, txtdata, ttl=0):
        """Create a new :class:`~dyn.tm.records.SPFRecord` on the DynECT System
        """
        self._txtdata = txtdata
        self._ttl = ttl
        self.api_args = {'rdata': {'txtdata': self._txtdata},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.SPFRecord`'s rdata as a JSON
        blob
        """
        guts = super(SPFRecord, self).rdata()
        shell = {'spf_rdata': guts}
        return shell

    @property
    def txtdata(self):
        """Free text box containing SPF record information"""
        return self._txtdata

    @txtdata.setter
    def txtdata(self, value):
        self._txtdata = value
        self.api_args['rdata']['txtdata'] = self._txtdata
        self._update_record(self.api_args)


class SRVRecord(DNSRecord):
    """The Services Record type allow a service to be associated with a host
    name. A user or application that wishes to discover where a service is
    located can interrogate for the relevant SRV that describes the service.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a :class:`~dyn.tm.records.SRVRecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param port: Indicates the port where the service is running
        :param priority: Numeric value for priority usage. Lower value takes
            precedence over higher value where two records of the same type
            exist on the zone/node
        :param target: The domain name of a host where the service is running
            on the specified port
        :param weight: Secondary prioritizing of records to serve. Records of
            equal priority should be served based on their weight. Higher values
            are served more often
        :param ttl: TTL for the record. Set to 0 to use zone default
        """
        if 'create' in kwargs:
            super(SRVRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'SRVRecord'
        else:
            super(SRVRecord, self).__init__(zone, fqdn)
            self._record_type = 'SRVRecord'
            self._port = self._priority = self._target = self._weight = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'port' in kwargs or 'priority' in kwargs or 'target' in \
                    kwargs or 'weight' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) > 1:
                self._post(*args, **kwargs)

    def _post(self, port, priority, target, weight, ttl=0):
        """Create a new :class:`~dyn.tm.records.SRVRecord` on the DynECT System
        """
        self._port = port
        self._priority = priority
        self._target = target
        self._weight = weight
        self._ttl = ttl
        self.api_args = {'rdata': {'port': self._port,
                                   'priority': self._priority,
                                   'target': self._target,
                                   'weight': self._weight},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.SRVRecord`'s rdata as a JSON
        blob
        """
        guts = super(SRVRecord, self).rdata()
        shell = {'srv_rdata': guts}
        return shell

    @property
    def port(self):
        """Indicates the port where the service is running"""
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        self.api_args['rdata']['port'] = self._port
        self._update_record(self.api_args)

    @property
    def priority(self):
        """Numeric value for priority usage. Lower value takes precedence over 
        higher value where two records of the same type exist on the zone/node
        """
        return self._priority

    @priority.setter
    def priority(self, value):
        self._priority = value
        self.api_args['rdata']['priority'] = self._priority
        self._update_record(self.api_args)

    @property
    def target(self):
        """The domain name of a host where the service is running on the 
        specified `port`
        """
        return self._target

    @target.setter
    def target(self, value):
        self._target = value
        self.api_args['rdata']['target'] = self._target
        self._update_record(self.api_args)

    @property
    def weight(self):
        """Secondary prioritizing of records to serve. Records of equal 
        priority should be served based on their weight. Higher values are 
        served more often
        """
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value
        self.api_args['rdata']['weight'] = self._weight
        self._update_record(self.api_args)


class TLSARecord(DNSRecord):
    """The TLSA record is used to associate a TLS server
    certificate or public key with the domain name where the record is
    found, thus forming a "TLSA certificate association". Defined in RFC 6698
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create an :class:`~dyn.tm.records.TLSARecord` object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param cert_usage: Specifies the provided association that will be used
            to match the certificate presented in the TLS handshake. Example
            values: 0 (CA constraint), 1 (Service certificate constraint),
            2 (Trust anchor assertion ), 3 (Domain-issued certificate)
        :param selector: Specifies which part of the TLS certificate presented
            by the server will be matched against the association data. Example
            values: 0 (Full certificate), 1 (SubjectPublicKeyInfo)
        :param match_type: Specifies how the certificate association is
            presented. Example values: 0 (No hash used), 1 (SHA-256),
            2 (SHA-512)
        :param certificate: Full certificate or its SubjectPublicKeyInfo, or
            hash based on the matching type.
        :param ttl: TTL for the record in seconds
        """
        if 'create' in kwargs:
            super(TLSARecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'TLSARecord'
        else:
            super(TLSARecord, self).__init__(zone, fqdn)
            self._record_type = 'TLSARecord'
            self._cert_usage = self._selector = None
            self._mathc_type = self._certificate = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif len(args) + len(kwargs) == 1:
                self._get_record(*args, **kwargs)
            elif 'cert_usage' in kwargs or 'selector' in \
                    kwargs or 'match_type' in kwargs or \
                    'certificate' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) >= 1:
                self._post(*args, **kwargs)

    def _post(self, cert_usage, selector, match_type, certificate, ttl=0):
        """Create a new :class:`~dyn.tm.records.TLSARecord` on the DynECT System
        """
        self._ttl = ttl
        self._cert_usage = cert_usage
        self._selector = selector
        self._match_type = match_type
        self._certificate = certificate
        self.api_args = {'rdata': {'cert_usage': self._cert_usage,
                                   'selector': self._selector,
                                   'match_type': self._match_type,
                                   'certificate': self._certificate},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.TLSARecord`'s rdata as a JSON blob
        """
        guts = super(TLSARecord, self).rdata()
        shell = {'tlsa_rdata': guts}
        return shell

    @property
    def cert_usage(self):
        """Specifies the provided association that will be used
        to match the certificate presented in the TLS handshake
        """
        return self._cert_usage

    @cert_usage.setter
    def cert_usage(self, value):
        self._cert_usage = value
        self.api_args['rdata']['cert_usage'] = self._cert_usage
        self._update_record(self.api_args)
        
    @property
    def selector(self):
        """Specifies which part of the TLS certificate presented
        by the server will be matched against the association data.
        """
        return self._selector

    @selector.setter
    def selector(self, value):
        self._selector = value
        self.api_args['rdata']['selector'] = self._selector
        self._update_record(self.api_args)

    @property
    def match_type(self):
        """Specifies how the certificate association is presented.
        """
        return self._match_type

    @match_type.setter
    def match_type(self, value):
        self._match_type = value
        self.api_args['rdata']['match_type'] = self._match_type
        self._update_record(self.api_args)
        
    @property
    def certificate(self):
        """Full certificate or its SubjectPublicKeyInfo, or
        hash based on the matching type
        """
        return self._certificate

    @certificate.setter
    def certificate(self, value):
        self._certificate = value
        self.api_args['rdata']['certificate'] = self._certificate
        self._update_record(self.api_args)
 

class TXTRecord(DNSRecord):
    """The Text record type provides the ability to associate arbitrary text
    with a name. For example, it can be used to provide a description of the
    host, service contacts, or any other required system information.
    """

    def __init__(self, zone, fqdn, *args, **kwargs):
        """Create a new TXTRecord object

        :param zone: Name of zone where the record will be added
        :param fqdn: Name of node where the record will be added
        :param txtdata: Free form text for this
            :class:`~dyn.tm.records.TXTRecord`
        :param ttl: TTL for the record. Set to 0 to use zone default
        """
        if 'create' in kwargs:
            super(TXTRecord, self).__init__(zone, fqdn, kwargs['create'])
            del kwargs['create']
            self._build(kwargs)
            self._record_type = 'TXTRecord'
        else:
            super(TXTRecord, self).__init__(zone, fqdn)
            self._record_type = 'TXTRecord'
            self._txtdata = None
            if 'record_id' in kwargs:
                self._get_record(kwargs['record_id'])
            elif 'txtdata' in kwargs or 'ttl' in kwargs:
                self._post(*args, **kwargs)
            elif len(args) + len(kwargs) == 2:
                self._post(*args, **kwargs)

    def _post(self, txtdata, ttl=0):
        """Create a new :class:`~dyn.tm.records.TXTRecord` on the DynECT System
        """
        self._ttl = ttl
        self._txtdata = txtdata
        self.api_args = {'rdata': {'txtdata': self._txtdata},
                         'ttl': self._ttl}
        self._create_record(self.api_args)

    def rdata(self):
        """Return this :class:`~dyn.tm.records.TXTRecord`'s rdata as a JSON
        blob
        """
        guts = super(TXTRecord, self).rdata()
        shell = {'txt_rdata': guts}
        return shell

    @property
    def txtdata(self):
        """Free form text"""
        return self._txtdata

    @txtdata.setter
    def txtdata(self, value):
        self._txtdata = value
        self.api_args['rdata']['txtdata'] = self._txtdata
        self._update_record(self.api_args)
