# Licensed under a 3-clause BSD style license - see LICENSE.rst

import os
from contextlib import contextmanager
import requests
from astropy.tests.helper import pytest
from astropy.io.ascii.tests.common import assert_equal
from astropy.extern.six import string_types
from ... import besancon
from ...utils import commons
from ...utils.testing_tools import MockResponse

# SKIP - don't run tests because Besancon folks don't want them (based on the fact that your@email.net is now rejected)
# def test_besancon_reader():
# assert os.path.exists('besancon_test.txt')
#     B = asciitable.read('t/besancon_test.txt',Reader=besancon.BesanconFixed,guess=False)
#     assert_equal(len(B),12)
#
# def test_basic():
#     besancon_model = besancon.request_besancon('astropy.astroquery@gmail.com',10.5,0.0,soli=0.0001)
#     B = asciitable.read(besancon_model,Reader=besancon.BesanconFixed,guess=False)
#     B.pprint()

# to prevent test hanging
besancon.Besancon.TIMEOUT = 1
besancon.Besancon.ping_delay = 1

DATA_FILES = ('besancon_test.txt', 'besancon_test2.txt')


def data_path(filename):
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    return os.path.join(data_dir, filename)


@pytest.mark.parametrize(('filename', 'length', 'ncols', 'd1', 'mv1'), zip(DATA_FILES, (13, 6), (18, 24), (0.091, 0.111), (10.20, 9.70)))
def test_reader(filename, length, ncols, d1, mv1):
    besancon_model = data_path(filename)
    with open(besancon_model, 'r') as f:
        data = f.read()
    B = besancon.core.parse_besancon_model_string(data)
    B.pprint()
    assert_equal(len(B), length)
    assert_equal(len(B.columns), ncols)
    assert B['Dist'][0] == d1
    assert B['Mv'][0] == mv1


@pytest.fixture
def patch_post(request):
    mp = request.getfuncargvalue("monkeypatch")
    mp.setattr(requests, 'post', post_mockreturn)
    return mp

@pytest.fixture
def patch_get_readable_fileobj(request):
    @contextmanager
    def get_readable_fileobj_mockreturn(filename, **kwargs):
        # file_obj = StringIO.StringIO(filename)
        if isinstance(filename, string_types):
            is_binary = kwargs.get('encoding',None) == 'binary'
            file_obj = open(data_path(filename), "r"+('b' if is_binary else ''))
        else:
            file_obj = filename
        # file_obj = data_path(filename)
        yield file_obj
    mp = request.getfuncargvalue("monkeypatch")
    mp.setattr(commons, 'get_readable_fileobj', get_readable_fileobj_mockreturn)
    return mp


def post_mockreturn(url, data, timeout=10, stream=True, params=None, **kwargs):
    # filename = data_path('1376235131.430670.resu')
    filename = data_path('query_return.iframe.html')
    content = open(filename, 'rb').read()
    return MockResponseBesancon(content, filename, **kwargs)


def test_query(patch_post, patch_get_readable_fileobj):
    B = besancon.Besancon()
    B.url_download = ''
    result = B.query(0, 0, 'adam.g.ginsburg@gmail.com')
    assert result is not None

def test_default_params():
    """ Ensure that the default parameters of the query match the default
    parameters on the web form (excepting coordinates and e-mail address) """
    data = besancon.Besancon.query_async(0,0,'a@b.com',get_query_payload=True)

    with open(data_path('default_params.txt')) as f:
        dp = eval(f.read())

    for k in dp:
        assert dp[k] == data[k]
        # DEBUG print "\t".join((str(x) for x in (k, dp[k] == data[k], dp[k], data[k])))

class MockResponseBesancon(MockResponse):

    def __init__(self, content=None, url=None, headers={}, **kwargs):
        super(MockResponseBesancon, self).__init__(content)
        self.raw = url  # StringIO.StringIO(url)
        self.headers = headers
