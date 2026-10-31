import pytest
from uuid import uuid4
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.requests.login_user_requester import LoginUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.requests.create_user_requester import CreateUserRequester


@pytest.mark.api_mid
class TestUserLogin:
    # Позитивные проверки:
    def test_login_admin_valid(self):  # Авторизация в роли админа
        login_user_request = LoginUserRequest(username="admin", password="123456")

        response = LoginUserRequester(
            request_spec=RequestSpecs.unauth_headers(),
            response_spec=ResponseSpecs.request_ok()
        ).post(login_user_request)

        assert login_user_request.username == response.user.username
        assert response.user.role == "ROLE_ADMIN"

    def test_login_user_valid(self):
        # Создание пользователя
        user_name = f"Max{uuid4().hex[:8]}"
        create_user_request = CreateUserRequest(username=user_name, password="Pas!sw0rd", role="ROLE_USER")

        CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        login_user_request = LoginUserRequest(username=user_name, password="Pas!sw0rd")

        # Авторизация в роли пользователя
        response = LoginUserRequester(
            request_spec=RequestSpecs.unauth_headers(),
            response_spec=ResponseSpecs.request_ok()
        ).post(login_user_request)

        assert login_user_request.username == response.user.username
        assert response.user.role == "ROLE_USER"

    # Негативные проверки (админ):
    @pytest.mark.parametrize(  # Некорректный логин/пароль
        "username, password",
        [
            ("admin", "12345"),
            ("abmin", "123456"),
            ("nimda", "654321")
        ]
    )
    def test_login_admin_invalid(self, username, password):
        login_user_request = LoginUserRequest(username=username, password=password)

        LoginUserRequester(
            request_spec=RequestSpecs.unauth_headers(),
            response_spec=ResponseSpecs.request_unauthorized()
        ).post(login_user_request)

    @pytest.mark.parametrize(  # Отсутствует логин/пароль
        "username, password",
        [
            ("", "123456"),
            ("admin", ""),
            ("", "")
        ]
    )
    def test_login_admin_empty(self, username, password):
        login_user_request = LoginUserRequest(username=username, password=password)

        LoginUserRequester(
            request_spec=RequestSpecs.unauth_headers(),
            response_spec=ResponseSpecs.request_bad()
        ).post(login_user_request)
