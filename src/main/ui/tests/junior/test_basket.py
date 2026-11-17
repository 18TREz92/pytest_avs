from playwright.sync_api import expect


def test_add_item_and_check_in_cart(auth_page):
    # Добавляем Sauce Labs Backpack
    auth_page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()

    # Переходим в корзину
    auth_page.locator(".shopping_cart_link").click()

    # Проверяем, что товар есть
    item_name = auth_page.locator('[data-test="inventory-item-name"]')
    assert item_name.inner_text() == "Sauce Labs Backpack"


def test_add_two_items_and_check_in_cart(auth_page):
    # Добавляем Fleece Jacket
    auth_page.locator('[data-test="add-to-cart-sauce-labs-fleece-jacket"]').click()

    # Добавляем Bolt T-shirt
    auth_page.locator('[data-test="add-to-cart-sauce-labs-bolt-t-shirt"]').click()

    # Переходим в корзину
    auth_page.locator('[data-test="shopping-cart-link"]').click()
    name_jacket = auth_page.locator('.inventory_item_name', has_text='Sauce Labs Fleece Jacket')
    name_t_shirt = auth_page.locator('.inventory_item_name', has_text='Sauce Labs Bolt T-Shirt')

    assert name_jacket.inner_text() == "Sauce Labs Fleece Jacket"
    assert name_t_shirt.inner_text() == "Sauce Labs Bolt T-Shirt"


def test_remove_item_from_cart(auth_page):
    # Добавляем товар в корзину
    auth_page.locator('[data-test="add-to-cart-sauce-labs-fleece-jacket"]').click()

    # Переходим в корзину
    auth_page.locator('[data-test="shopping-cart-link"]').click()

    # Проверяем что товар в корзине
    jacket = auth_page.locator('.inventory_item_name', has_text='Sauce Labs Fleece Jacket')
    expect(jacket).to_be_visible()

    # Удаляем товар
    auth_page.locator('[data-test="remove-sauce-labs-fleece-jacket"]').click()

    # Проверяем, что товара больше нет в корзине
    expect(jacket).not_to_be_visible()


def test_remove_two_items_from_cart(auth_page):
    # Добавляем товары в корзину
    auth_page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    auth_page.locator('[data-test="add-to-cart-test.allthethings()-t-shirt-(red)"]').click()

    # Переходим в корзину
    auth_page.locator('[data-test="shopping-cart-link"]').click()

    # Проверяем что товары в корзине
    backpack = auth_page.locator('.inventory_item_name', has_text='Sauce Labs Backpack')
    tshirt = auth_page.locator('.inventory_item_name', has_text='Test.allTheThings() T-Shirt (Red)')
    expect(backpack).to_be_visible()
    expect(tshirt).to_be_visible()

    # Удаляем товары
    auth_page.locator('[data-test="remove-sauce-labs-backpack"]').click()
    auth_page.locator('[data-test="remove-test.allthethings()-t-shirt-(red)"]').click()

    # Проверяем, что товара больше нет в корзине
    expect(backpack).not_to_be_visible()
    expect(tshirt).not_to_be_visible()


def test_e2e(auth_page):
    # Находим карточки товаров
    jacket_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Fleece Jacket")
    t_shirt_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Bolt T-Shirt")

    # Добавляем товары в корзину
    jacket_card.locator("button").click()
    t_shirt_card.locator("button").click()

    # Переходим в корзину
    auth_page.locator('[data-test="shopping-cart-link"]').click()

    # Проверяем что товары в корзине
    jacket_name = auth_page.locator('.inventory_item_name', has_text='Sauce Labs Fleece Jacket')
    tshirt_name = auth_page.locator('.inventory_item_name', has_text='Sauce Labs Bolt T-Shirt')
    expect(jacket_name).to_be_visible()
    expect(tshirt_name).to_be_visible()

    # Считаем сумму товаров
    prices_text = auth_page.locator(".inventory_item_price").all_text_contents()
    prices = [float(price.replace("$", "")) for price in prices_text]
    expected_total = sum(prices)

    # Заполняем поля Checkout
    auth_page.locator("#checkout").click()
    auth_page.locator("#first-name").fill("Test")
    auth_page.locator("#last-name").fill("Testovich")
    auth_page.locator("#postal-code").fill("111111")
    auth_page.locator("#continue").click()

    # Проверяем Item total
    item_total_text = auth_page.locator(".summary_subtotal_label").inner_text()  # Example: "Item total: $49.99"
    item_total_value = float(item_total_text.split("$")[1])
    assert item_total_value == expected_total, f"Item total {item_total_value} не совпадает с суммой товаров {expected_total}"

    # Tax и Total
    tax_text = auth_page.locator(".summary_tax_label").inner_text()  # Example: "Tax: $4.00"
    tax_value = float(tax_text.split("$")[1])
    total_text = auth_page.locator(".summary_total_label").inner_text()  # Example: "Total: $53.99"
    total_value = float(total_text.split("$")[1])
    assert total_value == round(item_total_value + tax_value, 2), "Total не совпадает с суммой Item total + Tax"

    # Жмем Finish
    auth_page.locator('[data-test="finish"]').click()

    # Проверяем успех оплаты товара
    success_message = auth_page.locator(".complete-header")
    expect(success_message).to_have_text("Thank you for your order!")


def test_checkout_without_items(auth_page):
    # Добавляем товар
    auth_page.locator('[data-test="add-to-cart-sauce-labs-fleece-jacket"]').click()

    # Переход в корзину
    auth_page.locator('[data-test="shopping-cart-link"]').click()

    # Проверяем что товар добавлен в корзину
    jacket = auth_page.locator('.inventory_item_name', has_text='Sauce Labs Fleece Jacket')
    expect(jacket).to_be_visible()

    # Жмем Checout
    auth_page.locator('[data-test="checkout"]').click()

    # Заполянем поле First Name и Last Name
    auth_page.get_by_placeholder("First Name").fill("NewUser")
    auth_page.get_by_placeholder("Last Name").fill("Nrk")

    # Жмем Continue
    auth_page.locator('[data-test="continue"]').click()

    # Провряем ошибку
    error_message = auth_page.locator('[data-test="error"]')
    expect(error_message).to_have_text('Error: Postal Code is required')