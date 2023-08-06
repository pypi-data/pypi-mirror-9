# Licensed under a 3-clause BSD style license - see LICENSE.rst
from ... import splatalogue
from ...utils.testing_tools import MockResponse
from astropy import units as u
from astropy.tests.helper import pytest
import requests
import os

SPLAT_DATA = 'CO_colons.csv'


def data_path(filename):
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    return os.path.join(data_dir, filename)


@pytest.fixture
def patch_post(request):
    mp = request.getfuncargvalue("monkeypatch")
    mp.setattr(requests, 'post', post_mockreturn)
    return mp


def post_mockreturn(url, data=None, timeout=10, **kwargs):
    filename = data_path(SPLAT_DATA)
    content = open(filename, "rb").read()
    return MockResponse(content, **kwargs)


def test_simple(patch_post):
    x = splatalogue.Splatalogue.query_lines(114 * u.GHz, 116 * u.GHz, chemical_name=' CO ')


def test_init(patch_post):
    x = splatalogue.Splatalogue.query_lines(114 * u.GHz, 116 * u.GHz, chemical_name=' CO ')
    S = splatalogue.Splatalogue(chemical_name=' CO ')
    y = S.query_lines(114 * u.GHz, 116 * u.GHz)
    # it is not currently possible to test equality between tables:
    # masked arrays fail
    # assert y == x
    assert len(x) == len(y)
    assert all(y['Species'] == x['Species'])
    assert all(x['Chemical Name'] == y['Chemical Name'])


def test_load_species_table():
    tbl = splatalogue.load_species_table.species_lookuptable()
    CO = tbl.find(' CO ')
    assert len(CO) == 4


# regression test: ConfigItems were in wrong order at one point
def test_url():
    assert 'http://' in splatalogue.core.Splatalogue.QUERY_URL
    assert 'cv.nrao.edu' in splatalogue.core.Splatalogue.QUERY_URL


# regression test: get_query_payload should work (#308)
def test_get_payload():
    q = splatalogue.core.Splatalogue.query_lines_async(1 * u.GHz, 10 * u.GHz,
                                                       get_query_payload=True)
    assert '__utma' in q

# regression test: line lists should ask for only one line list, not all
def test_line_lists():
    q = splatalogue.core.Splatalogue.query_lines_async(1 * u.GHz, 10 * u.GHz,
                                                       line_lists=['JPL'],
                                                       get_query_payload=True)
    assert q['displayJPL'] == 'displayJPL'
    assert q['displaySLAIM'] == ''


# regression test: raise an exception if a string is passed to line_lists
# uses get_query_payload to avoid having to monkeypatch
def test_linelist_type():
    with pytest.raises(TypeError) as exc:
        splatalogue.core.Splatalogue.query_lines_async(1 * u.GHz, 10 * u.GHz,
                                                       line_lists='JPL',
                                                       get_query_payload=True)
    assert exc.value.args[0] == "Line lists should be a list of linelist names.  See Splatalogue.ALL_LINE_LISTS"


def test_top20_crashorno():
    splatalogue.core.Splatalogue.query_lines_async(114 * u.GHz, 116 * u.GHz, top20='top20',
                                                   get_query_payload=True)
    with pytest.raises(ValueError) as exc:
        splatalogue.core.Splatalogue.query_lines_async(114 * u.GHz, 116 * u.GHz,
                                                       top20='invalid',
                                                       get_query_payload=True)
    assert exc.value.args[0] == "Top20 is not one of the allowed values"


def test_band_crashorno():
    splatalogue.core.Splatalogue.query_lines_async(band='alma3',
                                                   get_query_payload=True)
    with pytest.raises(ValueError) as exc:
        splatalogue.core.Splatalogue.query_lines_async(band='invalid',
                                                       get_query_payload=True)
    assert exc.value.args[0] == "Invalid frequency band."
