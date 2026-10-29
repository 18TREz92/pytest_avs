import requests
import pytest
from uuid import uuid4



@pytest.mark.api_jun
class TestUserLogin:
    # Позитивные проверки:
    def test_login_admin_valid(self):    # Авторизация в роли админа
        login_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_admin_response.status_code == 200
        assert login_admin_response.json()["user"]["username"] == "admin"
        assert login_admin_response.json()["user"]["role"] == "ROLE_ADMIN"


    def test_login_user_valid(self):    # Авторизация в роли пользователя
        username = f"Max{uuid4().hex[:8]}"

        login_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_admin_response.status_code == 200
        admin_token = login_admin_response.json().get("token")

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_USER"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {admin_token}"
            }
        )

        assert create_user_response.status_code == 200

        login_user_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": "Pas!sw0rd"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_user_response.status_code == 200
        assert login_user_response.json()["user"]["username"] == username
        assert login_user_response.json()["user"]["role"] == "ROLE_USER"

    # Негативные проверки (админ):
    @pytest.mark.parametrize(    # Некорректный логин/пароль
        "username, password",
        [
            ("admin", "12345"),
            ("abmin", "123456"),
            ("nimda", "654321")
        ]
    )
    def test_login_admin_invalid(self, username, password):
        login_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": password
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_admin_response.status_code == 401

    @pytest.mark.parametrize(    # Отсутствует логин/пароль
        "username, password",
        [
            ("", "123456"),
            ("admin", ""),
            ("", "")
        ]
    )
    def test_login_admin_empty(self, username, password):
        login_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": password
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_admin_response.status_code == 400
