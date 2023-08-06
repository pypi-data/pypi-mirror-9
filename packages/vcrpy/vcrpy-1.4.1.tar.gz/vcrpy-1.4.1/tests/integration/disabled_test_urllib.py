'''Integration tests with urllib2'''
# coding=utf-8

import pytest
urllib = pytest.importorskip("urllib")

import vcr
from assertions import assert_cassette_empty, assert_cassette_has_one_response


@pytest.fixture(params=["https", "http"])
def scheme(request):
    """
    Fixture that returns both http and https
    """
    return request.param


def test_response_code(scheme, tmpdir):
    '''Ensure we can read a response code from a fetch'''
    url = scheme + '://httpbin.org/'
    with vcr.use_cassette(str(tmpdir.join('atts.yaml'))) as cass:
        code = urllib.urlopen(url).getcode()

    with vcr.use_cassette(str(tmpdir.join('atts.yaml'))) as cass:
        assert code == urlopen(url).getcode()


