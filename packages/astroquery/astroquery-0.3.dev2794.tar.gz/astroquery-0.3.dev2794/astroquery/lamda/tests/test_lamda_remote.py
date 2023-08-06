# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.tests.helper import remote_data
from ... import lamda
import requests
import imp
imp.reload(requests)


@remote_data
def test_query():
    result = lamda.query(mol='co', query_type='erg_levels')
    assert [len(r) for r in result] == [2, 40, 41]
    collider_dict = result[0]
    assert collider_dict.keys() == ['PH2', 'OH2']
    assert [len(collider_dict[r]) for r in collider_dict] == [820,820]
