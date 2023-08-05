# -*- coding: utf-8 -*-

# ConstantDict as detailed at
# http://loose-bits.com/2011/06/constantdict-yet-another-python.html


class ConstantDict(object):
    """An enumeration class."""
    _dict = None

    @classmethod
    def dict(cls):
        """Dictionary of all upper-case constants."""
        if cls._dict is None:
            val = lambda x: getattr(cls, x)
            cls._dict = dict(((c, val(c)) for c in dir(cls)
                             if c == c.upper()))
        return cls._dict

    def __contains__(self, value):
        return value in self.dict().values()

    def __iter__(self):
        for value in self.dict().values():
            yield value

    def __getattr__(self, name):
        if name in self.dict():
            return self._dict[name]
        else:
            return object.__getattribute__(self, name)


class MsgFields(ConstantDict):
    """
    Names of fields embedded in a DSMS message
    """
    ABUSE_EMAIL = "abuseemail"
    ARTIFACT = "artifact"
    ASN = "asn"
    ASNIP = "asnip"
    AS_CC = "asncc"
    AS_CIDR = "ascidr"
    AS_NAME = "asname"
    AS_UPDATE_DATE = "asupdatedate"
    CATEGORIES = "categories"
    CIDR = "cidr"
    COUNTRY_CODE = "cc"
    DOMAIN = "domain"
    EXTERNAL_URL_SET = "exturlset"
    FILE_PACK = "filepack"
    GEOIP = "geoip"
    HOSTNAME = "hostname"
    HTTP_CONTENTS = "httpcontents"
    HTTP_STATUS = "httpstatus"
    HTTP_REDIR = "httpredir"
    HTTP_HEADERS = "httpheaders"
    HTTP_USERAGENT = "httpuseragent"
    IP = "ip"
    IPSET = "ipset"
    JOB_SETTINGS = "jobsettings"
    LAT = "lat"
    LONG = "long"
    NET_CC = "netcc"
    NET_CIDR = "netcidr"
    NET_DESC = "netdesc"
    NET_NAME = "netname"
    NET_UPDATE_DATE = "netupdatedate"
    OS_GUESS_ACCURACY = "osaccuracy"
    OS_FAMILY = "osfamily"
    OS_FINGERPRINTS = "osfingerprints"
    OS_GEN = "osgen"
    OS_GUESS = "osguess"
    OS_NAME = "osname"
    OS_TYPE = "ostype"
    PATH = "path"
    PORTS = "ports"
    PORT_STATUS = "portstatus"
    PORT_PROTO = "portproto"
    PORT_NUM = "portnum"
    PHYSICAL_ADDRESS = "phyaddr"
    SPIDER = "spider"
    SPIDER_TIMEOUT = "spidertimeout"
    STATUS = "status"
    URL = "url"
    URL_CONTENT = "urlcontent"
    URL_SCREENSHOT = "urlscreenshot"
    URL_SPIDER_CONTENT = "urlspidercontent"
    VIRUSTOTAL_RESULT = "virustotal"
    VIRUSTOTAL_PREV_HASH = "virustotalprevhash"
    WEB_FINGERPRINTS = "webfingerprints"
    WEPAWET_JUDGEMENT = "wepawetjudge"
    WEPAWET_RESULT = "wepawet"
    WEPAWET_REPORT_URL = "wepaweturl"
    WEPAWET_TASK_ID = "wepawettaskid"
    WEPAWET_PREV_TASK_ID = "wepawetprevtaskid"
    WHOIS = "whois"
    WHOIS_RAW = "raw"

    SEEDED_TASK = "seeded"

    TASKRESULTS = "tmoids"

    TRS_META = "_trs"
    TRS_META_JOB_ID = "jid"
    TRS_META_TARGET_ID = "tid"

    META = "_"
    META_AGENT_NAME = "agent"
    META_START_TIME = "stime"
    META_END_TIME = "etime"
    META_SUCCESS = "ok"
    META_RESULT = "r"
    META_TASK_NAME = "tname"
    META_TASK_VERSION = "v"
    META_ERR = "e"
    META_MSG = "m"

    TASKS_ASNIP = "asnip_task"
    TASKS_GEOIP = "geoip_task"
    TASKS_HTTP_GET = "http_get_task"
    TASKS_HTTP_SPIDER = "http_spider_task"
    TASKS_HTTP_STATUS = "http_status_task"
    TASKS_URL_SCREENSHOT = "url_screenshot_task"
    TASKS_RESOLVER = "resolver_task"
    TASKS_WEB_FINGERPRINT = "web_fingerprint_task"
    TASKS_OS_FINGERPRINT = "os_fingerprint_task"
    TASKS_WHOIS = "whois_task"
    TASKS_VIRUSTOTAL = "virustotal_task"
    TASKS_WEPAWET = "virustotal_task"


