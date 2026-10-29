import requests
import pytest
from uuid import uuid4


@pytest.mark.api_jun
class TestCreateUser:
    # Позитивные проверки:
    def test_create_user_valid(self):    # Создание нового пользователя
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
        assert create_user_response.json().get("username") == username
        assert create_user_response.json().get("role") == "ROLE_USER"


    # Негативные проверки:
    @pytest.mark.parametrize(       # логин/пароль не по требованиям
        "username, password",
        [
            ("абв", "Pas!sw0rd"),
            ("ab", "Pas!sw0rd"),
            ("abv!", "Pas!sw0rd"),
            ("Maxx1", "Pas!sw0rд"),
            ("Maxx2", "Pas!sw0"),
            ("Maxx3", "pas!sw0rd"),
            ("Maxx4", "PAS!SW0RD"),
            ("Maxx5", "PaSSW0RD"),
            ("Maxx6", "PaS!SWRD"),
        ]
    )
    def test_create_user_invalid(self, username, password):
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

        admin_token = login_admin_response.json().get("token")

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": password,
                "role": "ROLE_USER"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {admin_token}"
            }
        )

        assert create_user_response.status_code == 400
