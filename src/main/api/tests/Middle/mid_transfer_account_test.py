import pytest
from uuid import uuid4
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from src.main.api.models.transfer_account_request import TransferAccountRequest
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.requests.deposit_account_requester import DepositAccountRequester
from src.main.api.requests.transfer_account_requester import TransferAccountRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api_mid
class TestTransferAccount:
    # Позитивные проверки:
    def test_transfer_account_valid(self):
        # Создаём 2 счёта
        user_name = f"Max{uuid4().hex[:8]}"
        create_user_request = CreateUserRequest(username=user_name, password="Pas!sw0rd", role="ROLE_USER")

        CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        # Создание счёта №1
        first_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post()

        assert first_account_response.balance == 0
        assert first_account_response.id is not None
        first_account_id = first_account_response.id
        first_balance = first_account_response.balance

        # Создание счёта №2
        second_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post()

        assert second_account_response.balance == 0
        assert second_account_response.id is not None
        second_account_id = second_account_response.id
        assert first_account_id != second_account_id

        # Пополняем счёт № 1
        first_amount = 2000

        deposit_first_account_request = DepositAccountRequest(accountId=first_account_id, amount=first_amount)
        first_deposit_response = DepositAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(deposit_first_account_request)

        assert first_deposit_response.id == first_account_id
        assert first_deposit_response.balance == first_balance + first_amount
        new_first_balance = first_deposit_response.balance

        # Переводим на счёт №2 минимальную сумму
        min_transfer = 500
        transfer_account_request = TransferAccountRequest(fromAccountId=first_account_id, toAccountId=second_account_id,
                                                          amount=min_transfer)
        transfer_response = TransferAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(transfer_account_request)

        assert transfer_response.fromAccountIdBalance == new_first_balance - min_transfer

    # Негативные проверки
    @pytest.mark.parametrize(
        "transfer",
        [499.99, 10000.01]
    )
    def test_transfer_account_invalid(self, transfer):
        # Создаём 2 счёта
        user_name = f"Max{uuid4().hex[:8]}"
        create_user_request = CreateUserRequest(username=user_name, password="Pas!sw0rd", role="ROLE_USER")

        CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        # Создание счёта №1
        first_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post()

        assert first_account_response.balance == 0
        assert first_account_response.id is not None
        first_account_id = first_account_response.id
        first_balance = first_account_response.balance

        # Создание счёта №2
        second_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post()

        assert second_account_response.balance == 0
        assert second_account_response.id is not None
        second_account_id = second_account_response.id
        assert first_account_id != second_account_id

        # Пополняем счёт № 1 на максимально возможную сумму
        amount_max = 9000
        deposit_first_account_request = DepositAccountRequest(accountId=first_account_id, amount=amount_max)
        first_deposit_response = DepositAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(deposit_first_account_request)

        assert first_deposit_response.id == first_account_id
        assert first_deposit_response.balance == first_balance + amount_max
        new_first_balance = first_deposit_response.balance

        # Пополняем счёт №1 ещё раз, чтобы потом можно было проверить верхнюю границу перевода
        amount = 2000
        new_deposit_first_account_request = DepositAccountRequest(accountId=first_account_id, amount=amount)
        new_first_deposit_response = DepositAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(new_deposit_first_account_request)

        assert new_first_deposit_response.id == first_account_id
        assert new_first_deposit_response.balance == new_first_balance + amount

        # Переводим на счёт №2 сумму меньше/больше минимальной/максимальной
        transfer_account_request = TransferAccountRequest(fromAccountId=first_account_id, toAccountId=second_account_id,
                                                          amount=transfer)
        TransferAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_bad()
        ).post(transfer_account_request)