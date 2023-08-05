# -*- coding: utf-8 -*-

from .fields import MsgFields as F

# jsonschema v4 doesn't support formats on object keys, so we're stuck with
# regexes to validate. When jsonschema v5 comes out, can look at that.
# This regex as per:
# https://stackoverflow.com/questions/53497/regular-expression-that-matches-va
# lid-ipv6-addresses
ipv4re = "^(\d{1,3}\.){1,3}(\d{1,3})$"
ipv6re = ("^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:)"
          "{1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}"
          ":){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA"
          "-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0"
          "-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:"
          "[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a"
          "-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25"
          "[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}(25[0-5]|(2[0-4]|1{0,1}"
          "[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}"
          "[0-9]){0,1}[0-9]).){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$")
ipv4v6re = "{0}|{1}".format(ipv4re, ipv6re)


def build_schema(schema, add_meta=True, type_="object",
                 additionalProperties=False):
    """
    Adds a few necessary embelishments to any schema
    """

    schema["$schema"] = "http://json-schema.org/draft-04/schema#"
    schema["type"] = type_
    schema["additionalProperties"] = additionalProperties
    if add_meta:
        schema["properties"][F.META] = _MetaSchema
    return schema

_MetaSchema = build_schema({
    "properties": {
        F.META_START_TIME: {"type": "string"},
        F.META_END_TIME: {"type": "string"},
        F.META_AGENT_NAME: {"type": ["string", "null"]},
        F.META_TASK_NAME: {"type": "string"},
        F.META_TASK_VERSION: {"type": "string"},
        F.META_ERR: {"type": ["string", "null"]},
        F.META_MSG: {"type": ["string", "null"]},
    }
}, add_meta=False)

# TaskResultSet schema, currently not checked, but defined for completeness
TrsSchema = build_schema({
    "properties": {
        F.TRS_META_JOB_ID: {"type": "number"},
        F.TRS_META_TARGET_ID: {"type": "number"},
    }
}, add_meta=False)

TestSchema = build_schema({
    "properties": {
        "a": {"type": "string"},
        "b": {"type": ["string", "null"]},
        u"レスト": {"type": ["string", "null"]},
    },
    "required": ["a"]
})

# ############ Add schemas from here ################

ArtifactSchema = build_schema({
    "properties": {
        F.PATH: {"type": "string"},
    }
})

AsnipSchema = build_schema({
    "properties": {
        F.ASNIP: {
            "type": "object",
            "patternProperties": {
                ipv4v6re: {
                    "type": "object",
                    "properties": {
                        F.ABUSE_EMAIL: {"type": ["string", "null"]},
                        F.ASN: {"type": ["number", "null"]},
                        F.AS_CC: {"type": ["string", "null"]},
                        F.AS_CIDR: {"type": ["string", "null"]},
                        F.AS_NAME: {"type": ["string", "null"]},
                        F.AS_UPDATE_DATE: {"type": ["string", "null"]},
                        F.NET_CC: {"type": ["string", "null"]},
                        F.NET_CIDR: {"type": ["string", "null"]},
                        F.NET_DESC: {"type": ["string", "null"]},
                        F.NET_NAME: {"type": ["string", "null"]},
                        F.NET_UPDATE_DATE: {"type": ["string", "null"]},
                        F.PHYSICAL_ADDRESS: {"type": ["string", "null"]},
                    },
                }
            },
            "additionalProperties": False,
        },
    }
})

DomainSchema = build_schema({
    "properties": {
        F.DOMAIN: {"type": "string"},
    }
})

# Special schema:
# a bucket for any kinds of misc settings a Job might need: user-agent strings,
# previous file hashes, previous IP addresses
JobsettingsSchema = build_schema({
    "properties": {
    },
}, add_meta=False, additionalProperties=True)

GeoipSchema = build_schema({
    "properties": {
        F.GEOIP: {
            "type": "object",
            "patternProperties": {
                ipv4v6re: {
                    "type": "object",
                    "properties": {
                        F.COUNTRY_CODE: {"type": ["string", "null"]},
                        F.LAT: {"type": ["number", "null"]},
                        F.LONG: {"type": ["number", "null"]},
                    }
                }
            },
            "additionalProperties": False,
        },
    }
})

