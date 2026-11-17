from playwright.sync_api import expect


def test_auth(page):
    page.goto("https://www.saucedemo.com/")  # открываем нужную страницу

    page.get_by_placeholder("Username").fill("standard_user")  # заполняем валидный логин
    page.get_by_placeholder("Password").fill("secret_sauce")  # заполняем валидный пароль

    page.locator("#login-button").click()  # кликаем по кнопке входа "Login"

    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")  # проверяем редирект на нужный URL


def test_login_locked_out_user(page):
    page.goto("https://www.saucedemo.com/")  # открываем страницу логина

    # Вводим логин и пароль заблокированного пользователя
    page.get_by_placeholder("Username").fill("locked_out_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.locator("#login-button").click()

    # Проверяем, что URL не изменился
    expect(page).to_have_url("https://www.saucedemo.com/")

    # Проверяем появление ошибки
    error = page.locator("h3[data-test='error']")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Epic sadface: Sorry, this user has been locked out.")


def test_logout(auth_page):
    # --- Логаут ---
    auth_page.locator("#react-burger-menu-btn").click()  # открываем боковое меню
    auth_page.locator("#logout_sidebar_link").click()  # кликаем на logout

    # Проверяем возвращение на страницу логина
    expect(auth_page).to_have_url("https://www.saucedemo.com/")
    expect(auth_page.locator("#login-button")).to_be_visible()


def test_logout_visual_user(page):
    page.goto("https://www.saucedemo.com/")

    # Логинимся
    page.get_by_placeholder("Username").fill("visual_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.locator("#login-button").click()

    # Проверяем, что мы на странице каталога
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")

    # Выходим
    page.locator("#react-burger-menu-btn").click()
    page.locator("#logout_sidebar_link").click()

    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(page.locator("#login-button")).to_be_visible()