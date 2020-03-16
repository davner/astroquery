# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
MAST Utils
==========

Miscellaneous functions used throughout the MAST module.
"""

import numpy as np

import requests
import json
from urllib import parse 
import astropy.coordinates as coord

from ..version import version
from ..exceptions import ResolverError

from . import conf


def _parse_type(dbtype):
    """
    Takes a data type as returned by a database call and regularizes it into a
    triplet of the form (human readable datatype, python datatype, default value).

    Parameters
    ----------
    dbtype : str
        A data type, as returned by a database call (ex. 'char').

    Returns
    -------
    response : tuple
        Regularized type tuple of the form (human readable datatype, python datatype, default value).

    For example:

    _parse_type("short")
    ('integer', np.int64, -999)
    """

    dbtype = dbtype.lower()

    return {
        'char': ('string', str, ""),
        'string': ('string', str, ""),
        'datetime': ('string', str, ""),  # TODO: handle datetimes correctly
        'date': ('string', str, ""),  # TODO: handle datetimes correctly

        'double': ('float', np.float64, np.nan),
        'float': ('float', np.float64, np.nan),
        'decimal': ('float', np.float64, np.nan),

        'int': ('integer', np.int64, -999),
        'short': ('integer', np.int64, -999),
        'long': ('integer', np.int64, -999),
        'number': ('integer', np.int64, -999),

        'boolean': ('boolean', bool, None),
        'binary': ('boolean', bool, None),

        'unsignedbyte': ('byte', np.ubyte, -999)
    }.get(dbtype, (dbtype, dbtype, dbtype))


def _simple_request(url, params):
    """
    Light wrapper on requests.session().get basically to make monkey patched testing easier/more effective.
    """

    session = requests.session()
    headers = {"User-Agent": "astroquery/{} {}".format(version, session.headers['User-Agent']),
               "Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    return response


def resolve_object(objectname):
    """
    Resolves an object name to a position on the sky.

    Parameters
    ----------
    objectname : str
        Name of astronomical object to resolve.

    Returns
    -------
    response : `~astropy.coordinates.SkyCoord`
        The sky position of the given object.
    """

    request_args = {"service": "Mast.Name.Lookup",
                    "params": {'input': objectname, 'format': 'json'}}
    request_string =  'request={}'.format(parse.urlencode(json.dumps(request_args)))

    response = _simple_request("{}/api/v0/invoke".format(conf.server), request_string)
    result = response.json()

    if len(result['resolvedCoordinate']) == 0:
        raise ResolverError("Could not resolve {} to a sky position.".format(objectname))

    ra = result['resolvedCoordinate'][0]['ra']
    dec = result['resolvedCoordinate'][0]['decl']
    coordinates = coord.SkyCoord(ra, dec, unit="deg")

    return coordinates
