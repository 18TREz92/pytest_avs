from uuid import uuid4
import requests
import pytest


@pytest.mark.api_jun
class TestDepositAccount:
    # Позитивные проверки:
    def test_deposit_account_valid(self):
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

        create_account_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )

        assert create_account_response.status_code == 201
        assert create_account_response.json().get("balance") == 0
        account_id = create_account_response.json().get("id")
        start_balance = create_account_response.json().get("balance")
        amount_min = 1000

        deposit_account_response = requests.post(  # Пополнение счёта на минимальную сумму
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": account_id,
                "amount": amount_min
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert deposit_account_response.status_code == 200
        assert deposit_account_response.json().get("balance") == start_balance + amount_min
        new_balance = deposit_account_response.json().get("balance")
        amount_max = 9000

        deposit_account_response = requests.post(  # Пополнение счёта на максимальную сумму
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": account_id,
                "amount": amount_max
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert deposit_account_response.status_code == 200
        assert deposit_account_response.json().get("balance") == new_balance + amount_max

    # Негативные проверки:
    @pytest.mark.parametrize(
        "amount",
        [999.99, 9000.01]
    )
    def test_deposit_account_invalid(self, amount):
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

        create_account_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )

        assert create_account_response.status_code == 201
        assert create_account_response.json().get("balance") == 0
        account_id = create_account_response.json().get("id")
        start_balance = create_account_response.json().get("balance")

        deposit_account_response = requests.post(  # Пополнение счёта на сумму меньше/больше минимальной/максимальной
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": account_id,
                "amount": amount
            },
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )

        assert deposit_account_response.status_code == 400

        # Проверяем, что баланс действительно не изменился:
        account_transactions_response = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{account_id}",
            headers={
                "Authorization": f"Bearer {user_token}",
                "accept": "application/json"
            }
        )
        assert account_transactions_response.status_code == 200
        assert account_transactions_response.json().get("balance") == start_balance
