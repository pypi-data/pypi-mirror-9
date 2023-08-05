# -*- coding: utf-8 -*-

import colander
from .fields import MsgFields as F


class _MetaSchema(colander.Schema):
    start_time = colander.SchemaNode(colander.String(), name=F.META_START_TIME)
    end_time = colander.SchemaNode(colander.String(), name=F.META_END_TIME)
    err = colander.SchemaNode(colander.String(), name=F.META_ERR, missing=None)
    msg = colander.SchemaNode(colander.String(), name=F.META_MSG, missing=None)


class BaseTaskSchema(colander.Schema):
    meta = _MetaSchema(name=F.META)


class TestSchema(BaseTaskSchema):
    # A stable schema for testing purposes.
    a = colander.SchemaNode(colander.String(), name="a")
    b = colander.SchemaNode(colander.String(), name="b", missing=None)
    uni = colander.SchemaNode(colander.String(), name="テスト", missing=None)


# ###### Actual Task schema definitions ########

class DomainSchema(BaseTaskSchema):
    domain = colander.SchemaNode(colander.String(), name=F.DOMAIN)


class UrlSchema(BaseTaskSchema):
    url = colander.SchemaNode(colander.String(), name=F.URL)


class HostnameSchema(BaseTaskSchema):
    hostname = colander.SchemaNode(colander.String(), name=F.HOSTNAME)


class WhoisSchema(BaseTaskSchema):
    whois_raw = colander.SchemaNode(colander.String(),
                                    name=F.WHOIS_RAW,
                                    missing=None)


class HttpstatusSchema(BaseTaskSchema):
    http_status = colander.SchemaNode(colander.Integer(),
                                      name=F.HTTP_STATUS,
                                      missing=None)


class IpSchema(BaseTaskSchema):
    ip = colander.SchemaNode(colander.String(), name=F.IP)


class IpSetSchema(colander.Mapping):
    # we allow arbitrary keys here
    pass


class GeoipSchema(BaseTaskSchema):
    cc = colander.SchemaNode(colander.String(),
                             name=F.COUNTRY_CODE,
                             missing=None)
    lat = colander.SchemaNode(colander.Float(),
                              name=F.LAT,
                              missing=None)
    long = colander.SchemaNode(colander.Float(),
                               name=F.LONG,
                               missing=None)
