


# content of conftest.py
import pytest

class A(object):
    pass

@pytest.fixture
def base():
    print 'INST A'
    return A()

@pytest.fixture(params=["merlinux.eu", "mail.python.org"])
def smtp(request, base):
    print request.param
    return base

@pytest.fixture(params=['user', 'admin', None])
def auth_status(request, base):
    return base


def test_nyan(smtp, auth_status):
    assert smtp == auth_status
