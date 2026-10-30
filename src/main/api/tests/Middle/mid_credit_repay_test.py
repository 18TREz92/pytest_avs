from uuid import uuid4
import pytest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_request_request import CreditRequestRequest
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.requests.credit_repay_requester import CreditRepayRequester
from src.main.api.requests.credit_request_requester import CreditRequestRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api_mid
class TestRepayCredit:
    # Позитивные проверки:
    def test_repay_credit_valid(self):
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
        credit_id = credit_response.creditId

        # Погашаем кредит единовременно на всю сумму
        repay_amount = 5000
        credit_repay_request = CreditRepayRequest(creditId=credit_id, accountId=account_id, amount=repay_amount)
        credit_repay_response = CreditRepayRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(credit_repay_request)

        assert credit_repay_response.creditId == credit_id
        assert credit_repay_response.amountDeposited == repay_amount

    # Негативные проверки:
    def test_repay_credit_invalid(self):
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
        credit_id = credit_response.creditId

        # Пытаемся погасить половину кредита
        repay_amount = 2500
        credit_repay_request = CreditRepayRequest(creditId=credit_id, accountId=account_id, amount=repay_amount)
        CreditRepayRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_bad_content()
        ).post(credit_repay_request)