import pytest
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest, CreateCreditSecretRequest
from src.main.api.models.credit_request_request import CreditRequestRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest


@pytest.fixture   # Создание пользователя
def create_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(user_request)
    return user_request


@pytest.fixture   # Создание одного счёта
def create_account_response(api_manager, create_user_request):
    return api_manager.user_steps.create_account(create_user_request)


@pytest.fixture   # Создание двух счетов
def create_two_accounts(api_manager, create_user_request):
    first_account = api_manager.user_steps.create_account(create_user_request)
    second_account = api_manager.user_steps.create_account(create_user_request)
    return first_account, second_account


@pytest.fixture   # Создание двух счетов и пополнение одного для дальнейшего перевода
def prepare_accounts_for_transfer(api_manager, create_user_request, create_two_accounts):
    from_account, to_account = create_two_accounts

    first_amount = RandomModelGenerator.generate_deposit_amount_for_transfer()
    second_amount = RandomModelGenerator.generate_deposit_amount_for_transfer()

    for amount in (first_amount, second_amount):
        api_manager.user_steps.deposit_account(create_user_request, DepositAccountRequest(accountId=from_account.id, amount=amount))

    expected_balance = from_account.balance + first_amount + second_amount

    return from_account, to_account, expected_balance


@pytest.fixture   # Создание пользователя для кредита
def create_credit_secret_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateCreditSecretRequest)
    response = api_manager.admin_steps.create_user(user_request)

    assert response.role == user_request.role, 'Роль созданного пользователя для кредита не совпадает с переданной'
    return user_request


@pytest.fixture   # Создание счёта для кредита
def create_credit_account_response(api_manager, create_credit_secret_request):
    return api_manager.user_steps.create_account(create_credit_secret_request)


@pytest.fixture   # Взятие кредита на счёт
def create_credit_response(api_manager, create_credit_secret_request, create_credit_account_response):
    credit_request = CreditRequestRequest(
        accountId=create_credit_account_response.id,
        amount=RandomModelGenerator.generate_credit_amount(),
        termMonths=RandomModelGenerator.generate_credit_term_months()
    )

    return api_manager.user_steps.request_credit(create_credit_secret_request, credit_request)