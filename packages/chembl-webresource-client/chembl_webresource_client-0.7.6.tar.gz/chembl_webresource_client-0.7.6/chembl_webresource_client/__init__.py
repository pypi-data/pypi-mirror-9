__author__ = 'mnowotka'

try:
    __version__ = __import__('pkg_resources').get_distribution('chembl_webresource_client').version
except Exception as e:
    __version__ = 'development'

import gevent

def _greenlet_report_error(self, exc_info):
    pass

gevent.greenlet.Greenlet._report_error = _greenlet_report_error

import requests
import grequests

from chembl_webresource_client.assay_resource import AssayResource
from chembl_webresource_client.target_resource import TargetResource
from chembl_webresource_client.compound_resource import CompoundResource

__all__ = [
    "AssayResource",
    "TargetResource",
    "CompoundResource",
]
