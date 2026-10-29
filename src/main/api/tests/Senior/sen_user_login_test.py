import pytest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.login_user_request import LoginUserRequest


@pytest.mark.api_sen
class TestUserLogin:
    # Позитивные проверки:
    def test_login_admin_valid(self, api_manager: ApiManager):  # Авторизация в роли админа
        login_user_request = LoginUserRequest(username="admin", password="123456")
        response = api_manager.admin_steps.login_user(login_user_request)

        assert login_user_request.username == response.user.username
        assert response.user.role == "ROLE_ADMIN"

    def test_login_user_valid(self, api_manager: ApiManager, create_user_request: CreateUserRequest):  # Создание пользователя и авторизация под ним
        login_user_request = LoginUserRequest(
            username=create_user_request.username,
            password=create_user_request.password
        )

        response = api_manager.admin_steps.login_user(login_user_request)

        assert response.user.username == login_user_request.username
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
    def test_login_admin_invalid(self, username: str, password: str, api_manager: ApiManager):
        login_user_request = LoginUserRequest(username=username, password=password)
        api_manager.admin_steps.login_invalid_user(login_user_request)

    @pytest.mark.parametrize(  # Отсутствует логин/пароль
        "username, password",
        [
            ("", "123456"),
            ("admin", ""),
            ("", "")
        ]
    )
    def test_login_admin_empty(self, username: str, password: str, api_manager: ApiManager):
        login_user_request = LoginUserRequest(username=username, password=password)
        api_manager.admin_steps.login_empty_user(login_user_request)