HostnameSchema = build_schema({
    "properties": {
        F.HOSTNAME: {"type": "string"},
    }
})

HttpstatusSchema = build_schema({
    "properties": {
        F.HTTP_STATUS: {"type": ["number", "null"]},
        F.HTTP_REDIR: {"type": ["string", "null"]},
        F.HTTP_HEADERS: {"type": ["object", "null"]},
        F.IP: {"type": ["string", "null"]},
    }
})

UrlcontentSchema = build_schema({
    "properties": {
        F.HTTP_STATUS: {"type": ["number", "null"]},
        F.FILE_PACK: {"type": ["string", "null"]},
        F.IP: {"type": ["string", "null"]},
    }
})

UrlspidercontentSchema = build_schema({
    "properties": {
        F.HTTP_STATUS: {"type": ["number", "null"]},
        F.FILE_PACK: {"type": ["string", "null"]},
        F.SPIDER_TIMEOUT: {"type": "boolean"},
        F.EXTERNAL_URL_SET: {
            "type": "array",
            "items": {
                "type": ["string", "null"],
            }
        },
        # F.IP: {"type": ["string", "null"]},
    }
})

UrlscreenshotSchema = build_schema({
    "properties": {
        F.FILE_PACK: {"type": ["string", "null"]},
    }
})

IpSingleSchema = build_schema({
    "properties": {
        F.IP: {
            "type": ["string", "null"],
        }
    }
}, add_meta=False)

IpsetSchema = build_schema({
    "properties": {
        F.IPSET: {
            "type": "array",
            "items": {
                "type": ["string", "null"],
                "format": "ipv4",
            }
        }
    }
})

OsfingerprintsSchema = build_schema({
    "properties": {
        F.OS_FINGERPRINTS: {
            "type": "object",
            "patternProperties": {
                ipv4v6re: {
                    "type": ["object", "null"],
                    "properties": {
                        F.PORTS: {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    F.PORT_NUM: {"type": ["number"]},
                                    F.PORT_PROTO: {"type": ["string"]},
                                    F.PORT_STATUS: {"type": ["string"]},
                                },
                            },
                        },
                        F.OS_GUESS: {
                            "type": "object",
                            "properties": {
                                F.OS_NAME: {"type": ["string"]},
                                F.OS_GUESS_ACCURACY: {"type": ["number"]},
                                F.OS_FAMILY: {"type": ["string"]},
                                F.OS_GEN: {"type": ["string"]},
                            },
                        },
                        F.STATUS: {
                            "type": "string",
                        },
                    },
                },
            },
            "additionalProperties": False,
        },
    }
})

UrlSchema = build_schema({
    "properties": {
        F.URL: {"type": "string"},
    }
})

VirustotalSchema = build_schema({
    "properties": {
        F.VIRUSTOTAL_RESULT: {"type": ["object", "null"]},
        F.HTTP_STATUS: {"type": ["number", "null"]},
    }
})

WebfingerprintsSchema = build_schema({
    "properties": {
        F.WEB_FINGERPRINTS: {
            "type": ["object", "null"],
            "patternProperties": {
                "[0-9 -_a-zA-Z\:]+": {
                    "properties": {
                        F.CATEGORIES: {
                            "type": ["array"],
                            "items": {
                                "type": ["string", "null"],
                            }
                        }
                    }
                }
            }
        },
        F.IP: {
            "type": ["string", "null"],
        }
    }
})

WepawetSchema = build_schema({
    "properties": {
        F.WEPAWET_REPORT_URL: {"type": ["string", "null"]},
        F.WEPAWET_JUDGEMENT: {"type": ["number", "null"]},
        F.WEPAWET_TASK_ID: {"type": ["string", "null"]}
    }
})

WhoisSchema = build_schema({
    "properties": {
        F.WHOIS_RAW: {"type": ["string", "null"]},
    }
})
