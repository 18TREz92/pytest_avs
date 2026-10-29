from uuid import uuid4
import pytest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.requests.deposit_account_requester import DepositAccountRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api_mid
class TestDepositAccount:
    # Позитивные проверки:
    def test_deposit_account_valid(self):
        user_name = f"Max{uuid4().hex[:8]}"
        create_user_request = CreateUserRequest(username=user_name, password="Pas!sw0rd", role="ROLE_USER")

        CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        # Создаём счёт
        account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post()

        assert account_response.balance == 0
        assert account_response.id is not None
        account_id = account_response.id
        start_balance = account_response.balance

        # Пополнение счёта на минимальную сумму
        min_amount = 1000

        deposit_account_request = DepositAccountRequest(accountId=account_id, amount=min_amount)
        deposit_response = DepositAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(deposit_account_request)

        assert deposit_response.id == account_id
        assert deposit_response.balance == start_balance + min_amount
        new_balance = deposit_response.balance

        # Пополнение счёта на максимальную сумму
        max_amount = 9000

        deposit_account_request = DepositAccountRequest(accountId=account_id, amount=max_amount)
        deposit_response = DepositAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(deposit_account_request)

        assert deposit_response.id == account_id
        assert deposit_response.balance == new_balance + max_amount

    # Негативные проверки:
    @pytest.mark.parametrize(
        "amount",
        [999.99, 9000.01]
    )
    def test_deposit_account_invalid(self, amount):
        user_name = f"Max{uuid4().hex[:8]}"
        create_user_request = CreateUserRequest(username=user_name, password="Pas!sw0rd", role="ROLE_USER")

        CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        # Создаём счёт
        account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post()

        assert account_response.balance == 0
        assert account_response.id is not None
        account_id = account_response.id

        # Пополнение счёта на сумму меньше/больше минимальной/максимальной

        deposit_account_request = DepositAccountRequest(accountId=account_id, amount=amount)
        DepositAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_bad()
        ).post(deposit_account_request)