class MsgValues(ConstantDict):
    """
    Aliases for values in a particular message field
    """
    HTTP_STATUS_NONCONNECT = -1
    HTTP_CONTENT_FILE = "content"
    HTTP_HEADERS_FILE = "headers"
    HTTP_SPIDER_FILES = "spiderfiles"

    NMAP_STATUS_UP = "up"

    VIRUSTOTAL_HAS_FILE = 1
    VIRUSTOTAL_MISSING_FILE = 0
    VIRUSTOTAL_ERROR = -1
    VIRUSTOTAL_RATE_LIMIT_STATUS = 204

    WEPAWET_SUSPICIOUS_RESULT = 3
    WEPAWET_MALICIOUS_RESULT = 2
    WEPAWET_BENIGN_RESULT = 1
    WEPAWET_UNKNOWN_RESULT = -1

    URL_MANIFEST = "urlmani"
    URL_SCREENSHOT_FILE = "urlshot"


class MsgErrs(ConstantDict):
    """
    Used to generate error messages: <MsgErrs value>.format(reason)
    """
    DOCKER_ERROR = "DOCKER_ERROR::{0}"

    FILE_IO_ERROR = "FILE_IO_ERROR::{0}"

    FORMAT_ERROR = "FORMAT_ERROR::{0}"

    INPUT_INCORRECT_FORMAT = "INPUT_INCORRECT_FORMAT::{0}"
    INPUT_MISSING = "INPUT_MISSING::{0}"
    INPUT_WRONG_TYPE = "INPUT_WRONG_TYPE::{0}"

    HOSTNAME_UNRESOLVABLE = "HOSTNAME_UNRESOLVABLE::{0}"
    HOSTNAME_INVALID = "HOSTNAME_INVALID::{0}"

    LOOKUP_FAILED = "LOOKUP_FAILED::{0}"

    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED::{0}"
    REMOTE_API_ERROR = "REMOTE_API_ERROR::{0}"

    NMAP_EXEC_ERROR = "NMAP_EXEC_ERROR::{0}"
    NMAP_PARSE_ERROR = "NMAP_PARSE_ERROR::{0}"

    RESULT_FAIL = "TASK_RESULT_FAIL::{0}"
    RESULT_INVALID = "RESULT_INVALID::{0}"

    SETTINGS_ERROR = "SETTINGS_ERROR::{0}"

    FILE_SIZE_LIMIT_EXCEEDED = "FILE_SIZE_LIMIT_EXCEEDED::{0}"

    UNSPECIFIED_ERROR = "UNSPECIFIED_ERROR::{0}"

    URL_INVALID = "URL_INVALID::{0}"
    URL_TIMEOUT = "URL_TIMEOUT::{0}"
    URL_SCREENSHOT_CANCELLED = "URL_SCREENSHOT_CANCELLED::{0}"
    URL_SCREENSHOT_TIMEOUT = "URL_SCREENSHOT_TIMEOUT::{0}"
    URL_SCREENSHOT_UNAVAILABLE = "URL_SCREENSHOT_UNAVAILABLE::{0}"
    URL_SPIDER_TIMEOUT = "URL_SPIDER_TIMEOUT::{0}"
    URL_CONN_ERROR = "URL_CONN_ERROR::{0}"
