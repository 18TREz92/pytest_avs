import pytest
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest, CreateCreditSecretRequest
from src.main.api.models.credit_request_request import CreditRequestRequest


@pytest.fixture  # Создание пользователя
def create_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(user_request)
    return user_request


@pytest.fixture  # Создание одного счёта
def create_account_response(api_manager, create_user_request):
    return api_manager.user_steps.create_account(create_user_request)


@pytest.fixture  # Создание двух счетов
def create_two_accounts(api_manager, create_user_request):
    first_account = api_manager.user_steps.create_account(create_user_request)
    second_account = api_manager.user_steps.create_account(create_user_request)
    return first_account, second_account


@pytest.fixture  # Создание пользователя для кредита
def create_credit_secret_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateCreditSecretRequest)
    response = api_manager.admin_steps.create_user(user_request)

    assert response.role == "ROLE_CREDIT_SECRET"

    return user_request


@pytest.fixture  # Создание счёта для кредита
def create_credit_account_response(api_manager, create_credit_secret_request):
    return api_manager.user_steps.create_account(create_credit_secret_request)


@pytest.fixture  # Взятие кредита на счёт
def create_credit_response(api_manager, create_credit_secret_request, create_credit_account_response):
    # Проверяем подготовленный счёт
    assert create_credit_account_response.balance == 0
    assert create_credit_account_response.id is not None

    amount = 5000
    term_months = 12

    credit_request_request = CreditRequestRequest(accountId=create_credit_account_response.id, amount=amount,
                                                  termMonths=term_months)

    credit_response = api_manager.user_steps.request_credit(create_credit_secret_request, credit_request_request)

    # Проверяем, что кредит подготовлен правильно
    assert credit_response.id == create_credit_account_response.id
    assert credit_response.amount == amount
    assert credit_response.termMonths == term_months
    assert credit_response.balance == create_credit_account_response.balance + amount
    assert credit_response.creditId is not None

    return credit_response
