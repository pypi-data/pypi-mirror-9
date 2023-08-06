from __future__ import absolute_import
import django  # noqa
from django.contrib.auth.models import User
from .base import *  # noqa
from selenium.webdriver.support.select import Select

pytestmark = pytest.mark.selenium


@pytest.mark.skipif('django.VERSION[:2]==(1,8)')
def test_mass_update_1(admin_site):
    """
    Check Boolean Field.
    Common values are not filled in boolean fields ( there is no reason to do that ).
    """
    assert User.objects.filter(is_active=True).count() > 1  # sanity check

    browser, administrator = admin_site
    browser.find_element_by_link_text("Users").click()
    browser.find_element_by_id("action-toggle").click()
    browser.find_element_by_xpath("//input[@name='_selected_action' and @value='1']").click()  # unselect sax

    Select(browser.find_element_by_name("action")).select_by_visible_text("Mass update")
    browser.find_element_by_name("index").click()  # execute

    assert "Mass update users" in browser.title
    browser.find_element_by_name("chk_id_is_active").click()
    browser.find_element_by_id("id_is_active").click()
    browser.find_element_by_name("apply").click()
    assert "Select user to change" in browser.title
    assert User.objects.filter(is_active=True).count() == 1

