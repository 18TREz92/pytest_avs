import pytest
from uuid import uuid4
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.login_user_requester import LoginUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api_mid
class TestCreateAccount:
    # Позитивные проверки:
    def test_create_account_valid(self):
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

        # Создание счёта №2
        second_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post()

        assert second_account_response.balance == 0
        assert second_account_response.id is not None
        second_account_id = second_account_response.id
        assert first_account_id != second_account_id

    # Негативные проверки:
    def test_create_account_invalid_by_admin(self):  # Создание счёта в роли админа

        login_user_request = LoginUserRequest(username="admin", password="123456")

        response = LoginUserRequester(
            request_spec=RequestSpecs.unauth_headers(),
            response_spec=ResponseSpecs.request_ok()
        ).post(login_user_request)

        assert response.user.role == "ROLE_ADMIN"

        CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_forbidden()
        ).post()

    def test_create_third_account_invalid(self):  # Создание третьего счёта
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

        # Создание счёта №2
        second_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_created()
        ).post()

        assert second_account_response.balance == 0
        assert second_account_response.id is not None
        second_account_id = second_account_response.id
        assert first_account_id != second_account_id

        # Создание счёта №3
        CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=user_name, password="Pas!sw0rd"),
            response_spec=ResponseSpecs.request_conflict()
        ).post()
