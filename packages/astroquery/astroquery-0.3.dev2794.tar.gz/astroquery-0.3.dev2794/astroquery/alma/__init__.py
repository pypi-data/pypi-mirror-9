# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
ALMA Archive service.
"""
from astropy import config as _config


class Conf(_config.ConfigNamespace):
    """
    Configuration parameters for `astroquery.alma`.
    """

    timeout = _config.ConfigItem(60, "Timeout in seconds")

    archive_url = _config.ConfigItem(['http://almascience.org',
                                      'http://almascience.eso.org',
                                      'http://almascience.nrao.edu',
                                      'http://almascience.nao.ac.jp',
                                      'http://beta.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/aq', # the beta server (for testing)
                                     ],
                                     'The ALMA Archive mirror to use')

conf = Conf()

from .core import Alma, AlmaClass

__all__ = ['Alma', 'AlmaClass',
           'Conf', 'conf',
           ]


