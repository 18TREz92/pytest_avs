from playwright.sync_api import expect


def test_count_catalog(auth_page):
    # Проверяем количество товаров
    products = auth_page.locator(
        ".inventory_item")  # используем класс, так как каждая карточка имеет класс, а не id (важный момент)
    assert products.count() == 6


def test_sorted_by_name(auth_page):
    # Ждём видимости селектора
    sort_select = auth_page.locator(".product_sort_container")
    expect(sort_select).to_be_visible(timeout=5000)

    # Сортируем от A до Z
    sort_select.select_option("az")

    # Получаем список названий товаров
    names = auth_page.locator(".inventory_item_name").all_text_contents()

    # Проверяем, что список отсортирован по имени
    assert names == sorted(names), "Товары не отсортированы по имени A-Z"


def test_sorted_by_name_reversed(auth_page):
    # Ждём видимости селектора
    sort_select = auth_page.locator(".product_sort_container")
    expect(sort_select).to_be_visible(timeout=5000)

    # Сортируем от Z до A
    sort_select.select_option("za")

    # Получаем список названий товаров
    names = auth_page.locator(".inventory_item_name").all_text_contents()

    # Проверяем, что список отсортирован по имени
    assert names == sorted(names, reverse=True), "Товары не отсортированы по имени Z-A"


def test_sort_by_price(auth_page):
    # Локатор селекта сортировки
    sort_select = auth_page.locator(".product_sort_container")
    expect(sort_select).to_be_visible(timeout=5000)

    # Сортировка по цене от low to high
    sort_select.select_option("lohi")  # low → high

    # Получаем список цен
    prices_text = auth_page.locator(".inventory_item_price").all_text_contents()

    # Преобразуем в числа (удаляем $)
    prices = [float(p.replace("$", "")) for p in prices_text]

    # Проверяем сортировку по возрастанию
    assert prices == sorted(prices), "Товары не отсортированы по цене low → high"

    # Сортировка по цене от high to low
    sort_select.select_option("hilo")  # high → low

    # Получаем список цен снова
    prices_text = auth_page.locator(".inventory_item_price").all_text_contents()
    prices = [float(p.replace("$", "")) for p in prices_text]

    # Проверяем сортировку по убыванию
    assert prices == sorted(prices, reverse=True), "Товары не отсортированы по цене high → low"


def test_add_bike_light_to_cart(auth_page):
    # Добавляем товар в корзину
    product_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Bike Light")
    add_button = product_card.locator("button")  # кнопка Add to cart внутри карточки

    # Кликаем
    add_button.click()

    # Проверяем, что кнопка изменилась на Remove
    expect(add_button).to_have_text("Remove")

    # Проверяем счётчик корзины
    expect(auth_page.locator(".shopping_cart_badge")).to_have_text("1")


def test_add_onesie_to_cart(auth_page):
    # Добавляем товар в корзину
    product_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Onesie")
    button = product_card.locator("button")  # кнопка Add to cart внутри карточки

    # Кликаем
    button.click()

    # Проверяем, что кнопка изменилась на Remove
    expect(button).to_have_text("Remove")

    # Проверяем счётчик корзины
    expect(auth_page.locator(".shopping_cart_badge")).to_have_text("1")

    # Кликаем для удаления по той же кнопке
    button.click()

    # Проверяем, что кнопка изменилась на Add to cart
    expect(button).to_have_text("Add to cart")

    # Проверяем счётчик корзины
    expect(auth_page.locator(".shopping_cart_badge")).not_to_be_visible()


def test_product_details_onesie(auth_page):
    # Находим карточку товара
    product_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Onesie")

    # Сохраняем название и цену с карточки
    product_name = product_card.locator('[data-test="inventory-item-name"]').inner_text()
    product_price = product_card.locator('[data-test="inventory-item-price"]').inner_text()

    # Переходим на страницу товара
    product_card.locator('[data-test="inventory-item-name"]').click()

    # Проверяем название и цену на странице деталей
    detail_name = auth_page.locator('[data-test="inventory-item-name"]').inner_text()
    detail_price = auth_page.locator('[data-test="inventory-item-price"]').inner_text()

    assert detail_name == product_name, "Название товара не совпадает"
    assert detail_price == product_price, "Цена товара не совпадает"


def test_product_details_jacket(auth_page):
    # Находим карточку товара
    product_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Fleece Jacket")

    # Сохраняем название и цену с карточки
    product_name = product_card.locator('[data-test="inventory-item-name"]').inner_text()
    product_price = product_card.locator('[data-test="inventory-item-price"]').inner_text()

    # Переходим на страницу товара
    product_card.locator('[data-test="inventory-item-name"]').click()

    # Проверяем название и цену на странице деталей
    detail_name = auth_page.locator('[data-test="inventory-item-name"]').inner_text()
    detail_price = auth_page.locator('[data-test="inventory-item-price"]').inner_text()

    assert detail_name == product_name, "Название товара не совпадает"
    assert detail_price == product_price, "Цена товара не совпадает"


def test_remove_item_from_catalog(auth_page):
    # Кликаем по кнопке Add to cart
    product_card = auth_page.locator(".inventory_item", has_text="Test.allTheThings() T-Shirt (Red)")
    product_button = product_card.locator('[data-test="add-to-cart-test.allthethings()-t-shirt-(red)"]')
    product_button.click()

    # Проверяем, что кнопка Remove появилась
    remove_button = product_card.locator('[data-test="remove-test.allthethings()-t-shirt-(red)"]')
    assert remove_button.is_visible(), "Кнопка Remove не появилась"

    # Удаляем из корзины
    remove_button.click()

    # Проверяем, что кнопка Add to cart вернулась после удаления
    add_button = product_card.locator('[data-test="add-to-cart-test.allthethings()-t-shirt-(red)"]')
    assert add_button.is_visible(), "Кнопка Add to cart не вернулась после удаления"


def test_remove_onesie_from_catalog(auth_page):
    # Кликаем по кнопке Add to cart
    product_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Onesie")
    product_button = product_card.locator('[data-test="add-to-cart-sauce-labs-onesie"]')
    product_button.click()

    # Проверяем, что кнопка Remove появилась
    remove_button = product_card.locator('[data-test="remove-sauce-labs-onesie"]')
    assert remove_button.is_visible(), "Кнопка Remove не появилась"

    # Удаляем из корзины
    remove_button.click()

    # Проверяем, что кнопка Add to cart вернулась после удаления
    add_button = product_card.locator('[data-test="add-to-cart-sauce-labs-onesie"]')
    assert add_button.is_visible(), "Кнопка Add to cart не вернулась после удаления"