from django.contrib.auth.models import User
from django_dynamic_fixture import G
import django_webtest
import pytest


def pytest_configure(config):
    try:
        from django.apps import AppConfig  # noqa
        import django

        django.setup()
    except ImportError:
        pass


@pytest.fixture(scope='function')
def app(request):
    wtm = django_webtest.WebTestMixin()
    wtm.csrf_checks = False
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return django_webtest.DjangoTestApp()



@pytest.fixture(scope='function')
def users():
    return G(User, n=2, is_staff=False, is_active=False)


