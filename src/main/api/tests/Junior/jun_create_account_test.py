import requests
import pytest
from uuid import uuid4


@pytest.mark.api_jun
class TestCreateAccount:
    # Позитивные проверки:
    def test_create_account_valid(self):
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
        user_token = login_user_response.json().get("token")

        create_first_account_response = requests.post(             # Создание счёта №1
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        assert create_first_account_response.status_code == 201
        assert create_first_account_response.json().get("balance") == 0
        first_account_id = create_first_account_response.json().get("id")
        assert first_account_id is not None


        create_second_account_response = requests.post(           # Создание счёта №2
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )

        assert create_second_account_response.status_code == 201
        assert create_second_account_response.json().get("balance") == 0
        second_account_id = create_second_account_response.json().get("id")
        assert second_account_id is not None
        assert first_account_id != second_account_id

    # Негативные проверки:
    def test_create_account_invalid_by_admin(self):    # Создание счёта в роли админа

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

        create_account_by_admin_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {admin_token}"
            }
        )
        assert create_account_by_admin_response.status_code == 403

    def test_create_third_account_invalid(self):    # Создание третьего счёта
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
        user_token = login_user_response.json().get("token")

        create_first_account_response = requests.post(             # Создание счёта №1
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )

        assert create_first_account_response.status_code == 201
        assert create_first_account_response.json().get("balance") == 0
        first_account_id = create_first_account_response.json().get("id")
        assert first_account_id is not None


        create_second_account_response = requests.post(           # Создание счёта №2
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )

        assert create_second_account_response.status_code == 201
        assert create_second_account_response.json().get("balance") == 0
        second_account_id = create_second_account_response.json().get("id")
        assert second_account_id is not None
        assert first_account_id != second_account_id

        create_third_account_response = requests.post(        # Создание счёта №3
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        assert create_third_account_response.status_code == 409