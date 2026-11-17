from playwright.sync_api import expect
from steps.catalog_steps import CatalogSteps
from steps.login_steps import LoginSteps


def test_auth(page):
    steps = LoginSteps(page)
    steps.open_login_page().login("standard_user", "secret_sauce")
    assert page.url == "https://www.saucedemo.com/inventory.html"


def test_login_locked_out_user(page):
    steps = LoginSteps(page)
    steps.open_login_page().login("locked_out_user", "secret_sauce")
    assert page.url == "https://www.saucedemo.com/"
    error_text = steps.get_error_text()
    assert "locked out" in error_text


def test_logout(page):
    login = LoginSteps(page)
    catalog = CatalogSteps(page)

    login.open_login_page().login("standard_user", "secret_sauce")
    expect(catalog.catalog.product_cards, "Ожидаем, что в каталоге есть товары",).not_to_have_count(0)

    catalog.logout()
    assert page.url == "https://www.saucedemo.com/", "Ожидаем возврат на страницу логина"


def test_logout_visual_user(page):
    login = LoginSteps(page)
    catalog = CatalogSteps(page)

    login.open_login_page().login("visual_user", "secret_sauce")
    expect(catalog.catalog.product_cards, "Ожидаем, что в каталоге есть товары",).not_to_have_count(0)

    catalog.logout()
    assert page.url == login.LOGIN_URL, "Ожидаем возврат на страницу логина"