from uuid import uuid4
import pytest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_request_request import CreditRequestRequest
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.requests.credit_request_requester import CreditRequestRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api_mid
class TestRequestCredit:
    # Позитивные проверки:
    def test_request_credit_valid(self):
        # Создаём счёт:
        user_name = f"Max{uuid4().hex[:8]}"
        create_user_request = CreateUserRequest(username=user_name, password="Pas!sw0rd", role="ROLE_CREDIT_SECRET")

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)
        assert create_user_request.role == response.role

        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post()

        assert create_account_response.balance == 0
        assert create_account_response.id is not None
        account_id = create_account_response.id
        balance = create_account_response.balance

        # Берём кредит на минимальную сумму
        amount = 5000
        term_months = 12

        credit_request_request = CreditRequestRequest(accountId=account_id, amount=amount, termMonths=term_months)
        credit_response = CreditRequestRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post(credit_request_request)

        # В фактическом ответе из Swagger идентификатор счёта называется "id".
        assert credit_response.id == account_id
        assert credit_response.amount == amount
        assert credit_response.termMonths == term_months
        assert credit_response.balance == balance + amount
        assert credit_response.creditId is not None

    # Негативные проверки: сумма ниже минимума и выше максимума.

    @pytest.mark.parametrize(
        "amount",
        [4999.99, 15000.01]
    )
    def test_request_credit_invalid(self, amount):
        user_name = f"Max{uuid4().hex[:8]}"
        create_user_request = CreateUserRequest(username=user_name, password="Pas!sw0rd", role="ROLE_CREDIT_SECRET")

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)
        assert create_user_request.role == response.role

        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post()

        assert create_account_response.balance == 0
        assert create_account_response.id is not None
        account_id = create_account_response.id

        term_months = 12
        credit_request_request = CreditRequestRequest(accountId=account_id, amount=amount, termMonths=term_months)
        CreditRequestRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_bad()
        ).post(credit_request_request)